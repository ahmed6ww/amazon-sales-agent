#!/usr/bin/env python3
"""
Amazon scraper: extracts specific element IDs from the product page.

Targets (raw HTML + cleaned text):
- #productTitle
- #productOverview_feature_div
- #feature-bullets
- #productDescription
- #prodDetails
- #detailBullets_feature_div
- #aplus

Usage:
  python backend/app/services/amazon/scraper.py <amazon_product_url>
"""

from __future__ import annotations

import os
import re
import sys
import json
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple

# Add backend directory to Python path for imports when running directly
# This allows: python3 app/services/amazon/scraper.py <url>
if __name__ == "__main__":
    backend_dir = Path(__file__).resolve().parent.parent.parent.parent
    if str(backend_dir) not in sys.path:
        sys.path.insert(0, str(backend_dir))

import scrapy
from scrapy.crawler import CrawlerProcess


TARGET_IDS = [
    "productTitle",
    "productOverview_feature_div",
    "feature-bullets",
    "productDescription",
    "prodDetails",
    "detailBullets_feature_div",
    "aplus",
]


def _clean_text(value: Optional[str]) -> str:
    if not value:
        return ""
    return re.sub(r"\s+", " ", value).strip()


def _parse_dynamic_image_json(attr_value: Optional[str]) -> List[str]:
    """Parse Amazon's data-a-dynamic-image JSON attr into a list of absolute/relative URLs."""
    if not attr_value:
        return []
    try:
        data = json.loads(attr_value)
        # keys are URLs
        return list(data.keys())
    except Exception:
        return []


def _parse_srcset(attr_value: Optional[str]) -> List[str]:
    """Parse an HTML srcset attribute into a list of URLs."""
    if not attr_value:
        return []
    urls: List[str] = []
    try:
        parts = [p.strip() for p in attr_value.split(",")]
        for part in parts:
            if not part:
                continue
            # Format examples: "https://... 1x" or "https://... 320w"
            first = part.split()[0]
            if first:
                urls.append(first)
    except Exception:
        pass
    return urls


def _normalize_image_url(url: Optional[str]) -> str:
    """Normalize image URL for comparison/deduplication: strip querystring and whitespace."""
    if not url:
        return ""
    try:
        # Drop query params/fragments which often encode sizes or cache keys
        base = url.split("?")[0].split("#")[0]
        return base.strip()
    except Exception:
        return url.strip()


def _texts(sel: scrapy.SelectorList) -> List[str]:
    """Extract visible text only (skip script/style/noscript)."""
    raw = sel.css("*:not(script):not(style):not(noscript)::text").getall()
    cleaned = [_clean_text(t) for t in raw]
    # Drop empties and lone punctuation/markers
    cleaned = [t for t in cleaned if t and not re.fullmatch(r"[*:/.()-]+", t)]
    return cleaned


def _kv_from_rows(rows: List[Tuple[str, str]]) -> Dict[str, str]:
    d: Dict[str, str] = {}
    for k, v in rows:
        if k and v:
            d[k] = v
    return d


def _pick_price_text(response: scrapy.http.Response) -> Tuple[str, str, str]:
    """Return (source, text, html) for the first found price, else ('', '', '')."""
    candidates = [
        ("apex_offscreen", "#apex_desktop span.a-price span.a-offscreen"),
        ("core_offscreen", "#corePrice_feature_div span.a-price span.a-offscreen"),
        ("tp_total", "#tp_price_block_total_price_ww span.a-offscreen"),
        ("ourprice", "#priceblock_ourprice"),
        ("dealprice", "#priceblock_dealprice"),
        ("saleprice", "#priceblock_saleprice"),
        ("generic_offscreen", "span.a-price span.a-offscreen"),
    ]
    for name, css in candidates:
        sel = response.css(css)
        txt = _clean_text(" ".join(sel.css("::text").getall()))
        if txt:
            return name, txt, sel.get() or ""
    return "", "", ""


