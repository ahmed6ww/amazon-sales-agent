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
from typing import Dict, Any
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


