from agents import Runner
from typing import Dict, Any, Optional, List, Tuple
from .agent import research_agent
from .helper_methods import scrape_amazon_listing
from .schemas import (
    MarketPosition,
    MarketTier,
)


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

        # 3) Build a single analysis prompt using pre-fetched data + CSV context
        # Keep it compact; the agent should use CSV context only for high-level grounding
        import json
        prompt = (
            "Analyze this pre-fetched Amazon product data for the 5 MVP required sources, and use the CSV keyword context only for grounding (do not perform full keyword scoring here).\n\n"
            f"PRODUCT INFO:\n- URL/ASIN: {asin_or_url}\n- Marketplace: {marketplace}\n- Main Keyword: {main_keyword or 'Not specified'}\n\n"
            f"SCRAPED DATA (structured):\n{scraped_data}\n\n"
            f"CSV CONTEXT (Top 10 each) — Revenue keywords (slim):\n{json.dumps(rev_sample, separators=(',', ':'))}\n\n"
            f"CSV CONTEXT (Top 10 each) — Design keywords (slim):\n{json.dumps(des_sample, separators=(',', ':'))}\n\n"
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
            "- Notes: Any observations about completeness or issues\n"
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

    def _extract_value(self, data: Dict[str, Any], keys: List[str]) -> Optional[str]:
        for k in keys:
            v = data.get(k)
            if isinstance(v, str) and v.strip():
                return v.strip()
        return None

    def _extract_list(self, data: Dict[str, Any], keys: List[str]) -> List[str]:
        for k in keys:
            v = data.get(k)
            if isinstance(v, list):
                return [str(x) for x in v if isinstance(x, (str, int, float))]
        return []

    def _collect_asins(self, rows: List[Dict[str, Any]]) -> set:
        asins = set()
        for row in rows[:10]:  # limit to top 10 contribution
            # Prefer explicit ASIN fields
            for key in ("ASIN", "Asin", "asin", "Parent ASIN", "ParentAsin", "ParentASIN"):
                val = row.get(key)
                if isinstance(val, str) and len(val.strip()) == 10 and val.strip().upper().startswith("B0"):
                    asins.add(val.strip().upper())
            # Fallback: scan values for ASIN-like tokens
            for v in row.values():
                if isinstance(v, str):
                    token = v.strip().upper()
                    if len(token) == 10 and token.startswith("B0"):
                        asins.add(token)
        return asins

    def _classify_market_position(self, scraped_data: Dict[str, Any]) -> MarketPosition:
        # attempt to get price and unit
        price_info = scraped_data.get("price", {}) or {}
        amount = None
        currency = None
        if isinstance(price_info, dict):
            amount = price_info.get("amount")
            currency = price_info.get("currency")
        elif isinstance(price_info, (int, float)):
            amount = float(price_info)
        elif isinstance(price_info, str):
            # parse "$12.99" style strings
            import re
            m = re.search(r"([\$€£])?\s*(\d+(?:\.\d+)?)", price_info)
            if m:
                currency = {"$": "USD", "€": "EUR", "£": "GBP"}.get(m.group(1) or "", None)
                try:
                    amount = float(m.group(2))
                except Exception:
                    amount = None
        # Other possible fields
        if amount is None:
            for k in ("price_str", "price_text", "price_display"):
                val = scraped_data.get(k)
                if isinstance(val, str):
                    import re
                    m = re.search(r"([\$€£])?\s*(\d+(?:\.\d+)?)", val)
                    if m:
                        currency = currency or {"$": "USD", "€": "EUR", "£": "GBP"}.get(m.group(1) or "", None)
                        try:
                            amount = float(m.group(2))
                            break
                        except Exception:
                            continue

        pack_size, unit_name = self._extract_pack_size(scraped_data)
        ppu = None
        if amount and pack_size and pack_size > 0:
            ppu = round(float(amount) / float(pack_size), 2)

        tier = MarketTier.UNKNOWN
        rationale = "Insufficient data"
        if ppu is not None:
            # naive heuristic thresholds; can be tuned per category
            if ppu < 0.75:
                tier = MarketTier.BUDGET
                rationale = f"Low price per {unit_name or 'unit'} ({ppu})"
            elif ppu > 1.50:
                tier = MarketTier.PREMIUM
                rationale = f"High price per {unit_name or 'unit'} ({ppu})"
            else:
                tier = MarketTier.AVERAGE
                rationale = f"Mid-range price per {unit_name or 'unit'} ({ppu})"

        return MarketPosition(
            tier=tier,
            rationale=rationale,
            price=amount,
            currency=currency,
            unit_count=pack_size,
            unit_name=unit_name,
            price_per_unit=ppu,
        )

    def _extract_pack_size(self, scraped_data: Dict[str, Any]) -> Tuple[Optional[float], Optional[str]]:
        # Try pack/quantity/weight cues
        details = scraped_data.get("details", {}) or {}
        specs = scraped_data.get("specifications", {}) or {}
        pack_size = None
        unit = None
        for d in (details, specs):
            for k, v in d.items():
                ks = str(k).lower()
                vs = str(v)
                if any(t in ks for t in ["pack", "count", "quantity", "ounces", "oz", "grams", "g", "pounds", "lb", "kg", "ml", "l"]):
                    # very light parse: extract first number
                    import re
                    m = re.search(r"(\d+(?:\.\d+)?)", vs)
                    if m:
                        try:
                            pack_size = float(m.group(1))
                            # crude unit guess
                            if any(u in ks for u in ["oz", "ounces"]):
                                unit = "oz"
                            elif any(u in ks for u in ["g", "grams"]):
                                unit = "g"
                            elif any(u in ks for u in ["lb", "pounds"]):
                                unit = "lb"
                            elif any(u in ks for u in ["ml"]):
                                unit = "ml"
                            elif any(u in ks for u in ["l "]):
                                unit = "l"
                            else:
                                unit = unit or "unit"
                            return pack_size, unit
                        except Exception:
                            continue
        return None, None

    def _derive_main_keyword_candidates(
        self, title: str, revenue_csv: List[Dict[str, Any]], design_csv: List[Dict[str, Any]]
    ) -> List[str]:
        import re
        candidates: List[str] = []
        tl = (title or "").lower()
        # from title: take noun-ish phrases by trimming brand and attributes crudely
        base = re.sub(r"[^a-z0-9 ]+", " ", tl).strip()
        tokens = [t for t in base.split() if len(t) > 2]
        if tokens:
            candidates.append(" ".join(tokens[:4]).strip())
        # from CSVs: top keyword phrases by Search Volume
        def top_phrases(rows: List[Dict[str, Any]]) -> List[str]:
            def sv(row):
                try:
                    return int(float(row.get("Search Volume", 0) or 0))
                except Exception:
                    return 0
            sorted_rows = sorted(rows[:10], key=sv, reverse=True)
            seen = set()
            phrases = []
            for r in sorted_rows:
                p = str(r.get("Keyword Phrase", "")).strip()
                if p and p.lower() not in seen:
                    seen.add(p.lower())
                    phrases.append(p)
            return phrases[:3]
        candidates.extend(top_phrases(revenue_csv))
        candidates.extend(top_phrases(design_csv))
        # normalize and dedupe
        dedup = []
        seen = set()
        for c in candidates:
            cl = c.lower()
            if cl and cl not in seen:
                seen.add(cl)
                dedup.append(c)
        return dedup[:5]

    def _quality_from_text(self, text: str) -> str:
        if text and len(text) > 20:
            return "good"
        if text and len(text) > 0:
            return "fair"
        return "missing"