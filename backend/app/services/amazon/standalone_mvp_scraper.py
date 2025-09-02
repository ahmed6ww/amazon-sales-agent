#!/usr/bin/env python3
"""
Standalone MVP scraper that runs in its own process to avoid reactor/event loop conflicts.
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
        print(json.dumps({"success": False, "error": "Usage: standalone_mvp_scraper.py <url>"}))
        sys.exit(1)
    url = sys.argv[1]
    try:
        from app.services.amazon.mvp_scraper import scrape_mvp_url
        data = scrape_mvp_url(url)
        if data and not data.get("error"):
            print(json.dumps({"success": True, "data": data, "url": url}))
        else:
            print(json.dumps({"success": False, "error": data.get("error", "Scraping failed"), "data": data or {}, "url": url}))
    except Exception as e:
        print(json.dumps({"success": False, "error": str(e), "data": {}, "url": url}))
        sys.exit(1)

if __name__ == "__main__":
    main() 