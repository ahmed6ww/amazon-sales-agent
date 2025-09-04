"""
MVP Scraper Endpoint: returns title, images, A+ content, reviews, Q&A
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, Optional
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

_MARKETPLACE_TLD = {
    "ae": "ae",
    "us": "com",
    "com": "com",
    "uk": "co.uk",
    "de": "de",
    "fr": "fr",
    "it": "it",
    "es": "es",
    "ca": "ca",
    "in": "in",
}


def _build_url(url: Optional[str], asin: Optional[str], marketplace: str) -> str:
    if url and url.strip():
        return url.strip()
    if asin and asin.strip():
        tld = _MARKETPLACE_TLD.get(marketplace.lower(), "com")
        return f"https://www.amazon.{tld}/dp/{asin.strip()}"
    raise HTTPException(status_code=400, detail="Provide either 'url' or 'asin'")


@router.get("/scrape/mvp")
async def scrape_mvp(
    url: Optional[str] = Query(None, description="Amazon product URL to scrape"),
    asin: Optional[str] = Query(None, description="ASIN to build URL from (alternative to url)"),
    marketplace: str = Query("ae", description="Marketplace for ASIN (ae, com, uk, de, fr, it, es, ca, in)")
) -> Dict[str, Any]:
    try:
        full_url = _build_url(url, asin, marketplace)
        if "amazon." not in full_url.lower():
            raise HTTPException(status_code=400, detail="Please provide a valid Amazon URL/ASIN")

        # Call via standalone process to avoid event loop conflicts
        import subprocess, sys, json
        from pathlib import Path
        current_file = Path(__file__)
        app_dir = current_file.parent.parent.parent.parent
        backend_dir = app_dir.parent
        script_path = app_dir / "services" / "amazon" / "standalone_scraper.py"

        proc = subprocess.run([sys.executable, str(script_path), full_url], capture_output=True, text=True, timeout=120, cwd=str(backend_dir))
        if proc.returncode != 0:
            raise HTTPException(status_code=502, detail=f"MVP scraper process failed: {proc.stderr}")
        try:
            payload = json.loads(proc.stdout.strip())
        except Exception as e:
            raise HTTPException(status_code=502, detail=f"Invalid MVP scraper output: {proc.stdout[:200]}")
        if not payload.get("success"):
            raise HTTPException(status_code=502, detail=payload.get("error", "MVP scraping failed"))
        data = payload.get("data", {})

        return {
            "success": True,
            "url": full_url,
            "asin": data.get("asin", ""),
            "data": {
                "title": data.get("title", ""),
                "images": data.get("images", {}),
                "aplus_content": data.get("aplus_content", {}),
                "reviews": data.get("reviews", {}),
                "qa_section": data.get("qa_section", {}),
            },
            "debug_info": data.get("debug_title_info", {})
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("MVP scrape endpoint failed")
        raise HTTPException(status_code=500, detail=str(e)) 