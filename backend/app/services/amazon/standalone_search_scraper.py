#!/usr/bin/env python3
"""
Standalone search scraper that runs in its own process to avoid reactor/event loop conflicts.
Implements requirement #14: Top 15 organic results scraping (excluding sponsored).
"""

import sys
import json
import re
from pathlib import Path
from typing import Dict, Any, List

# Add backend dir to path
current = Path(__file__)
backend_dir = current.parent.parent.parent.parent
sys.path.insert(0, str(backend_dir))

def scrape_amazon_search_page(url: str, max_results: int = 15) -> Dict[str, Any]:
    """
    Scrape Amazon search results page.
    
    Args:
        url: Amazon search URL
        max_results: Maximum number of organic results to extract
        
    Returns:
        Dict containing search results
    """
    try:
        import scrapy
        from scrapy.crawler import CrawlerProcess
        from scrapy.http import Request
        
        class AmazonSearchSpider(scrapy.Spider):
            name = "amazon_search_spider"
            scraped: Dict[str, Any] = {}
            
            custom_settings = {
                "ROBOTSTXT_OBEY": False,
                "LOG_LEVEL": "ERROR",
                "RETRY_ENABLED": True,
                "RETRY_TIMES": 3,
                "DOWNLOAD_TIMEOUT": 45,
                "DOWNLOAD_DELAY": 1.0,
                "COOKIES_ENABLED": True,
                "AUTOTHROTTLE_ENABLED": True,
                "AUTOTHROTTLE_START_DELAY": 0.5,
                "AUTOTHROTTLE_MAX_DELAY": 10.0,
                "DEFAULT_REQUEST_HEADERS": {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                    "Accept-Language": "en-US,en;q=0.9",
                    "Upgrade-Insecure-Requests": "1",
                },
                "ITEM_PIPELINES": {},
            }
            
            def __init__(self, url: str, max_results: int = 15, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.start_url = url
                self.max_results = max_results
            
            def start_requests(self):
                yield Request(self.start_url, callback=self.parse)
            
            def parse(self, response):
                html_len = len(response.text)
                has_captcha = "captcha" in response.text.lower()
                
                if response.status in (403, 503) or has_captcha or html_len < 5000:
                    self.scraped = {
                        "success": False,
                        "error": "Blocked or insufficient content",
                        "blocked_reason": f"status:{response.status}, size:{html_len}, captcha:{has_captcha}",
                    }
                    return
                
                # Extract organic search results (exclude sponsored)
                organic_results = self._extract_organic_results(response)
                
                self.scraped = {
                    "success": True,
                    "data": {
                        "url": response.url,
                        "status": response.status,
                        "response_size": html_len,
                        "organic_results": organic_results[:self.max_results],
                        "total_organic_found": len(organic_results)
                    }
                }
            
            def _extract_organic_results(self, response) -> List[Dict[str, Any]]:
                """Extract organic search results, excluding sponsored ads"""
                results = []
                
                # Amazon search results are typically in divs with data-asin attributes
                # Sponsored results are usually marked differently
                product_divs = response.css('div[data-asin]')
                
                for div in product_divs:
                    # Skip sponsored results
                    if self._is_sponsored_result(div):
                        continue
                    
                    result = self._extract_product_data(div)
                    if result:
                        results.append(result)
                
                return results
            
            def _is_sponsored_result(self, div) -> bool:
                """Check if result is sponsored/ad"""
                # Look for sponsored indicators
                sponsored_indicators = [
                    'sponsored',
                    'advertisement',
                    'ad',
                    'promoted'
                ]
                
                div_text = ' '.join(div.css('::text').getall()).lower()
                return any(indicator in div_text for indicator in sponsored_indicators)
            
            def _extract_product_data(self, div) -> Dict[str, Any]:
                """Extract product data from search result div"""
                try:
                    # Extract ASIN
                    asin = div.css('::attr(data-asin)').get()
                    
                    # Extract title
                    title_selectors = [
                        'h2 a span::text',
                        'h2 span::text',
                        '.s-size-mini .s-color-base::text',
                        '[data-cy="title-recipe-title"] span::text'
                    ]
                    
                    title = ""
                    for selector in title_selectors:
                        title = div.css(selector).get()
                        if title:
                            break
                    
                    # Extract price
                    price_selectors = [
                        '.a-price-whole::text',
                        '.a-price .a-offscreen::text',
                        '.a-price-range .a-price .a-offscreen::text'
                    ]
                    
                    price = ""
                    for selector in price_selectors:
                        price = div.css(selector).get()
                        if price:
                            break
                    
                    # Extract rating
                    rating = div.css('.a-icon-alt::text').get()
                    
                    # Extract review count
                    review_count = div.css('.a-size-base::text').get()
                    
                    # Extract image URL
                    img_url = div.css('img::attr(src)').get()
                    
                    # Extract product URL
                    product_url = div.css('h2 a::attr(href)').get()
                    if product_url and not product_url.startswith('http'):
                        from urllib.parse import urljoin
                        product_url = urljoin(response.url, product_url)
                    
                    return {
                        "asin": asin,
                        "title": title.strip() if title else "",
                        "price": price.strip() if price else "",
                        "rating": rating.strip() if rating else "",
                        "review_count": review_count.strip() if review_count else "",
                        "image_url": img_url,
                        "product_url": product_url,
                        "is_organic": True
                    }
                    
                except Exception as e:
                    return None
        
        # Run the scraper
        settings = {
            "ROBOTSTXT_OBEY": False,
            "LOG_LEVEL": "ERROR",
        }
        process = CrawlerProcess(settings)
        crawler = process.create_crawler(AmazonSearchSpider)
        process.crawl(crawler, url=url, max_results=max_results)
        process.start()
        
        # Return scraped data
        return crawler.stats.get_value("scraped", crawler.spider.scraped if hasattr(crawler, "spider") else {})
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Search scraping error: {str(e)}",
            "data": {}
        }


def main():
    if len(sys.argv) < 2:
        print(json.dumps({"success": False, "error": "Usage: standalone_search_scraper.py <search_url> [max_results]"}))
        sys.exit(1)
    
    search_url = sys.argv[1]
    max_results = int(sys.argv[2]) if len(sys.argv) > 2 else 15
    
    try:
        result = scrape_amazon_search_page(search_url, max_results)
        print(json.dumps(result))
    except Exception as e:
        print(json.dumps({"success": False, "error": str(e), "data": {}}))
        sys.exit(1)


if __name__ == "__main__":
    main()


