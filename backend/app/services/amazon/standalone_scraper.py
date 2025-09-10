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
        # Ensure URL field is present for downstream consumers
        if isinstance(result, dict) and "data" in result and isinstance(result["data"], dict):
            result["data"].setdefault("url", url)
        print(json.dumps(result))
    except Exception as e:
        print(json.dumps({"success": False, "error": str(e), "data": {}, "url": url}))
        sys.exit(1)

if __name__ == "__main__":
    main() 