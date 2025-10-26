"""
SERP API Amazon Product Scraper

Fast, reliable Amazon product scraping using SERP API.
"""

import requests
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


def scrape_amazon_with_serpapi(asin: str, api_key: str) -> Dict[str, Any]:
    """
    Scrape Amazon product using SERP API
    
    Args:
        asin: Amazon ASIN (e.g., B0D9C28SVB)
        api_key: Your SERP API key
        
    Returns:
        Standardized product data matching pipeline format
    """
    try:
        url = "https://serpapi.com/search"
        params = {
            "engine": "amazon_product",
            "asin": asin,
            "api_key": api_key,
            "country": "us"
        }
        
        logger.info(f"🔍 Calling SERP API for ASIN: {asin}")
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        
        # Check for errors
        if "error" in data:
            return {"success": False, "error": data["error"]}
        
        product = data.get("product_results", {})
        
        if not product:
            return {"success": False, "error": "No product data from SERP API"}
        
        # Extract and normalize data to match pipeline format
        title = product.get("title", "")
        bullets = product.get("feature_bullets", [])
        price_str = product.get("price", "")
        description = product.get("description", "")
        
        # Build standardized response
        result = {
            "success": True,
            "url": f"https://www.amazon.com/dp/{asin}",
            "status": 200,
            "title": title,  # Top-level for SEO runner
            "elements": {
                "productTitle": {
                    "present": bool(title),
                    "text": [title]
                },
                "feature-bullets": {
                    "present": bool(bullets),
                    "bullets": bullets,
                    "text": bullets  # Keep for backwards compatibility
                },
                "productDescription": {
                    "present": bool(description),
                    "text": [description] if description else []
                },
                "productOverview_feature_div": {
                    "present": False,
                    "kv": {}
                }
            },
            "price": {
                "raw": price_str,
                "amount": _parse_price(price_str),
                "currency": "$"
            },
            "images": {
                "all_images": product.get("images", [])[:5],
                "main_image": product.get("images", [None])[0],
                "image_count": len(product.get("images", [])[:5])
            },
            "brand": product.get("brand", ""),
            "method": "serpapi"
        }
        
        logger.info(f"   ✅ SERP API extracted: {title[:50]}...")
        return result
        
    except requests.exceptions.Timeout:
        logger.error("SERP API request timed out")
        return {"success": False, "error": "SERP API request timed out"}
    except requests.exceptions.RequestException as e:
        logger.error(f"SERP API request error: {e}")
        return {"success": False, "error": f"SERP API request failed: {str(e)}"}
    except Exception as e:
        logger.error(f"SERP API error: {e}")
        return {"success": False, "error": str(e)}


def _parse_price(price_str: str) -> float:
    """Extract numeric price from string like '$7.25'"""
    if not price_str:
        return None
    try:
        # Remove currency symbols and commas
        cleaned = price_str.replace("$", "").replace(",", "").strip()
        return float(cleaned)
    except (ValueError, AttributeError):
        return None


def extract_asin_from_url(url: str) -> str:
    """
    Extract ASIN from Amazon URL
    
    Args:
        url: Amazon product URL or ASIN
        
    Returns:
        ASIN string
    """
    import re
    
    # Handle /dp/ format
    match = re.search(r'/dp/([A-Z0-9]{10})', url)
    if match:
        return match.group(1)
    
    # Handle /gp/product/ format
    match = re.search(r'/gp/product/([A-Z0-9]{10})', url)
    if match:
        return match.group(1)
    
    # Handle ASIN in query parameter
    match = re.search(r'[?&]asin=([A-Z0-9]{10})', url)
    if match:
        return match.group(1)
    
    # Assume it's already an ASIN or extract from end
    cleaned = url.replace("https://www.amazon.com/dp/", "")
    cleaned = cleaned.replace("https://www.amazon.com/gp/product/", "")
    asin = cleaned.split("/")[0].split("?")[0]
    
    return asin

