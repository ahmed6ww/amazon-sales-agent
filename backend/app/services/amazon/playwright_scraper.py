"""
Playwright-based Amazon scraper (real browser rendering)
Copied from working RSS scraper approach for better anti-blocking

This uses the same proven strategy as your RSS/journal scrapers:
- Real browser (Chromium/Firefox) with multiple configs
- CloudScraper fallback (Cloudflare bypass)
- Stealth JavaScript injection
- Proper browser fingerprints
- Random delays between attempts
- Content validation before returning
"""

import os
import re
import json
import asyncio
import random
from typing import Optional, Dict, Any, List, Tuple
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout
import logging

logger = logging.getLogger(__name__)

try:
    import cloudscraper
    CLOUDSCRAPER_AVAILABLE = True
except ImportError:
    CLOUDSCRAPER_AVAILABLE = False
    logger.warning("CloudScraper not available - install with: pip install cloudscraper")


def _clean_text(value: Optional[str]) -> str:
    """Clean whitespace from text"""
    if not value:
        return ""
    return re.sub(r"\s+", " ", value).strip()


def _parse_price_value(raw: str) -> Tuple[Optional[float], Optional[str]]:
    """Extract numeric amount and currency from price string"""
    if not raw:
        return None, None
    
    # Common currency symbols
    currency_match = re.search(r"([$€£¥₹]|CAD|USD|EUR|GBP|JPY|INR)", raw)
    currency = currency_match.group(1) if currency_match else None
    
    # Remove non-number separators except dot and comma
    cleaned = raw.replace("\u00A0", " ")
    cleaned = re.sub(r"[^0-9,.-]", "", cleaned)
    
    # Normalize comma/dot as decimal separator
    if "," in cleaned and "." in cleaned:
        cleaned_num = cleaned.replace(",", "")
    elif "," in cleaned and "." not in cleaned:
        cleaned_num = cleaned.replace(",", ".")
    else:
        cleaned_num = cleaned
    
    num_match = re.search(r"-?[0-9]+(?:\.[0-9]+)?", cleaned_num)
    try:
        amount = float(num_match.group(0)) if num_match else None
    except Exception:
        amount = None
    
    return amount, currency


