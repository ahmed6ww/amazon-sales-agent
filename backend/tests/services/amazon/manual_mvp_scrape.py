#!/usr/bin/env python3
"""
Manual runner to scrape a live Amazon product page and print the result.
No pytest, no mocks. Provide the URL as an argument or paste when prompted.

Usage:
  python backend/tests/manual_mvp_scrape.py <amazon_product_url>
  # or just run without args and paste the URL when prompted
"""

import sys
import json
from pathlib import Path


def _ensure_backend_on_path() -> None:
    """Ensure the repository backend folder is on sys.path for imports."""
    current = Path(__file__).resolve()
    backend_dir = current.parents[1]  # .../backend
    if str(backend_dir) not in sys.path:
        sys.path.insert(0, str(backend_dir))


def main() -> int:
    _ensure_backend_on_path()
    # Defer import until after sys.path fix
    try:
        from app.services.amazon.scraper import scrape_amazon_product  # type: ignore
    except Exception as e:
        print(f"Import error: {e}")
        return 1

    # Get URL from argv or prompt
    url = sys.argv[1] if len(sys.argv) > 1 else None
    if not url:
        try:
            url = input("Enter Amazon product URL: ").strip()
        except KeyboardInterrupt:
            print("\nCancelled.")
            return 1

    if not url:
        print("No URL provided.")
        return 1

    print("Scraping... this may take a few seconds.")
    try:
        result = scrape_amazon_product(url)
    except Exception as e:
        print(json.dumps({"success": False, "error": str(e), "url": url}, indent=2))
        return 1

    # Pretty-print output
    success = bool(result.get("success"))
    data = result.get("data", {})
    print(json.dumps({"success": success, "url": url, "data": data}, indent=2, ensure_ascii=False))

    # Also show a tiny summary for quick glance
    title = data.get("title")
    asin = (data.get("elements") or {}).get("detailBullets_feature_div", {}).get("kv", {}).get("ASIN")
    bullets = (data.get("elements") or {}).get("feature-bullets", {}).get("bullets", [])
    print("\nSummary:")
    print(f"  ASIN:   {asin}")
    print(f"  Title:  {title}")
    print(f"  Images: {((data.get('images') or {}).get('all_images', []))}")
    print(f"  A+:     {((data.get('elements') or {}).get('aplus'))}")
    print(f"  Bullets: {(bullets)}")
    for i, b in enumerate(bullets[:5], 1):
        print(f"    {i}. {b}")

    return 0 if success else 2


if __name__ == "__main__":
    raise SystemExit(main())
