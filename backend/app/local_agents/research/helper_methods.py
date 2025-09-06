"""
Helper Methods for Research Agent

This module contains the core implementation functions for:
- Amazon product scraping
- Data extraction and processing
"""

import json
import subprocess
import sys
import traceback
from typing import Dict, Any, List, Tuple, Optional
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())  # Load environment variables from .env file


def scrape_amazon_listing(asin_or_url: str) -> Dict[str, Any]:
    """
    Scrape an Amazon product listing using the standalone scraper
    via a separate subprocess to avoid reactor/event loop conflicts.

    Args:
        asin_or_url: Either an ASIN (e.g., B08KT2Z93D) or full Amazon URL

    Returns:
        Dict containing scraped data (title, images, A+ content excerpts, reviews, Q&A, price)
    """
    # Convert ASIN to full URL if needed
    if not asin_or_url.startswith("http"):
        url = f"https://www.amazon.com/dp/{asin_or_url}"
    else:
        url = asin_or_url

    try:
        from pathlib import Path
        current_file = Path(__file__)
        app_dir = current_file.parent.parent.parent
        backend_dir = app_dir.parent
        scraper_script = app_dir / "services" / "amazon" / "standalone_scraper.py"

        result = subprocess.run(
            [sys.executable, str(scraper_script), url],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=str(backend_dir),
        )

        if result.returncode != 0:
            return {
                "success": False,
                "error": f"Scraper process failed: {result.stderr.strip()}",
                "data": {},
                "url": url,
            }

        try:
            container = json.loads(result.stdout.strip())
        except json.JSONDecodeError as e:
            return {
                "success": False,
                "error": f"Failed to parse scraper output: {str(e)}. Output head: {result.stdout[:200]}",
                "data": {},
                "url": url,
            }

        if not isinstance(container, dict):
            return {"success": False, "error": "Invalid scraper response", "data": {}, "url": url}

        if not container.get("success"):
            return {
                "success": False,
                "error": container.get("error", "Unknown scraping error"),
                "data": container.get("data", {}),
                "url": url,
            }

        scraped_data = container.get("data", {}) or {}
        # Accept data if we have at least a title or images; no ASIN required for id-only path
        if not scraped_data:
            return {
                "success": False,
                "error": "No product data extracted",
                "data": {},
                "url": url,
            }

        return {"success": True, "data": scraped_data, "url": url}

    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": "Scraper process timed out (120 seconds)",
            "data": {},
            "url": url,
        }
    except Exception as e:
        error_details = f"Error in subprocess scraping: {str(e)}\nTraceback: {traceback.format_exc()}"
        return {"success": False, "error": error_details, "data": {}, "url": url}


# --- New generic helpers to keep the runner slim ---

def select_top_rows(rows: List[Dict[str, Any]], mode: str, limit: int = 10) -> List[Dict[str, Any]]:
    if not rows:
        return []

    def to_float(v: Any) -> float:
        try:
            if isinstance(v, str):
                vs = v.replace(",", "").strip()
                return float(vs)
            return float(v)
        except Exception:
            return 0.0

    def key_revenue(row: Dict[str, Any]) -> float:
        for k in (
            "Revenue",
            "Monthly Revenue",
            "Gross Revenue",
            "Estimated Revenue",
            "Revenue ($)",
            "Est. Revenue",
        ):
            if k in row and row.get(k) not in (None, ""):
                val = to_float(row.get(k))
                if val:
                    return val
        for k in ("Units Sold", "Sales", "Monthly Sales", "Orders", "Search Volume"):
            if k in row and row.get(k) not in (None, ""):
                val = to_float(row.get(k))
                if val:
                    return val
        return 0.0

    def key_design(row: Dict[str, Any]) -> float:
        for k in ("Cerebro IQ Score", "Relevancy", "Title Density"):
            if k in row and row.get(k) not in (None, ""):
                val = to_float(row.get(k))
                if val:
                    return val
        for k in ("Reviews", "Rating", "Search Volume"):
            if k in row and row.get(k) not in (None, ""):
                val = to_float(row.get(k))
                if val:
                    return val
        return 0.0

    key_fn = key_revenue if mode == "revenue" else key_design
    sorted_rows = sorted(rows, key=key_fn, reverse=True)
    return sorted_rows[:limit]


def collect_asins(rows: List[Dict[str, Any]], *, limit: int = 10) -> set:
    import re
    asin_regex = re.compile(r"B0[A-Z0-9]{8}")
    asins: set = set()
    for row in rows[:limit]:
        for key, val in row.items():
            if isinstance(key, str):
                for m in asin_regex.finditer(key.upper()):
                    asins.add(m.group(0))
            if isinstance(val, str):
                for m in asin_regex.finditer(val.upper()):
                    asins.add(m.group(0))
    return asins


def _parse_rating_info(scraped: Dict[str, Any]) -> Tuple[Optional[float], Optional[int]]:
    import re
    rating_value: Optional[float] = None
    ratings_count: Optional[int] = None

    reviews = (scraped.get("reviews") or {}) if isinstance(scraped, dict) else {}
    highlights = reviews.get("review_highlights") or []
    if highlights:
        m = re.search(r"([0-9.]+)\s+out of 5", str(highlights[0]))
        if m:
            try:
                rating_value = float(m.group(1))
            except Exception:
                rating_value = None
    if len(highlights) > 1 and ratings_count is None:
        m = re.search(r"([0-9,]+)\s+ratings?", str(highlights[1]))
        if m:
            try:
                ratings_count = int(m.group(1).replace(",", ""))
            except Exception:
                ratings_count = None

    if rating_value is None or ratings_count is None:
        kv = (((scraped.get("elements") or {}).get("detailBullets_feature_div") or {}).get("kv") or {})
        for k, v in kv.items():
            if "customer reviews" in str(k).lower():
                if rating_value is None:
                    m2 = re.search(r"([0-9.]+)\s+out of 5", str(v))
                    if m2:
                        try:
                            rating_value = float(m2.group(1))
                        except Exception:
                            pass
                if ratings_count is None:
                    m3 = re.search(r"([0-9,]+)\s+ratings?", str(v))
                    if m3:
                        try:
                            ratings_count = int(m3.group(1).replace(",", ""))
                        except Exception:
                            pass
                break

    return rating_value, ratings_count


def scrape_competitors(asins: List[str], *, max_items: int = 10) -> List[Dict[str, Any]]:
    results: List[Dict[str, Any]] = []
    for asin in asins[:max_items]:
        res = scrape_amazon_listing(asin)
        item: Dict[str, Any] = {"asin": asin, "success": bool(res.get("success"))}
        if res.get("success"):
            data = res.get("data", {}) or {}
            url = data.get("url") or f"https://www.amazon.com/dp/{asin}"
            title = data.get("title") or ((data.get("elements") or {}).get("productTitle") or {}).get("text")
            if isinstance(title, list):
                title = title[0] if title else ""
            price = (data.get("price") or {}) if isinstance(data.get("price"), dict) else {}
            amount = price.get("amount")
            currency = price.get("currency")
            rating_value, ratings_count = _parse_rating_info(data)
            item.update({
                "url": url,
                "title": title,
                "price_amount": amount,
                "price_currency": currency,
                "rating_value": rating_value,
                "ratings_count": ratings_count,
            })
        else:
            item.update({
                "error": res.get("error"),
            })
        results.append(item)
    return results