async def scrape_amazon_with_playwright(
    url: str,
    headless: bool = True,
    timeout_ms: int = 30000
) -> Dict[str, Any]:
    """
    Scrape Amazon product using Playwright (real browser)
    
    This is the same approach as your working RSS scraper:
    - Uses real browser (Chromium/Firefox)
    - Multiple configurations per browser
    - Stealth mode to avoid detection
    - Random delays between attempts
    - Content validation before returning
    
    Args:
        url: Amazon product URL
        headless: Run browser in headless mode (default True, can use "new" for Chrome stealth)
        timeout_ms: Page load timeout in milliseconds (default 30000 - 30s per attempt)
    
    Returns:
        Dict with scraped data or error
    """
    
    # Read environment variable for headless mode (same as RSS scraper)
    headless_env = os.getenv("PLAYWRIGHT_HEADLESS", "true").lower()
    if headless_env in {"false", "0", "no"}:
        launch_headless: bool | str = False
    elif headless_env == "new":
        launch_headless = "new"  # Chrome's advanced stealth mode
    else:
        launch_headless = True
    
    # Override with parameter if explicitly provided
    if not headless:
        launch_headless = False
    
    # Read timeout from environment (same as RSS scraper)
    timeout_ms = int(os.getenv("PLAYWRIGHT_TIMEOUT_MS", str(timeout_ms)))
    
    logger.info(f"🎭 Starting Playwright scraper for: {url}")
    logger.info(f"   Headless mode: {launch_headless}, Timeout: {timeout_ms}ms")
    
    # Define multiple browser configurations (same as RSS scraper)
    browser_configs = [
        # Config 1: Chromium with new headless mode (best stealth)
        {"type": "chromium", "headless": "new", "viewport": {"width": 1920, "height": 1080}},
        # Config 2: Chromium standard headless
        {"type": "chromium", "headless": True, "viewport": {"width": 1366, "height": 768}},
        # Config 3: Firefox fallback
        {"type": "firefox", "headless": True, "viewport": {"width": 1920, "height": 1080}},
    ]
    
    async with async_playwright() as p:
        # Try different browser configurations (similar to RSS scraper's multiple CloudScraper configs)
        for i, config in enumerate(browser_configs, 1):
            browser_type_name = config["type"]
            browser_type = p.chromium if browser_type_name == "chromium" else p.firefox
            try:
                logger.info(f"   Config {i}/3: Trying {browser_type_name} browser...")
                
                # Random delay between attempts (same as RSS scraper)
                if i > 1:
                    delay = random.uniform(2, 5)
                    logger.info(f"   Waiting {delay:.1f}s before next attempt...")
                    await asyncio.sleep(delay)
                
                # Chrome arguments for stealth (copied from RSS scraper)
                import platform
                chrome_args = [
                    "--disable-blink-features=AutomationControlled",
                    "--disable-features=VizDisplayCompositor",
                ]
                
                # Only add --no-sandbox on Linux (causes issues on Windows)
                if platform.system().lower() == "linux":
                    chrome_args.append("--no-sandbox")
                
                # Handle Chrome's "new" headless mode (best stealth)
                config_headless = config.get("headless", True)
                if config_headless == "new" and browser_type_name == "chromium":
                    chrome_args.append("--headless=new")
                    browser = await browser_type.launch(
                        headless=True,  # Standard headless for Playwright
                        args=chrome_args,
                    )
                else:
                    browser = await browser_type.launch(
                        headless=config_headless if isinstance(config_headless, bool) else True,
                        args=chrome_args,
                    )
                
                # Create context with config-specific viewport
                viewport = config.get("viewport", {"width": 1920, "height": 1080})
                context = await browser.new_context(
                    viewport=viewport,
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                )
                
                page = await context.new_page()
                
                # Add stealth techniques (copied from RSS scraper)
                await page.add_init_script("""
                    Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                    Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
                    Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
                """)
                
                # Navigate to Amazon
                logger.info(f"   Loading page...")
                await page.goto(url, wait_until="networkidle", timeout=timeout_ms)
                
                # Wait for content to load
                await page.wait_for_timeout(3000)
                
                # Check if we got blocked (CAPTCHA page)
                page_content = await page.content()
                if "captcha" in page_content.lower():
                    logger.warning(f"   ❌ Config {i}: Got CAPTCHA page")
                    await browser.close()
                    continue
                
                logger.info(f"   ✅ Page loaded successfully")
                
                # Extract product data
                result = await _extract_amazon_data(page, url)
                
                await browser.close()
                
                # Content validation (same as RSS scraper - check if we got real content)
                if result.get("success"):
                    # Validate we have meaningful data
                    title = result.get("elements", {}).get("productTitle", {}).get("text", [])
                    bullets = result.get("elements", {}).get("feature-bullets", {}).get("text", [])
                    
                    if title and len(title[0]) > 10:  # Title must be substantial
                        logger.info(f"✅ Config {i}: Extraction successful! Product: {title[0][:50]}...")
                        result["method"] = f"playwright_{browser_type_name}_config{i}"
                        result["config_used"] = i
                        return result
                    else:
                        logger.warning(f"   ⚠️ Config {i}: Title too short or missing - page may be blocked")
                        continue
                else:
                    logger.warning(f"   ⚠️ Config {i}: Extraction failed: {result.get('error')}")
                    continue
                
            except PlaywrightTimeout:
                logger.warning(f"   ⏱️ {browser_type.name} timeout after {timeout_ms}ms")
                try:
                    await browser.close()
                except:
                    pass
                continue
            
            except Exception as e:
                logger.warning(f"   ❌ {browser_type.name} failed: {e}")
                try:
                    await browser.close()
                except:
                    pass
                continue
        
        # All Playwright browsers failed - try CloudScraper as final fallback
        logger.warning("⚠️ All Playwright configs failed, trying CloudScraper fallback...")
        
        if CLOUDSCRAPER_AVAILABLE:
            cloudscraper_result = await _scrape_with_cloudscraper(url, timeout_ms)
            if cloudscraper_result.get("success"):
                return cloudscraper_result
        
        # Everything failed
        logger.error("❌ All scraping methods failed (Playwright + CloudScraper)")
        return {
            "success": False,
            "error": "All scraping methods failed (3 Playwright configs + CloudScraper)",
            "method": "all_failed"
        }