def _parse_price_value(raw: str) -> Tuple[Optional[float], Optional[str]]:
    """Extract numeric amount and currency symbol/code from a raw price string."""
    if not raw:
        return None, None
    # Common currency symbols
    currency_match = re.search(r"([$€£¥₹]|CAD|USD|EUR|GBP|JPY|INR)", raw)
    currency = currency_match.group(1) if currency_match else None
    # Remove non-number separators except dot and comma then normalize
    # Handle formats like $1,234.56 or €1.234,56 or 1 234,56
    cleaned = raw
    cleaned = cleaned.replace("\u00A0", " ")  # nbsp
    # Keep digits, separators, and minus
    cleaned = re.sub(r"[^0-9,.-]", "", cleaned)
    # If both comma and dot exist, assume dot is decimal; remove commas
    if "," in cleaned and "." in cleaned:
        cleaned_num = cleaned.replace(",", "")
    else:
        # If only comma exists, treat comma as decimal
        if "," in cleaned and "." not in cleaned:
            cleaned_num = cleaned.replace(",", ".")
        else:
            cleaned_num = cleaned
    num_match = re.search(r"-?[0-9]+(?:\.[0-9]+)?", cleaned_num)
    try:
        amount = float(num_match.group(0)) if num_match else None
    except Exception:
        amount = None
    return amount, currency


