#!/usr/bin/env python3
"""
Standalone scraper that runs in its own process to avoid reactor/event loop conflicts.
"""

import sys
import json
from pathlib import Path

# Add backend dir to path
current = Path(__file__)
backend_dir = current.parent.parent.parent.parent
sys.path.insert(0, str(backend_dir))

def main():
    if len(sys.argv) < 2:
        print(json.dumps({"success": False, "error": "Usage: standalone_scraper.py <url>"}))
        sys.exit(1)
    url = sys.argv[1]
    try:
        # Use the scraper as the unified backend
        from app.services.amazon.scraper import scrape_amazon_product
        result = scrape_amazon_product(url)
        
        # Normalize result structure for backwards compatibility
        # Playwright/CloudScraper returns flat structure, old Scrapy wrapped in "data"
        if isinstance(result, dict) and result.get("success"):
            # If result has "elements" but not wrapped in "data", wrap it
            if "elements" in result and "data" not in result:
                # Create wrapped structure
                data_content = {
                    "url": result.get("url", url),
                    "status": result.get("status", 200),
                    "elements": result.get("elements", {}),
                }
                # Add optional fields if present
                if "title" in result:
                    data_content["title"] = result["title"]
                if "price" in result:
                    data_content["price"] = result["price"]
                if "images" in result:
                    data_content["images"] = result["images"]
                if "brand" in result:
                    data_content["brand"] = result["brand"]
                
                result = {
                    "success": True,
                    "data": data_content,
                    "scraping_method": result.get("scraping_method", result.get("method", "unknown"))
                }
            elif "data" in result and isinstance(result["data"], dict):
                # Already wrapped, just ensure URL is set
                result["data"].setdefault("url", url)
        
        print(json.dumps(result))
        # Exit with error code if scraping failed
        if not result.get("success"):
            sys.exit(1)
    except ImportError as e:
        import traceback
        error_details = f"Import error: {str(e)}\n{traceback.format_exc()}"
        print(json.dumps({"success": False, "error": error_details, "data": {}, "url": url}), file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        import traceback
        error_details = f"{str(e)}\n{traceback.format_exc()}"
        print(json.dumps({"success": False, "error": error_details, "data": {}, "url": url}), file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main() 