async def _scrape_with_cloudscraper(url: str, timeout: int) -> Dict[str, Any]:
    """
    CloudScraper fallback (same as RSS scraper strategy)
    Tries multiple browser configurations for better success rate
    """
    if not CLOUDSCRAPER_AVAILABLE:
        return {"success": False, "error": "CloudScraper not installed"}
    
    logger.info(f"🌩️  Trying CloudScraper fallback...")
    
    # Multiple CloudScraper configs (same as RSS scraper)
    scraper_configs = [
        # Config 1: Chrome on Windows
        {
            "browser": {"browser": "chrome", "platform": "windows", "desktop": True},
            "interpreter": "nodejs",
            "delay": 8,
        },
        # Config 2: Firefox on Windows
        {
            "browser": {"browser": "firefox", "platform": "windows", "desktop": True},
            "interpreter": "nodejs",
            "delay": 10,
        },
        # Config 3: Chrome on macOS
        {
            "browser": {"browser": "chrome", "platform": "darwin", "desktop": True},
            "interpreter": "nodejs",
            "delay": 12,
        },
    ]
    
    for i, config in enumerate(scraper_configs, 1):
        try:
            logger.info(f"   CloudScraper config {i}/3...")
            
            # Random delay between attempts
            if i > 1:
                delay = random.uniform(2, 5)
                logger.info(f"   Waiting {delay:.1f}s...")
                await asyncio.sleep(delay)
            
            scraper = cloudscraper.create_scraper(**config)
            
            # Add headers (same as RSS scraper)
            scraper.headers.update({
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate, br",
                "DNT": "1",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-User": "?1",
                "Cache-Control": "max-age=0",
            })
            
            # Run in executor to avoid blocking (since cloudscraper is sync)
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: scraper.get(url, timeout=timeout // 1000)
            )
            
            if response.status_code == 200:
                logger.info(f"   ✅ CloudScraper config {i} succeeded!")
                
                # Parse with BeautifulSoup
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Extract data from BeautifulSoup (simplified extraction)
                result = _extract_from_beautifulsoup(soup, url)
                if result.get("success"):
                    result["method"] = f"cloudscraper_config{i}"
                    result["config_used"] = i
                    return result
            else:
                logger.warning(f"   ⚠️ CloudScraper config {i} failed: HTTP {response.status_code}")
                continue
        
        except Exception as e:
            logger.warning(f"   ❌ CloudScraper config {i} error: {e}")
            continue
    
    return {"success": False, "error": "All CloudScraper configs failed"}