class AmazonScraperSpider(scrapy.Spider):
    name = "amazon_scraper_spider"
    scraped: Dict[str, Any] = {}

    # Custom settings removed - now loaded from anti_blocking.py module
    # This allows centralized configuration and better anti-blocking features
    custom_settings = {}

    def __init__(self, url: str, proxy_url: Optional[str] = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_url = url
        self.proxy_url = proxy_url or os.getenv("SCRAPER_PROXY")

    def start_requests(self):
        meta = {}
        if self.proxy_url:
            meta["proxy"] = self.proxy_url
        yield scrapy.Request(self.start_url, callback=self.parse, meta=meta)

    def parse(self, response: scrapy.http.Response):
        html_len = len(response.text)
        has_captcha = "captcha" in response.text.lower()
        if response.status in (403, 503) or has_captcha or html_len < 5000:
            self.scraped = {
                "success": False,
                "error": "Blocked or insufficient content",
                "blocked_reason": f"status:{response.status}, size:{html_len}, captcha:{has_captcha}",
            }
            return

        include_html = os.getenv("ID_ONLY_INCLUDE_HTML", "0").lower() in {"1", "true", "yes"}

        out: Dict[str, Any] = {
            "url": response.url,
            "status": response.status,
            "response_size": html_len,
            "elements": {},
        }

        # productTitle
        title_sel = response.css("#productTitle")
        title_text = _clean_text(" ".join(title_sel.css("::text").getall()))
        elem: Dict[str, Any] = {"present": bool(title_text), "text": [title_text] if title_text else []}
        if include_html:
            elem["html"] = title_sel.get() or ""
        out["elements"]["productTitle"] = elem

        # productOverview_feature_div -> table rows as key/value
        pov_rows: List[Tuple[str, str]] = []
        for tr in response.css("#productOverview_feature_div table tr"):
            # labels can be in first td or bold span
            label = _clean_text(" ".join(tr.css("td:first-child ::text, th:first-child ::text, .a-text-bold::text").getall()))
            value = _clean_text(" ".join(tr.css("td:nth-child(2) ::text, td:last-child ::text, span.po-break-word::text").getall()))
            if label and value:
                pov_rows.append((label, value))
        # Avoid duplicating the same data as both kv and rows; keep kv only
        elem = {
            "present": bool(pov_rows),
            "kv": _kv_from_rows(pov_rows),
        }
        if include_html:
            elem["html"] = response.css("#productOverview_feature_div").get() or ""
        out["elements"]["productOverview_feature_div"] = elem

        # feature-bullets -> only the bullet items
        fb_sel = response.css("#feature-bullets")
        bullets = [
            _clean_text(t)
            for t in fb_sel.css("ul li .a-list-item::text, ul li span::text, ul li::text").getall()
        ]
        bullets = [
            b for b in bullets
            if b and b.lower() not in {"about this item", "see more product details"}
        ]
        # Dedupe while preserving order
        seen_fb = set()
        bullets = [x for x in bullets if not (x in seen_fb or seen_fb.add(x))]
        elem = {"present": bool(bullets), "bullets": bullets}
        if include_html:
            elem["html"] = fb_sel.get() or ""
        out["elements"]["feature-bullets"] = elem

        # productDescription -> paragraphs only
        pd_sel = response.css("#productDescription")
        paragraphs = [_clean_text(p) for p in pd_sel.css("p::text, p *::text").getall()]
        paragraphs = [p for p in paragraphs if p]
        # Deduplicate while preserving order
        seen = set()
        paragraphs = [x for x in paragraphs if not (x in seen or seen.add(x))]
        elem = {"present": bool(paragraphs), "paragraphs": paragraphs}
        if include_html:
            elem["html"] = pd_sel.get() or ""
        out["elements"]["productDescription"] = elem

        # prodDetails -> restrict to tech spec and detail bullets tables
        tech_rows: List[Tuple[str, str]] = []
        for tr in response.css("#prodDetails table#productDetails_techSpec_section_1 tr"):
            k = _clean_text(" ".join(tr.css("th::text, th *::text").getall()))
            v = _clean_text(" ".join(tr.css("td::text, td *::text").getall()))
            if k and v:
                tech_rows.append((k, v))

        add_rows: List[Tuple[str, str]] = []
        for tr in response.css("#prodDetails table#productDetails_detailBullets_sections1 tr"):
            k = _clean_text(" ".join(tr.css("th::text, th *::text").getall()))
            v = _clean_text(" ".join(tr.css("td::text, td *::text").getall()))
            if k and v:
                add_rows.append((k, v))

        elem = {
            "present": bool(tech_rows or add_rows),
            "tech_specs": _kv_from_rows(tech_rows),
            "additional_info": _kv_from_rows(add_rows),
        }
        if include_html:
            elem["html"] = response.css("#prodDetails").get() or ""
        out["elements"]["prodDetails"] = elem

        # detailBullets_feature_div -> bullets as key/value when possible
        db_sel = response.css("#detailBullets_feature_div")
        db_kv: Dict[str, str] = {}
        for li in db_sel.css("li"):
            label = _clean_text(" ".join(li.css("span.a-text-bold::text").getall())).rstrip(":")
            value = _clean_text(" ".join(li.css("span:not(.a-text-bold)::text, a::text").getall()))
            if label and value:
                db_kv[label] = value
        # Clean noisy Customer Reviews values (strip inline JS fragments and condense)
        for k in list(db_kv.keys()):
            if "customer reviews" in k.lower():
                v = db_kv[k]
                rating_match = re.search(r"([0-9.]+)\s+out of 5 stars", v, re.I)
                count_match = re.search(r"([0-9,]+)\s+ratings?", v, re.I)
                parts: List[str] = []
                if rating_match:
                    parts.append(f"{rating_match.group(1)} out of 5 stars")
                if count_match:
                    parts.append(f"{count_match.group(1)} ratings")
                if parts:
                    db_kv[k] = " ".join(parts)
                else:
                    db_kv[k] = _clean_text(v)[:200]
        elem = {"present": bool(db_kv), "kv": db_kv}
        if include_html:
            elem["html"] = db_sel.get() or ""
        out["elements"]["detailBullets_feature_div"] = elem

        # images -> aggregate hero + all thumbnails (dynamic JSON, hires, srcset, src/data-src)
        def _collect_image_urls(resp: scrapy.http.Response) -> List[str]:
            urls: List[str] = []
            seen: set[str] = set()

            def _upgrade_amazon_image(u: str) -> str:
                """Upgrade Amazon thumbnail to hi-res by stripping sizing tokens like ._SS40_, ._AC_US40_, etc."""
                try:
                    if not u:
                        return u
                    u = _normalize_image_url(u)
                    # Only process Amazon media hosts
                    if not re.search(r"\b(m\.media-amazon\.com|images-na\.ssl-images-amazon\.com)\b", u):
                        return u
                    # Example: https://m.media-amazon.com/images/I/51GKBz7WVYL._AC_US40_.jpg -> .../I/51GKBz7WVYL.jpg
                    m = re.match(r"^(https?://[^\s]+/images/[^/]+/[^./]+)(\._[^.]+_)?\.(jpg|jpeg|png|webp)$", u, re.I)
                    if m:
                        return f"{m.group(1)}.{m.group(3)}"
                    # Fallback: remove any ._TOKEN_ just before extension
                    return re.sub(r"\._[^./]+_(\.[a-zA-Z0-9]+)$", r"\\1", u)
                except Exception:
                    return u

            def _is_product_image(u: str) -> bool:
                """Filter out sprites/icons/overlays and non-product resources."""
                if not u:
                    return False
                lower = u.lower()
                # Exclude graphics folders and overlays/icons
                noisy_markers = [
                    "/images/g/", "/g/", "play-icon", "overlay", "sprite", "icon_", "360_icon", "placeholder",
                ]
                if any(marker in lower for marker in noisy_markers):
                    return False
                # Must be an image extension
                if not re.search(r"\.(jpg|jpeg|png|webp)$", lower):
                    return False
                return True

            def add(u: Optional[str]):
                if not u:
                    return
                abs_u = resp.urljoin(u)
                upgraded = _upgrade_amazon_image(abs_u)
                if not _is_product_image(upgraded):
                    return
                norm = _normalize_image_url(upgraded)
                if norm and norm not in seen:
                    seen.add(norm)
                    urls.append(norm)

            # Hero image variations
            for u in _parse_dynamic_image_json(resp.css("#landingImage::attr(data-a-dynamic-image)").get()):
                add(u)
            add(resp.css("#landingImage::attr(data-old-hires)").get())
            for u in _parse_srcset(resp.css("#landingImage::attr(srcset)").get()):
                add(u)

            # Thumbnails: try dynamic JSON first for each thumb, then hi-res/srcset, then src/data-src
            thumb_selectors = ["#altImages img", "#imageBlockThumbs img"]
            for sel in thumb_selectors:
                # data-a-dynamic-image can contain multiple size URLs for each thumb
                for dyn in resp.css(f"{sel}::attr(data-a-dynamic-image)").getall():
                    for u in _parse_dynamic_image_json(dyn):
                        add(u)
                # data-old-hires on some thumbs
                for u in resp.css(f"{sel}::attr(data-old-hires)").getall():
                    add(u)
                # srcset for thumbs
                for srcset in resp.css(f"{sel}::attr(srcset)").getall():
                    for u in _parse_srcset(srcset):
                        add(u)
                # fallback to src/data-src (may be small, but better than missing)
                for u in resp.css(f"{sel}::attr(data-src), {sel}::attr(src)").getall():
                    add(u)

            return urls

        image_urls = _collect_image_urls(response)
        out["images"] = {
            "present": bool(image_urls),
            "main_image": image_urls[0] if image_urls else "",
            "all_images": image_urls,
            "image_count": len(image_urls),
        }

        # aplus -> only headings and paragraph/list text
        aplus_sel = response.css("#aplus")
        headings = _texts(aplus_sel.css("h1, h2, h3, h4"))
        paras = _texts(aplus_sel.css("p"))
        list_items = _texts(aplus_sel.css("li"))
        # Dedupe while preserving order
        def _uniq(seq: List[str]) -> List[str]:
            seen: set[str] = set()
            return [x for x in seq if not (x in seen or seen.add(x))]
        headings = _uniq(headings)
        paras = _uniq(paras)
        list_items = _uniq(list_items)
        # Limit sizes to avoid bloat
        max_items = int(os.getenv("ID_ONLY_MAX_APLUS_ITEMS", "50"))
        elem = {
            "present": bool(headings or paras or list_items),
            "headings": headings[:max_items],
            "paragraphs": paras[:max_items],
            "list_items": list_items[:max_items],
        }
        if include_html:
            elem["html"] = aplus_sel.get() or ""
        out["elements"]["aplus"] = elem

        # Also expose a tiny title helper for quick sanity checks
        out["title"] = title_text

        # reviews -> sample review texts + rating/highlights
        review_texts = [
            _clean_text(t)
            for t in response.css("#cm-cr-dp-review-list .review-text-content span::text").getall()[:5]
            if _clean_text(t)
        ]
        rating_text = _clean_text(
            response.css("#acrPopover::attr(title), [data-hook='rating-out-of-text']::text").get()
        )
        review_count = _clean_text(response.css("#acrCustomerReviewText::text").get())
        out["reviews"] = {
            "present": bool(review_texts or rating_text or review_count),
            "sample_reviews": review_texts,
            "review_highlights": [rating_text, review_count],
        }

        # Q&A section -> inline questions if present (no follow-up request to keep it minimal)
        qa_pairs: List[Dict[str, str]] = []
        qa_block = response.css("#ask-btf_feature_div")
        if qa_block:
            qs = [
                _clean_text(q)
                for q in qa_block.css("span::text, a::text").getall()[:5]
                if _clean_text(q)
            ]
            qa_pairs = [{"q": q, "a": ""} for q in qs]
        out["qa_section"] = {
            "present": bool(qa_pairs),
            "qa_pairs": qa_pairs,
            "questions": [q.get("q") for q in qa_pairs],
        }

        # Extract price (lean): amount, currency, raw, source
        src, raw_price, price_html = _pick_price_text(response)
        amount, currency = _parse_price_value(raw_price)
        price_obj: Dict[str, Any] = {
            "present": bool(raw_price),
            "raw": raw_price if raw_price else "",
            "amount": amount,
            "currency": currency,
            "source": src,
        }
        if include_html:
            price_obj["html"] = price_html
        out["price"] = price_obj

        self.scraped = {"success": True, "data": out}


def scrape_amazon_product(url: str, proxy_url: Optional[str] = None) -> Dict[str, Any]:
    """
    Synchronous scraper with anti-blocking features based on Scrapy documentation
    
    Anti-Blocking Features (from Scrapy docs):
    1. User Agent Rotation - RandomUserAgentMiddleware (priority 400)
    2. Smart Retry Logic - EnhancedRetryMiddleware (priority 550)
       - Retries on HTTP 500, 503 (Amazon blocking)
       - Retries on non-text responses (CAPTCHA detection)
       - Retries on CAPTCHA keywords in HTML
    3. Cookie Handling - CookiesMiddleware (priority 700)
    4. Random Delays - RandomDelayMiddleware (2-5s)
    5. Proper Referers - RefererMiddleware (priority 450)
    6. Auto Throttle - Adaptive rate limiting
    
    References:
    - RetryMiddleware: https://docs.scrapy.org/topics/downloader-middleware.html#retry-middleware
    - UserAgentMiddleware: https://docs.scrapy.org/topics/downloader-middleware.html#useragentmiddleware
    - CookiesMiddleware: https://docs.scrapy.org/topics/downloader-middleware.html#cookiesmiddleware
    """
    import sys
    import traceback
    
    # Load anti-blocking settings with fallback
    settings = None
    anti_blocking_enabled = False
    
    try:
        from app.services.amazon.anti_blocking import get_anti_blocking_settings
        settings = get_anti_blocking_settings()
        # Override log level from environment
        settings["LOG_LEVEL"] = os.getenv("SCRAPER_LOG_LEVEL", "INFO")
        anti_blocking_enabled = True
        print(f"✅ Anti-blocking enabled: User Agent Rotation, Smart Retry, Random Delays (2-5s)", file=sys.stderr)
    except ImportError as e:
        print(f"⚠️ Anti-blocking module not found: {e}", file=sys.stderr)
        print(f"⚠️ Using minimal fallback settings (may get blocked)", file=sys.stderr)
        settings = {
            "ROBOTSTXT_OBEY": False,
            "LOG_LEVEL": os.getenv("SCRAPER_LOG_LEVEL", "INFO"),
            "DOWNLOAD_DELAY": 3.0,
            "COOKIES_ENABLED": True,
            "RETRY_ENABLED": True,
            "RETRY_TIMES": 3,
            "RETRY_HTTP_CODES": [500, 502, 503, 504, 429, 403],
        }
    except Exception as e:
        print(f"❌ Error loading anti-blocking: {e}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        settings = {
            "ROBOTSTXT_OBEY": False,
            "LOG_LEVEL": os.getenv("SCRAPER_LOG_LEVEL", "INFO"),
            "DOWNLOAD_DELAY": 3.0,
            "COOKIES_ENABLED": True,
        }
    
    # Run scraper with error handling
    try:
        process = CrawlerProcess(settings)
        crawler = process.create_crawler(AmazonScraperSpider)
        process.crawl(crawler, url=url, proxy_url=proxy_url)
        process.start()
        
        # Get result from spider
        result = crawler.stats.get_value("scraped", 
                                         crawler.spider.scraped if hasattr(crawler, "spider") else {})
        
        if not result:
            result = {"success": False, "error": "No result returned from spider", "data": {}}
        
        # Add debugging info
        if anti_blocking_enabled and result.get("success"):
            result["anti_blocking_used"] = True
            print(f"✅ Scraping successful with anti-blocking features", file=sys.stderr)
        elif not result.get("success"):
            error = result.get("error", "Unknown error")
            print(f"❌ Scraping failed: {error}", file=sys.stderr)
            if "Blocked" in error or "captcha" in error.lower():
                print(f"💡 Tip: Consider using a proxy or ScraperAPI for better success rates", file=sys.stderr)
        
        return result
        
    except Exception as e:
        error_msg = f"Scraper crashed: {str(e)}"
        print(f"❌ {error_msg}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        
        return {
            "success": False,
            "error": error_msg,
            "error_type": type(e).__name__,
            "data": {}
        }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"success": False, "error": "Usage: scraper.py <url>"}))
        sys.exit(1)
    url = sys.argv[1]
    try:
        result = scrape_amazon_product(url)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        sys.exit(0 if result.get("success") else 2)
    except Exception as e:
        print(json.dumps({"success": False, "error": str(e), "url": url}))
        sys.exit(1)
