from agents import Runner
from typing import Dict, Any, Optional, List
from .agent import research_agent
from .helper_methods import scrape_amazon_listing, select_top_rows, collect_asins, scrape_competitors


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

        # 1) Fetch scraped data via helper
        scraped_result = scrape_amazon_listing(asin_or_url)
        if not scraped_result.get("success"):
            return {
                "success": False,
                "error": f"Scraping failed: {scraped_result.get('error', 'Unknown error')}",
                "scraped_data": scraped_result,
            }

        scraped_data = scraped_result.get("data", {})

        # 1.1) Select top competitors and scrape their price/ratings
        revenue_comp_rows = select_top_rows(revenue_csv or [], mode="revenue", limit=10)
        design_comp_rows = select_top_rows(design_csv or [], mode="design", limit=10)
        revenue_asins = collect_asins(revenue_comp_rows)
        design_asins = collect_asins(design_comp_rows)
        # Fallback: if none found in the top rows, scan entire CSVs for ASINs
        if not revenue_asins and (revenue_csv or []):
            revenue_asins = collect_asins(revenue_csv or [], limit=len(revenue_csv or []))
        if not design_asins and (design_csv or []):
            design_asins = collect_asins(design_csv or [], limit=len(design_csv or []))
        revenue_competitors = scrape_competitors(sorted(list(revenue_asins))[:10])
        design_competitors = scrape_competitors(sorted(list(design_asins))[:10])

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

        rev_sample = _slim_rows(revenue_csv or [], 10)
        des_sample = _slim_rows(design_csv or [], 10)

        # Compute base relevancy scores from CSVs (fraction of tracked ASINs with rank <= 10)
        def _compute_relevancy_scores(rows: List[Dict[str, Any]], competitor_asins: List[str]) -> Dict[str, float]:
            scores: Dict[str, float] = {}
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
                score10 = (ranks_in_top10 / max(1, len(asin_set))) * 10.0
                # Keep max score across revenue/design rows for same keyword
                scores[kw] = max(scores.get(kw, 0.0), score10)
            return scores

        # Build competitor asin lists from the CSV headers
        def _extract_asins_from_rows(rows: List[Dict[str, Any]]) -> List[str]:
            seen = set()
            for row in rows:
                for k in row.keys():
                    if isinstance(k, str) and k.startswith('B0') and len(k) == 10:
                        seen.add(k)
            return list(seen)

        rev_asins_list = _extract_asins_from_rows(revenue_csv or [])
        des_asins_list = _extract_asins_from_rows(design_csv or [])
        base_relevancy = _compute_relevancy_scores(revenue_csv or [], rev_asins_list)
        for k, v in _compute_relevancy_scores(design_csv or [], des_asins_list).items():
            base_relevancy[k] = max(base_relevancy.get(k, 0.0), v)

        # 3) Build a single analysis prompt using pre-fetched data + CSV context
        # Keep it compact; the agent should use CSV context only for high-level grounding
        import json
        prompt = (
            "Analyze this pre-fetched Amazon product data for the 5 MVP required sources, and use the CSV keyword context only for grounding (do not perform full keyword scoring here).\n\n"
            f"PRODUCT INFO:\n- URL/ASIN: {asin_or_url}\n- Marketplace: {marketplace}\n- Main Keyword: {main_keyword or 'Not specified'}\n\n"
            f"SCRAPED DATA (structured):\n{scraped_data}\n\n"
            f"CSV CONTEXT (Top 10 each) — Revenue keywords (slim):\n{json.dumps(rev_sample, separators=(',', ':'))}\n\n"
            f"CSV CONTEXT (Top 10 each) — Design keywords (slim):\n{json.dumps(des_sample, separators=(',', ':'))}\n\n"
            "COMPETITOR CONTEXT (use for market_position tiering):\n"
            f"- Revenue (all {len(rev_comp_slim)}):\n{json.dumps(rev_comp_slim, separators=(',', ':'))}\n"
            f"- Design (all {len(des_comp_slim)}):\n{json.dumps(des_comp_slim, separators=(',', ':'))}\n\n"
            f"BASE RELEVANCY SCORES (0–10 scale; proportion of competitor ASINs ranking top-10 per keyword × 10):\n{json.dumps(dict(sorted(base_relevancy.items(), key=lambda x: x[0]) ) , separators=(',', ':'))}\n\n"
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
            "Also include 'relevancy_scores' mapping using the provided base scores; you may adjust slightly if Amazon search validation suggests stronger/weaker relevance.\n"
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

            return {
                "success": True,
                "final_output": final_output_text or (raw_output if isinstance(raw_output, str) else None),
                # Back-compat aliases expected by endpoints/tests
                "analysis": final_output_text or (raw_output if isinstance(raw_output, str) else ""),
                "agent_used": "ResearchAnalyst",
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
                "base_relevancy_scores": base_relevancy,
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