def _extract_from_beautifulsoup(soup, url: str) -> Dict[str, Any]:
    """Extract Amazon data from BeautifulSoup (simplified version for CloudScraper)"""
    try:
        # Check for title
        title_elem = soup.select_one("#productTitle")
        if not title_elem:
            return {"success": False, "error": "Product title not found"}
        
        title_text = _clean_text(title_elem.get_text())
        if not title_text or len(title_text) < 10:
            return {"success": False, "error": "Product title too short"}
        
        out = {
            "url": url,
            "status": 200,
            "title": title_text,  # Add top-level title for SEO runner
            "elements": {},
            "success": True
        }
        
        # Title
        out["elements"]["productTitle"] = {"present": True, "text": [title_text]}
        
        # Bullets
        bullets = []
        bullets_container = soup.select_one("#feature-bullets")
        if bullets_container:
            for item in bullets_container.select("li span.a-list-item"):
                text = _clean_text(item.get_text())
                if text and len(text) > 3:
                    bullets.append(text)
        out["elements"]["feature-bullets"] = {"present": bool(bullets), "bullets": bullets, "text": bullets}
        
        # Description
        desc_elem = soup.select_one("#productDescription")
        desc_text = _clean_text(desc_elem.get_text()) if desc_elem else ""
        out["elements"]["productDescription"] = {"present": bool(desc_text), "text": [desc_text] if desc_text else []}
        
        # Price
        price_text = ""
        for selector in ["#apex_desktop span.a-offscreen", "#corePrice_feature_div span.a-offscreen", "span.a-price span.a-offscreen"]:
            elem = soup.select_one(selector)
            if elem:
                price_text = _clean_text(elem.get_text())
                if price_text:
                    break
        
        price_amount, price_currency = _parse_price_value(price_text) if price_text else (None, None)
        out["price"] = {"raw": price_text, "amount": price_amount, "currency": price_currency}
        
        # Images
        images = []
        main_img = soup.select_one("#landingImage, #imgTagWrapperId img")
        if main_img and main_img.get("src"):
            images.append(main_img["src"])
        out["images"] = {
            "all_images": images,
            "main_image": images[0] if images else None,
            "image_count": len(images)
        }
        
        # Brand
        brand_elem = soup.select_one("#bylineInfo, #brand")
        out["brand"] = _clean_text(brand_elem.get_text()) if brand_elem else ""
        
        logger.info(f"   ✅ CloudScraper extracted: {title_text[:50]}...")
        return out
    
    except Exception as e:
        return {"success": False, "error": f"CloudScraper extraction failed: {e}"}


