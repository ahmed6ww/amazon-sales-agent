from agents import Runner
from typing import Dict, Any, Optional, List
from .agent import research_agent
from .helper_methods import (
    scrape_amazon_listing, 
    select_top_rows, 
    collect_asins, 
    scrape_competitors,
    filter_keywords_by_original_content,  # NEW: Filter keywords by original content
    deduplicate_keywords_with_scores      # NEW: Deduplicate keywords with scores
)
from app.core.config import settings
from app.local_agents.scoring.subagents.intent_agent import USER_PROMPT_TEMPLATE
from app.services.keyword_processing.root_extraction import get_priority_roots_for_search
from app.services.keyword_processing.batch_processor import (
    optimize_keyword_processing_for_agents
)
import logging

logger = logging.getLogger(__name__)


class ResearchRunner:
    """
    Minimal runner: scrape via helper, then analyze with the agent once.
    """

    def run_research(
        self,
        asin_or_url: str,
        marketplace: str = "US",
        main_keyword: Optional[str] = None,
        revenue_csv: Optional[List[Dict[str, Any]]] = None,
        design_csv: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        Scrape the Amazon listing and analyze the 5 MVP sources using the agent.

        Args:
            asin_or_url: Amazon ASIN or full product URL
            marketplace: Target marketplace code
            main_keyword: Optional main keyword context

        Returns:
            Dict with success flag, analysis text, and raw scraped data
        """

        # 1) Fetch scraped data via helper with marketplace support
        scraped_result = scrape_amazon_listing(asin_or_url, marketplace)
        if not scraped_result.get("success"):
            return {
                "success": False,
                "error": f"Scraping failed: {scraped_result.get('error', 'Unknown error')}",
                "scraped_data": scraped_result,
            }

        scraped_data = scraped_result.get("data", {})

        # 1.1) Select top competitors and scrape their price/ratings
        top_n = getattr(settings, "RESEARCH_CSV_TOP_N", 200)  # Increased to analyze more keywords
        # Heuristic floors (configurable via settings if present)
        literal_floor = int(getattr(settings, "RESEARCH_LITERAL_FLOOR", 8))  # when literal match is strong
        competitor_floor = int(getattr(settings, "RESEARCH_COMPETITOR_FLOOR", 7))  # when many relevant designs
        revenue_comp_rows = select_top_rows(revenue_csv or [], mode="revenue", limit=top_n)
        design_comp_rows = select_top_rows(design_csv or [], mode="design", limit=top_n)
        revenue_asins = collect_asins(revenue_comp_rows, limit=top_n)
        design_asins = collect_asins(design_comp_rows, limit=top_n)
        # Fallback: if none found in the top rows, scan entire CSVs for ASINs
        if not revenue_asins and (revenue_csv or []):
            revenue_asins = collect_asins(revenue_csv or [], limit=top_n)
        if not design_asins and (design_csv or []):
            design_asins = collect_asins(design_csv or [], limit=top_n)
        revenue_competitors = scrape_competitors(sorted(list(revenue_asins))[:top_n])
        design_competitors = scrape_competitors(sorted(list(design_asins))[:top_n])

        # Slim competitor context for the agent (keep prompt compact)
        def _slim_comps(comps: List[Dict[str, Any]], limit: Optional[int] = None) -> List[Dict[str, Any]]:
            keep = ("asin", "price_amount", "price_currency", "rating_value", "ratings_count")
            slim: List[Dict[str, Any]] = []
            iterable = comps if limit is None else comps[:limit]
            for c in iterable:
                if isinstance(c, dict):
                    slim.append({k: c.get(k) for k in keep if k in c})
            return slim

        rev_comp_slim = _slim_comps(revenue_competitors)
        des_comp_slim = _slim_comps(design_competitors)
        
        # 2) Slim and include top-10 rows from each CSV (if provided) to guide analysis
        def _slim_rows(rows: List[Dict[str, Any]], limit: int = 10) -> List[Dict[str, Any]]:
            if not rows:
                return []
            # take first N (assumes upstream selection may already sort); avoid token blow-up by keeping key fields
            keep = {
                "Keyword Phrase",
                "Search Volume",
                "Relevancy",
                "Title Density",
                "CPR",
                "Cerebro IQ Score",
            }
            slimmed: List[Dict[str, Any]] = []
            for row in rows[:limit]:
                slim: Dict[str, Any] = {}
                for k, v in row.items():
                    if k in keep:
                        slim[k] = v
                if slim:
                    slimmed.append(slim)
            return slimmed

        rev_sample = _slim_rows(revenue_csv or [], top_n)
        des_sample = _slim_rows(design_csv or [], top_n)

        # Compute base relevancy scores from CSVs (fraction of tracked ASINs with rank <= 10)
        def _compute_relevancy_scores(rows: List[Dict[str, Any]], competitor_asins: List[str]) -> Dict[str, int]:
            """
            Calculate relevancy score (0-10) based on keyword ranking in top 10 for competitor ASINs.
            
            HOW IT WORKS:
            1. Check each keyword's rank for each competitor ASIN
            2. Count how many competitors rank in top 10 for this keyword
            3. Formula: (top10_count / total_asins) * 20, capped at 10
            
            EXAMPLE:
            - Keyword: "freeze dried strawberries"
            - 5 competitor ASINs analyzed
            - Ranks in top 10 for: 3 ASINs
            - Score: (3/5) * 20 = 12 → capped at 10/10
            
            WHY *20? To scale 50% performance to ~10/10. If keyword ranks top 10 for half
            the competitors, it gets high score since that's strong performance.
            """
            scores: Dict[str, int] = {}
            if not rows or not competitor_asins:
                return scores
            asin_set = [a for a in competitor_asins if isinstance(a, str) and len(a) == 10 and a.startswith('B0')]
            if not asin_set:
                return scores
            for row in rows:
                kw = str(row.get('Keyword Phrase', '')).strip()
                if not kw:
                    continue
                ranks_in_top10 = 0
                for asin in asin_set:
                    try:
                        rank_val = row.get(asin)
                        if rank_val is None:
                            continue
                        rank_num = int(float(rank_val))
                        if rank_num > 0 and rank_num <= 10:
                            ranks_in_top10 += 1
                    except Exception:
                        continue
                # Score formula: Scale to 0-10 range (doubled to reward 50%+ performance)
                score10 = min(10, int(round((ranks_in_top10 / max(1, len(asin_set))) * 20.0)))
                # Keep max score across revenue/design rows for same keyword
                scores[kw] = max(scores.get(kw, 0), score10)
            return scores

        # Simple literal-meaning relevance check using keyword tokens vs product title
        def _literal_relevance(keyword: str, product_title: str) -> float:
            kw = (keyword or "").lower().strip()
            title = (product_title or "").lower()
            if not kw or not title:
                return 0.0
            # token presence ratio (very simple heuristic, robust to ordering)
            import re
            kw_tokens = [t for t in re.split(r"[^a-z0-9]+", kw) if t]
            # normalize extremely short tokens and handle simple plurals (ball -> balls)
            norm_tokens = []
            for t in kw_tokens:
                if len(t) == 1:
                    continue
                norm_tokens.append(t)
                if t.endswith('s') and len(t) > 2:
                    norm_tokens.append(t[:-1])
                elif not t.endswith('s') and len(t) > 2:
                    norm_tokens.append(t + 's')
            if norm_tokens:
                kw_tokens = list(dict.fromkeys(norm_tokens))  # de-duplicate preserving order
            if not kw_tokens:
                return 0.0
            hits = sum(1 for t in kw_tokens if t in title)
            return hits / len(kw_tokens)

        # Determine competitor "relevant design" by keyword presence in competitor title
        def _count_relevant_designs(keyword: str, competitor_items: List[Dict[str, Any]]) -> int:
            k = (keyword or "").lower().strip()
            if not k:
                return 0
            import re
            kw_tokens = [t for t in re.split(r"[^a-z0-9]+", k) if t]
            count = 0
            for it in competitor_items:
                title = str(it.get("title") or "").lower()
                if not title:
                    continue
                hits = sum(1 for t in kw_tokens if t and t in title)
                if hits >= max(1, len(kw_tokens) - 1):  # loose match: allow one token miss
                    count += 1
            return count

        # Build competitor asin lists from the CSV headers
        def _extract_asins_from_rows(rows: List[Dict[str, Any]]) -> List[str]:
            seen = set()
            for row in rows:
                for k in row.keys():
                    if isinstance(k, str) and k.startswith('B0') and len(k) == 10:
                        seen.add(k)
            # keep stable order for all ASINs
            out = [a for a in list(seen)]
            return out

        rev_asins_list = _extract_asins_from_rows(revenue_csv or [])
        des_asins_list = _extract_asins_from_rows(design_csv or [])
        
        # Extract all keywords from both CSV files for optimized processing
        revenue_keywords = []
        for row in (revenue_csv or []):
            kw = row.get('Keyword Phrase', '')
            if kw and isinstance(kw, str):
                revenue_keywords.append(kw.strip())
        
        design_keywords = []
        for row in (design_csv or []):
            kw = row.get('Keyword Phrase', '')
            if kw and isinstance(kw, str):
                design_keywords.append(kw.strip())
        
        # Use optimized batch processing to handle large datasets efficiently
        batch_size = getattr(settings, "KEYWORD_BATCH_SIZE", 50)
        keyword_root_analysis = optimize_keyword_processing_for_agents(
            revenue_keywords=revenue_keywords,
            design_keywords=design_keywords,
            batch_size=batch_size
        )
        
        # Extract results for compatibility
        priority_roots = keyword_root_analysis.get('priority_roots', [])
        unique_keywords = revenue_keywords + design_keywords
        unique_keywords = list(dict.fromkeys([kw for kw in unique_keywords if kw.strip()]))
        
        # ==================================================================================
        # STEP 1: DEDUPLICATE KEYWORDS
        # ==================================================================================
        # PURPOSE: Remove duplicate keywords that appear in both revenue.csv and design.csv
        # WHY: When keywords appear in multiple CSVs, we need to:
        #      1. Keep only one instance (avoid showing "strawberry powder" twice)
        #      2. Preserve the HIGHEST relevancy score across all sources
        # EXAMPLE: If "freeze dried" appears in both CSVs with scores 7 and 9, keep score 9
        # OUTPUT: Deduplicated keyword list + unified relevancy scores
        # ==================================================================================
        
        logger.info("")
        logger.info("="*80)
        logger.info("🔧 [STEP 1: KEYWORD DEDUPLICATION]")
        logger.info("="*80)
        logger.info("📋 What: Remove duplicate keywords across revenue.csv and design.csv")
        logger.info("🎯 Why: Prevent duplicate keywords, keep highest relevancy score")
        logger.info("💡 How: Case-insensitive matching, score aggregation")
        logger.info("="*80)
        
        # First, compute traditional relevancy scores before deduplication
        pre_dedup_relevancy = _compute_relevancy_scores(revenue_csv or [], rev_asins_list)
        for k, v in _compute_relevancy_scores(design_csv or [], des_asins_list).items():
            pre_dedup_relevancy[k] = max(pre_dedup_relevancy.get(k, 0.0), v)
        
        # Apply deduplication: Remove duplicate keywords and keep highest scores
        unique_keywords, base_relevancy, dedup_stats = deduplicate_keywords_with_scores(
            keywords=unique_keywords,
            relevancy_scores=pre_dedup_relevancy
        )
        
        logger.info("")
        logger.info(f"✅ [DEDUPLICATION RESULTS]")
        logger.info(f"   📊 Input: {dedup_stats['original_count']} total keywords")
        logger.info(f"   🎯 Output: {dedup_stats['unique_count']} unique keywords")
        logger.info(f"   🗑️  Removed: {dedup_stats['duplicates_removed']} duplicates")
        logger.info(f"   📝 Note: {dedup_stats['duplicates_found_count']} keywords had multiple scores (kept highest)")
        logger.info("="*80)
        logger.info("")
        
        # ==================================================================================
        # STEP 2: CONTENT FILTER **DISABLED FOR SEO OPTIMIZATION**
        # ==================================================================================
        # PURPOSE: Was filtering to only keywords in current listing
        # WHY DISABLED: SEO optimization NEEDS new high-volume keywords not in current listing
        # IMPACT: Now passing ALL deduplicated keywords (6944) to categorization & SEO
        # BENEFIT: Can now add "beauty blender" (71K vol) even if not in current title
        # ==================================================================================
        
        logger.info("")
        logger.info("="*80)
        logger.info("🔧 [STEP 2: CONTENT FILTER - DISABLED]")
        logger.info("="*80)
        logger.info("📋 What: Content filter DISABLED for SEO optimization")
        logger.info("🎯 Why: Allow NEW high-volume keywords not in current listing")
        logger.info(f"💡 Impact: All {len(unique_keywords)} deduplicated keywords will be analyzed")
        logger.info("🚀 Benefit: Can now optimize with keywords like 'beauty blender' (71K vol)")
        logger.info("="*80)
        logger.info("")
        
        # SKIP content filtering - use ALL deduplicated keywords
        # This allows SEO agent to suggest new high-volume keywords
        filtered_base_relevancy = base_relevancy
        
        logger.info(f"✅ [KEYWORD PASSTHROUGH]")
        logger.info(f"   📊 Total keywords: {len(unique_keywords)}")
        logger.info(f"   🎯 All keywords will be categorized and scored")
        logger.info(f"   💡 SEO agent can now suggest NEW high-volume keywords")
        logger.info("="*80)
        logger.info("")
        
        # Log sample of mapped keywords with scores
        sample_keywords = list(filtered_base_relevancy.items())[:10]
        logger.info(f"📊 [RELEVANCY SAMPLE] First 10 keywords with scores:")
        for kw, score in sample_keywords:
            logger.info(f"   - '{kw}': {score}/10")
        
        base_relevancy = filtered_base_relevancy
        
        logger.info(f"📊 [FINAL STATS] Processing {len(unique_keywords)} deduplicated and filtered keywords")
        
        # ==================================================================================
        # END OF FILTERING AND DEDUPLICATION
        # ==================================================================================

        # Filter keywords by relevancy score (dynamic threshold based on dataset size)
        # More keywords = stricter threshold to focus on highest quality
        total_keywords = len(base_relevancy)
        if total_keywords > 200:
            min_relevancy_threshold = 4  # Very strict for large datasets (200+)
        elif total_keywords > 100:
            min_relevancy_threshold = 3  # Moderate for medium datasets (100-200)
        else:
            min_relevancy_threshold = 2  # Default for small datasets (≤100)

        logger.info(f"📊 Dynamic relevancy threshold: {min_relevancy_threshold} (based on {total_keywords} total keywords)")
        
        high_relevancy_keywords = []
        high_relevancy_scores = {}
        
        for keyword, score in base_relevancy.items():
            if score >= min_relevancy_threshold:
                high_relevancy_keywords.append(keyword)
                high_relevancy_scores[keyword] = score  # ✅ PRESERVE ORIGINAL SCORES

        logger.info(f"Filtered keywords by relevancy >= {min_relevancy_threshold}: {len(base_relevancy)} -> {len(high_relevancy_keywords)}")

        # Use filtered keywords with PRESERVED scores for agents
        full_base_relevancy = base_relevancy.copy()
        base_relevancy = high_relevancy_scores  # ✅ KEEPS ORIGINAL SCORES (3, 4, etc.)

        # Perform AI-powered root extraction for richer analysis context (non-blocking if fails)
        ai_keyword_root_analysis: Dict[str, Any] = {}
        try:
            from app.local_agents.keyword.subagents.root_extraction_agent import extract_roots_ai
            # Build minimal product context for the AI subagent
            _title_text = str(((scraped_data.get("elements") or {}).get("productTitle") or {}).get("text") or "")
            if isinstance(_title_text, list):
                _title_text = _title_text[0] if _title_text else ""
            _brand = (((scraped_data.get("elements") or {}).get("productOverview_feature_div") or {}).get("kv") or {}).get("Brand", "")
            product_context = {"title": _title_text, "category": scraped_data.get("category", ""), "brand": _brand}
            ai_keyword_root_analysis = extract_roots_ai(unique_keywords, product_context)
        except Exception:
            # Non-fatal: continue without AI root analysis
            ai_keyword_root_analysis = {}

        # Compute adjusted relevancy per rules:
        # 1) Literal meaning first. If literal score is high (>=0.6), keep base score.
        # 2) If literal is low (<0.6) but many relevant designs are ranked, incline to relevancy by boosting.
        #    We approximate "relevant designs ranked" by competitor title matches count among scraped competitors.
        #    Final confirmation via SERP is not implemented yet.
        product_title = str(((scraped_data.get("elements") or {}).get("productTitle") or {}).get("text") or "")
        if isinstance(product_title, list):
            product_title = product_title[0] if product_title else ""
        adjusted_relevancy: Dict[str, int] = {}
        # Ensure we consider the provided main_keyword too, even if absent from CSV-derived base map
        keywords_for_adjust = dict(base_relevancy)
        if main_keyword and main_keyword not in keywords_for_adjust:
            keywords_for_adjust[main_keyword] = 0

        for kw, base_score in keywords_for_adjust.items():
            lit = _literal_relevance(kw, product_title)
            if lit >= 0.6:
                # Literal meaning first: ensure a minimum score when literal is strong
                adjusted = max(base_score, literal_floor)
            else:
                # competitor relevant designs across both sets we scraped
                rel_rev = _count_relevant_designs(kw, revenue_competitors)
                rel_des = _count_relevant_designs(kw, design_competitors)
                rel_total = rel_rev + rel_des
                # if we have strong competitor relevance (>=7 across both lists), incline upward
                if rel_total >= 7:
                    # Preserve prior +2 boost with cap 10, while also enforcing a minimum floor
                    adjusted = max(base_score, min(10, max(base_score + 2, competitor_floor)))
                else:
                    adjusted = base_score
            adjusted_relevancy[kw] = int(max(0, min(10, int(round(adjusted)))))

        # 3) Build a single analysis prompt using pre-fetched data + CSV context
        # Keep it compact; the agent should use CSV context only for high-level grounding
        import json
        prompt = (
            "Analyze this pre-fetched Amazon product data for the 5 MVP required sources, and use the CSV keyword context only for grounding. Do not compute or mention keyword relevancy here.\n\n"
            f"PRODUCT INFO:\n- URL/ASIN: {asin_or_url}\n- Marketplace: {marketplace}\n- Main Keyword: {main_keyword or 'Not specified'}\n\n"
            f"SCRAPED DATA (structured):\n{scraped_data}\n\n"
            f"CSV CONTEXT (Top 10 each) — Revenue keywords (slim):\n{json.dumps(rev_sample, separators=(',', ':'))}\n\n"
            f"CSV CONTEXT (Top 10 each) — Design keywords (slim):\n{json.dumps(des_sample, separators=(',', ':'))}\n\n"
            "COMPETITOR CONTEXT (use for market_position tiering):\n"
            f"- Revenue (all {len(rev_comp_slim)}):\n{json.dumps(rev_comp_slim, separators=(',', ':'))}\n"
            f"- Design (all {len(des_comp_slim)}):\n{json.dumps(des_comp_slim, separators=(',', ':'))}\n\n"
            "Required sources to analyze (focus on extraction quality only):\n"
            "1. TITLE - Product title text and quality assessment\n"
            "2. IMAGES - Image URLs, count, and quality\n"
            "3. A+ CONTENT - Enhanced brand content sections and marketing material\n"
            "4. REVIEWS - Customer review samples and sentiment highlights\n"
            "5. Q&A SECTION - Question and answer pairs\n\n"
            "For each source, provide:\n"
            "- Extracted: Yes/No\n"
            "- Content: The actual data found\n"
            "- Quality: Assessment (Excellent/Good/Fair/Poor/Missing)\n"
            "- Notes: Any observations about completeness or issues\n\n"
            "For market_position: compare the product's price (or price_per_unit when unit_count/unit_name can be derived) against competitor medians to assign tier ('budget'|'premium'); provide a brief rationale.\n"
            "Do not include any keyword relevancy scoring in your response; the system will attach it.\n"
        )

        # 4) Single agent call
        try:
            result = Runner.run_sync(research_agent, prompt)
            raw_output = getattr(result, "final_output", None)

            structured: Dict[str, Any] = {}
            final_output_text: Optional[str] = None

            # If SDK returned a Pydantic model (ResearchStructuredOutput)
            if raw_output is not None and hasattr(raw_output, "model_dump"):
                try:
                    structured = raw_output.model_dump()
                    # keep a compact string preview for UI/testing
                    final_output_text = "Research structured output generated"
                except Exception:
                    structured = {}

            # Or if it’s already a dict
            if not structured and isinstance(raw_output, dict):
                structured = raw_output
                final_output_text = "Research structured output generated"

            # Otherwise, raw_output may be a narrative string; try to extract JSON as last resort
            if not structured and isinstance(raw_output, str):
                final_output_text = raw_output
                structured = self._extract_agent_json(raw_output)

            # Back-compat: create a tiny text summary for quick checks in older UIs/tests
            if structured and not final_output_text:
                try:
                    ps = (structured.get("data_quality", {}) or {}).get("per_source", {}) or {}
                    parts = []
                    for key in ["title", "images", "aplus", "reviews", "qa"]:
                        if key in ps:
                            parts.append(f"{key.upper()}: {ps.get(key)}")
                    if parts:
                        final_output_text = " | ".join(parts)
                except Exception:
                    pass


            # Build dynamic user prompt for IntentScoringSubagent (no execution here)
            import json as _json
            USER_PROMPT_TEMPLATE.format(
                scraped_product=_json.dumps(scraped_data or {}, separators=(",", ":")),
                base_relevancy_scores=_json.dumps(base_relevancy or {}, separators=(",", ":")),
            )

            return {
                "success": True,
                "final_output": final_output_text or (raw_output if isinstance(raw_output, str) else None),
                # Back-compat aliases expected by endpoints/tests
                "analysis": final_output_text or (raw_output if isinstance(raw_output, str) else ""),
                "agent_used": "ResearchAnalyst",
                "main_keyword": main_keyword,
                "scraped_product": scraped_data,
                "structured_data": structured or {},
                "csv_context_counts": {
                    "revenue_sample": len(rev_sample),
                    "design_sample": len(des_sample),
                },
                "competitor_scrapes": {
                    "revenue": revenue_competitors,
                    "design": design_competitors,
                },
                "base_relevancy_scores": base_relevancy,  # Optimized set for agents
                "full_base_relevancy_scores": full_base_relevancy,  # Complete analysis
                "adjusted_relevancy_scores": adjusted_relevancy,
                "keyword_root_analysis": keyword_root_analysis,
                "priority_roots": priority_roots,
                "total_unique_keywords": len(unique_keywords),
                "ai_keyword_root_analysis": ai_keyword_root_analysis,
                "agent_optimization": {
                    "timeout_prevention": True,
                    "agent_keywords_count": len(base_relevancy),
                    "full_keywords_count": len(unique_keywords),
                    "optimization_ratio": f"{len(base_relevancy)}/{len(unique_keywords)}"
                },
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "final_output": None,
                "scraped_product": scraped_data,
                "csv_context_counts": {
                    "revenue_sample": len(rev_sample),
                    "design_sample": len(des_sample),
                },
                "competitor_scrapes": {
                    "revenue": revenue_competitors,
                    "design": design_competitors,
                },
                "base_relevancy_scores": base_relevancy,  # Optimized set for agents
                "full_base_relevancy_scores": full_base_relevancy,  # Complete analysis  
                "adjusted_relevancy_scores": adjusted_relevancy,
                "keyword_root_analysis": keyword_root_analysis,
                "priority_roots": priority_roots,
                "total_unique_keywords": len(unique_keywords),
                "ai_keyword_root_analysis": ai_keyword_root_analysis,
                "agent_optimization": {
                    "timeout_prevention": True,
                    "agent_keywords_count": len(base_relevancy),
                    "full_keywords_count": len(unique_keywords),
                    "optimization_ratio": f"{len(base_relevancy)}/{len(unique_keywords)}"
                },
            }

    # --- internal: helpers ---
    # Note: all deterministic structuring and scoring has been moved to the agent.

    def _extract_agent_json(self, final_output: Optional[str]) -> Dict[str, Any]:
        """Best-effort extraction of a JSON object from the agent's final_output."""
        if not final_output or not isinstance(final_output, str):
            return {}
        import json, re
        text = final_output.strip()
        # Try to find the last JSON object in the text
        matches = re.findall(r"\{[\s\S]*\}", text)
        for snippet in reversed(matches):
            try:
                obj = json.loads(snippet)
                if isinstance(obj, dict):
                    return obj
            except Exception:
                continue
        return {}
