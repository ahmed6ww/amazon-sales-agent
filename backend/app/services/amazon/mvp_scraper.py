import os
import re
import sys
import json
import random
from typing import Optional, Dict, Any

import scrapy
from scrapy.crawler import CrawlerProcess


def _clean_text(value: Optional[str]) -> str:
    if not value:
        return ""
    return re.sub(r"\s+", " ", value).strip()


def _parse_dynamic_image_json(attr_value: Optional[str]) -> list[str]:
    if not attr_value:
        return []
    try:
        data = json.loads(attr_value)
        return list(data.keys())
    except Exception:
        return []


class AmazonMVPSpider(scrapy.Spider):
    name = "amazon_mvp_spider"
    scraped: Dict[str, Any] = {}

    custom_settings = {
        "ROBOTSTXT_OBEY": False,
        "LOG_LEVEL": "ERROR",
        "RETRY_ENABLED": True,
        "RETRY_TIMES": int(os.getenv("SCRAPER_RETRY_TIMES", "3")),
        "RETRY_HTTP_CODES": [429, 500, 502, 503, 504, 522, 524, 408],
        "DOWNLOAD_TIMEOUT": int(os.getenv("SCRAPER_TIMEOUT", "45")),
        "DOWNLOAD_DELAY": float(os.getenv("SCRAPER_DOWNLOAD_DELAY", "1.0")),
        "COOKIES_ENABLED": True,
        "AUTOTHROTTLE_ENABLED": True,
        "AUTOTHROTTLE_START_DELAY": 0.5,
        "AUTOTHROTTLE_MAX_DELAY": 10.0,
        "DEFAULT_REQUEST_HEADERS": {
            "User-Agent": os.getenv(
                "SCRAPER_USER_AGENT",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Language": os.getenv("SCRAPER_ACCEPT_LANGUAGE", "en-US,en;q=0.9,ar;q=0.8"),
            "Upgrade-Insecure-Requests": "1",
        },
        "ITEM_PIPELINES": {},
    }

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
        if response.status in (403, 503) or has_captcha or html_len < 20000:
            self.scraped = {
                "error": "Amazon blocking detected - unable to extract product data",
                "blocked_reason": f"status:{response.status}, size:{html_len}, captcha:{has_captcha}",
            }
            return

        # ASIN
        asin = None
        m = re.search(r"/dp/([A-Z0-9]{10})", response.url)
        if m:
            asin = m.group(1)
        asin = asin or response.css("#ASIN::attr(value)").get()
        self.scraped["asin"] = asin or ""

        # Title - robust selectors and fallbacks
        title = response.css(
            "#productTitle::text, span#productTitle::text, h1#title span::text, h1.a-size-large::text, "
            "span.a-size-large.product-title-word-break::text, .product-title-word-break::text, "
            "#titleSection h1 span::text, #centerCol #title span::text"
        ).get()
        
        # Clean and check if title is meaningful (not just whitespace)
        title = _clean_text(title) if title else ""
        
        if not title:
            title = response.css("meta[property='og:title']::attr(content), meta[name='title']::attr(content)").get()
            title = _clean_text(title) if title else ""
        
        if not title:
            # Try JSON-LD
            ld = response.css("script[type='application/ld+json']::text").get()
            if ld:
                try:
                    data = json.loads(ld)
                    if isinstance(data, dict):
                        title = data.get("name") or data.get("headline")
                    elif isinstance(data, list) and data:
                        # find first with name
                        for item in data:
                            if isinstance(item, dict) and (item.get("name") or item.get("headline")):
                                title = item.get("name") or item.get("headline")
                                break
                except Exception:
                    pass
        
        if not title:
            # Try page title and extract product name
            page_title = response.css("title::text").get()
            if page_title:
                # Amazon titles often: "Product Name : Amazon.ae"
                # Extract everything before " : Amazon.ae"
                if " : Amazon.ae" in page_title:
                    title = page_title.split(" : Amazon.ae")[0].strip()
                elif " : " in page_title:
                    parts = page_title.split(" : ")
                    # Take the first part (product name)
                    title = parts[0].strip()
                elif " - " in page_title and "amazon" in page_title.lower():
                    parts = page_title.split(" - ")
                    # Take the first part (before Amazon)
                    title = parts[0].strip()
                else:
                    title = page_title.strip()
        if not title:
            # Fallback to meta description prefix
            desc = response.css("meta[name='description']::attr(content)").get()
            if desc:
                # Often in form "Amazon.ae: Apple EarPods (USB-C) ..."
                parts = re.split(r"\s[:\-|]\s", desc, maxsplit=1)
                title = parts[-1] if parts else desc
        
        # Always add debug info to see what's happening
        debug_info = {
            "raw_title": title or "NONE_FOUND",
            "cleaned_title": _clean_text(title) or "EMPTY_AFTER_CLEAN",
            "page_title": response.css("title::text").get() or "NO_PAGE_TITLE",
            "meta_title": response.css("meta[property='og:title']::attr(content)").get() or "NO_META_TITLE",
            "response_size": len(response.text),
            "status": response.status
        }
        self.scraped["debug_title_info"] = debug_info
        
        # Final cleaning - ensure we have just the product name
        final_title = _clean_text(title)
        if final_title and " : Amazon.ae" in final_title:
            final_title = final_title.split(" : Amazon.ae")[0].strip()
        
        self.scraped["title"] = final_title

        # Images
        # Primary landing image dynamic JSON
        dynamic_json = response.css("#landingImage::attr(data-a-dynamic-image)").get()
        image_urls = _parse_dynamic_image_json(dynamic_json)
        if not image_urls:
            image_urls = [u for u in response.css("#altImages img::attr(src)").getall() if u]
        # Ensure absolute URLs and deduplicate
        image_urls = list(dict.fromkeys([response.urljoin(u) for u in image_urls]))
        self.scraped["images"] = {
            "main_image": image_urls[0] if image_urls else "",
            "all_images": image_urls,
            "image_count": len(image_urls),
        }

        # A+ content (EBC) with optional follow-up request when iframe/URL present
        aplus_sections: list[dict] = []
        aplus_root = response.css("#aplus, #aplus_feature_div, #aplus_v2")
        if aplus_root:
            headings = [
                _clean_text(h) for h in aplus_root.css("h2::text, h3::text").getall() if _clean_text(h)
            ]
            paragraphs = [
                _clean_text(p) for p in aplus_root.css("p::text, li::text, div.a-spacing-small::text, .aplus-module-content span::text").getall() if _clean_text(p)
            ]
            if headings or paragraphs:
                aplus_sections.append({"heading": headings[0] if headings else "Product Description", "paragraphs": paragraphs[:20]})
        else:
            # Detect possible A+ iframe or module URL
            iframe_url = response.css("iframe[src*='aplus']::attr(src)").get()
            if iframe_url:
                iframe_url = response.urljoin(iframe_url)
                yield scrapy.Request(iframe_url, callback=self.parse_aplus, meta=response.meta)
        self.scraped["aplus_content"] = {"sections": aplus_sections, "total_length": sum(len(s.get("paragraphs", [])) for s in aplus_sections)}

        # Reviews sample
        review_texts = [
            _clean_text(t)
            for t in response.css("#cm-cr-dp-review-list .review-text-content span::text").getall()[:5]
            if _clean_text(t)
        ]
        rating_text = _clean_text(
            response.css("#acrPopover::attr(title), [data-hook='rating-out-of-text']::text").get()
        )
        review_count = _clean_text(response.css("#acrCustomerReviewText::text").get())
        self.scraped["reviews"] = {
            "sample_reviews": review_texts,
            "review_highlights": [rating_text, review_count],
        }

        # Q&A (try inline, then follow link if available)
        qa_pairs = []
        qa_block = response.css("#ask-btf_feature_div")
        if qa_block:
            qs = [
                _clean_text(q)
                for q in qa_block.css("span::text, a::text").getall()[:5]
                if _clean_text(q)
            ]
            qa_pairs = [{"q": q, "a": ""} for q in qs]
        else:
            qa_link = response.css("a[href*='ask/questions']::attr(href)").get()
            if qa_link:
                qa_link = response.urljoin(qa_link)
                yield scrapy.Request(qa_link, callback=self.parse_qa, meta=response.meta)
        self.scraped["qa_section"] = {"qa_pairs": qa_pairs, "questions": [q.get("q") for q in qa_pairs]}

    def parse_aplus(self, response: scrapy.http.Response):
        paragraphs = [
            _clean_text(p)
            for p in response.css("p::text, li::text, div::text, span::text").getall()
            if _clean_text(p)
        ][:50]
        if paragraphs:
            current = self.scraped.get("aplus_content", {"sections": []})
            current["sections"].append({"heading": "A+ Content", "paragraphs": paragraphs})
            self.scraped["aplus_content"] = current

    def parse_qa(self, response: scrapy.http.Response):
        questions = [
            _clean_text(q)
            for q in response.css(".askTeaserQuestions .a-link-normal::text, .a-declarative .a-link-normal::text").getall()
            if _clean_text(q)
        ][:10]
        if questions:
            current = self.scraped.get("qa_section", {"qa_pairs": [], "questions": []})
            current["questions"] = list(dict.fromkeys(current.get("questions", []) + questions))
            current["qa_pairs"] = current.get("qa_pairs", []) + [{"q": q, "a": ""} for q in questions]
            self.scraped["qa_section"] = current


def scrape_mvp_url(url: str, proxy_url: Optional[str] = None) -> Dict[str, Any]:
    """
    Synchronous scraper for MVP fields (to be used in a subprocess).
    Returns a dict with MVP keys or error fields when blocked.
    """
    settings = {
        "USER_AGENT": os.getenv(
            "SCRAPER_USER_AGENT",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        ),
        "ROBOTSTXT_OBEY": False,
        "LOG_LEVEL": "ERROR",
    }
    process = CrawlerProcess(settings)
    crawler = process.create_crawler(AmazonMVPSpider)
    process.crawl(crawler, url=url, proxy_url=proxy_url)
    process.start()
    return crawler.stats.get_value("scraped", crawler.spider.scraped if hasattr(crawler, "spider") else {}) 