async def _extract_amazon_data(page, url: str) -> Dict[str, Any]:
    """Extract product data from Amazon page using Playwright selectors"""
    
    try:
        # Check if product title exists (critical element)
        title_elem = await page.query_selector("#productTitle")
        if not title_elem:
            return {
                "success": False,
                "error": "Product title not found - page likely blocked or invalid ASIN",
                "url": url
            }
        
        title_text = _clean_text(await title_elem.inner_text())
        if not title_text:
            return {
                "success": False,
                "error": "Product title empty - page likely blocked",
                "url": url
            }
        
        logger.info(f"   📦 Product: {title_text[:60]}...")
        
        out: Dict[str, Any] = {
            "url": url,
            "status": 200,
            "title": title_text,  # Add top-level title for SEO runner
            "elements": {}
        }
        
        # 1. Product Title
        out["elements"]["productTitle"] = {
            "present": True,
            "text": [title_text]
        }
        
        # 2. Product Overview (specs table)
        pov_rows: List[Tuple[str, str]] = []
        pov_table = await page.query_selector("#productOverview_feature_div table")
        if pov_table:
            rows = await pov_table.query_selector_all("tr")
            for row in rows:
                cells = await row.query_selector_all("td, th")
                if len(cells) >= 2:
                    label = _clean_text(await cells[0].inner_text())
                    value = _clean_text(await cells[1].inner_text())
                    if label and value:
                        pov_rows.append((label, value))
        
        out["elements"]["productOverview_feature_div"] = {
            "present": bool(pov_rows),
            "kv": dict(pov_rows) if pov_rows else {}
        }
        
        # 3. Feature Bullets
        bullets: List[str] = []
        bullets_container = await page.query_selector("#feature-bullets")
        if bullets_container:
            bullet_items = await bullets_container.query_selector_all("li span.a-list-item")
            for item in bullet_items:
                text = _clean_text(await item.inner_text())
                if text and len(text) > 3:  # Filter out empty/short items
                    bullets.append(text)
        
        out["elements"]["feature-bullets"] = {
            "present": bool(bullets),
            "bullets": bullets,  # Primary key for SEO runner
            "text": bullets      # Keep for backwards compatibility
        }
        
        # 4. Product Description
        desc_text = ""
        desc_elem = await page.query_selector("#productDescription")
        if desc_elem:
            desc_text = _clean_text(await desc_elem.inner_text())
        
        out["elements"]["productDescription"] = {
            "present": bool(desc_text),
            "text": [desc_text] if desc_text else []
        }
        
        # 5. Product Details (technical details table)
        detail_rows: List[Tuple[str, str]] = []
        details_table = await page.query_selector("#prodDetails table, #productDetails_techSpec_section_1")
        if details_table:
            rows = await details_table.query_selector_all("tr")
            for row in rows:
                th = await row.query_selector("th")
                td = await row.query_selector("td")
                if th and td:
                    label = _clean_text(await th.inner_text())
                    value = _clean_text(await td.inner_text())
                    if label and value:
                        detail_rows.append((label, value))
        
        out["elements"]["prodDetails"] = {
            "present": bool(detail_rows),
            "kv": dict(detail_rows) if detail_rows else {}
        }
        
        # 6. Detail Bullets (additional info)
        detail_bullets: List[str] = []
        detail_bullets_div = await page.query_selector("#detailBullets_feature_div")
        if detail_bullets_div:
            items = await detail_bullets_div.query_selector_all("li")
            for item in items:
                text = _clean_text(await item.inner_text())
                if text:
                    detail_bullets.append(text)
        
        out["elements"]["detailBullets_feature_div"] = {
            "present": bool(detail_bullets),
            "text": detail_bullets
        }
        
        # 7. A+ Content
        aplus_texts: List[str] = []
        aplus_div = await page.query_selector("#aplus")
        if aplus_div:
            paragraphs = await aplus_div.query_selector_all("p, h2, h3, .aplus-module")
            for p in paragraphs[:20]:  # Limit to first 20 elements
                text = _clean_text(await p.inner_text())
                if text and len(text) > 10:
                    aplus_texts.append(text)
        
        out["elements"]["aplus"] = {
            "present": bool(aplus_texts),
            "text": aplus_texts
        }
        
        # 8. Price (try multiple selectors)
        price_text = ""
        price_selectors = [
            "#apex_desktop span.a-price span.a-offscreen",
            "#corePrice_feature_div span.a-price span.a-offscreen",
            "#tp_price_block_total_price_ww span.a-offscreen",
            "#priceblock_ourprice",
            "#priceblock_dealprice",
            "span.a-price span.a-offscreen"
        ]
        
        for selector in price_selectors:
            elem = await page.query_selector(selector)
            if elem:
                price_text = _clean_text(await elem.inner_text())
                if price_text:
                    break
        
        price_amount, price_currency = _parse_price_value(price_text) if price_text else (None, None)
        
        out["price"] = {
            "raw": price_text,
            "amount": price_amount,
            "currency": price_currency
        }
        
        # 9. Images
        images: List[str] = []
        # Main image
        main_img = await page.query_selector("#landingImage, #imgTagWrapperId img")
        if main_img:
            src = await main_img.get_attribute("src")
            if src:
                images.append(src)
        
        # Thumbnail images
        thumbs = await page.query_selector_all("#altImages img, .imageThumbnail img")
        for thumb in thumbs[:10]:  # Limit to first 10
            src = await thumb.get_attribute("src")
            if src and src not in images:
                images.append(src)
        
        out["images"] = {
            "all_images": images,
            "main_image": images[0] if images else None,
            "image_count": len(images)
        }
        
        # 10. Brand (from byline or details)
        brand = ""
        brand_elem = await page.query_selector("#bylineInfo, #brand")
        if brand_elem:
            brand = _clean_text(await brand_elem.inner_text())
        
        out["brand"] = brand
        
        # Success!
        out["success"] = True
        
        return out
        
    except Exception as e:
        logger.error(f"Error extracting Amazon data: {e}")
        return {
            "success": False,
            "error": f"Data extraction failed: {str(e)}",
            "url": url
        }


def scrape_amazon_product_playwright(url: str, headless: bool = True, timeout_ms: int = 30000) -> Dict[str, Any]:
    """
    Synchronous wrapper for async Playwright scraper
    
    Args:
        url: Amazon product URL
        headless: Run browser in headless mode
        timeout_ms: Page load timeout (default 30000ms = 30s per attempt)
    
    Returns:
        Dict with scraped data
    """
    try:
        # Run async function in event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(
                scrape_amazon_with_playwright(url, headless, timeout_ms)
            )
            return result
        finally:
            loop.close()
    
    except Exception as e:
        logger.error(f"Playwright scraper crashed: {e}")
        return {
            "success": False,
            "error": f"Playwright scraper crashed: {str(e)}",
            "method": "playwright_crashed"
        }

