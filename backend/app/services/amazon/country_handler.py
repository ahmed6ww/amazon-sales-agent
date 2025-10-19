"""
Amazon Country Code Handler

Handles country-specific Amazon URLs and marketplace mapping.
Implements requirements #10-12: Country code handling, extraction, and URL construction.
"""

import re
from typing import Dict, Optional, Tuple
from urllib.parse import urlparse, quote_plus


# Marketplace to Amazon domain mapping (requirement #10)
MARKETPLACE_TO_DOMAIN = {
    "US": "amazon.com",
    "UK": "amazon.co.uk", 
    "GB": "amazon.co.uk",
    "DE": "amazon.de",
    "FR": "amazon.fr",
    "CA": "amazon.ca",
    "AE": "amazon.ae",
    "IN": "amazon.in",
    "IT": "amazon.it",
    "ES": "amazon.es",
    "NL": "amazon.nl",
    "JP": "amazon.jp",
    "AU": "amazon.com.au",
    "BR": "amazon.com.br",
    "MX": "amazon.com.mx",
    "SG": "amazon.sg",
    "TR": "amazon.com.tr",
    "PL": "amazon.pl",
    "SE": "amazon.se",
    "NO": "amazon.no",
    "BE": "amazon.com.be",
    "EG": "amazon.eg",
    "SA": "amazon.sa",
    "ZA": "amazon.co.za"
}

# Reverse mapping for domain to marketplace (prefer UK over GB for amazon.co.uk)
DOMAIN_TO_MARKETPLACE = {}
for marketplace, domain in MARKETPLACE_TO_DOMAIN.items():
    if domain not in DOMAIN_TO_MARKETPLACE:
        DOMAIN_TO_MARKETPLACE[domain] = marketplace
    # Prefer UK over GB for amazon.co.uk
    if domain == "amazon.co.uk" and marketplace == "UK":
        DOMAIN_TO_MARKETPLACE[domain] = "UK"


def extract_country_code_from_url(url: str) -> Optional[str]:
    """
    Extract country code from Amazon URL (requirement #11).
    
    Args:
        url: Amazon URL (e.g., "https://www.amazon.com/dp/B0752X9V28/...")
        
    Returns:
        Country code (e.g., "US") or None if not found
    """
    if not url:
        return None
    
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        
        # Extract domain from netloc (remove www. prefix)
        if domain.startswith('www.'):
            domain = domain[4:]
        
        # Check if it's an Amazon domain
        if not domain.startswith('amazon.'):
            return None
        
        # Map domain to marketplace
        return DOMAIN_TO_MARKETPLACE.get(domain)
        
    except Exception:
        return None


def get_amazon_domain_for_marketplace(marketplace: str) -> str:
    """
    Get Amazon domain for marketplace code (requirement #10).
    
    Args:
        marketplace: Marketplace code (e.g., "US", "UK", "DE")
        
    Returns:
        Amazon domain (e.g., "amazon.com", "amazon.co.uk")
    """
    if not marketplace:
        return "amazon.com"  # Default to US
    
    marketplace_upper = marketplace.upper()
    return MARKETPLACE_TO_DOMAIN.get(marketplace_upper, "amazon.com")


def construct_amazon_url(asin: str, marketplace: str = "US") -> str:
    """
    Construct Amazon product URL with country code (requirement #12).
    
    Args:
        asin: Product ASIN
        marketplace: Marketplace code
        
    Returns:
        Amazon product URL
    """
    domain = get_amazon_domain_for_marketplace(marketplace)
    return f"https://www.{domain}/dp/{asin}"


def construct_amazon_search_url(keyword: str, marketplace: str = "US") -> str:
    """
    Construct Amazon search URL with country code (requirement #13).
    
    Args:
        keyword: Search keyword
        marketplace: Marketplace code
        
    Returns:
        Amazon search URL (e.g., "https://www.amazon.com/s?k=stress+ball")
    """
    domain = get_amazon_domain_for_marketplace(marketplace)
    # Properly URL encode keyword including special characters
    encoded_keyword = quote_plus(keyword)
    return f"https://www.{domain}/s?k={encoded_keyword}"


def extract_base_url_from_input(input_url: str) -> str:
    """
    Extract base URL till country code from input URL (requirement #12).
    
    Args:
        input_url: Full Amazon URL
        
    Returns:
        Base URL (e.g., "https://www.amazon.com")
    """
    if not input_url:
        return "https://www.amazon.com"
    
    try:
        parsed = urlparse(input_url)
        domain = parsed.netloc.lower()
        
        # Ensure www. prefix
        if not domain.startswith('www.'):
            domain = f"www.{domain}"
        
        return f"https://{domain}"
        
    except Exception:
        return "https://www.amazon.com"


def get_marketplace_from_url(url: str) -> str:
    """
    Get marketplace code from URL.
    
    Args:
        url: Amazon URL
        
    Returns:
        Marketplace code (defaults to "US")
    """
    country_code = extract_country_code_from_url(url)
    return country_code or "US"


def validate_marketplace(marketplace: str) -> bool:
    """
    Validate if marketplace code is supported.
    
    Args:
        marketplace: Marketplace code to validate
        
    Returns:
        True if supported, False otherwise
    """
    return marketplace.upper() in MARKETPLACE_TO_DOMAIN


def get_supported_marketplaces() -> Dict[str, str]:
    """
    Get list of supported marketplaces.
    
    Returns:
        Dictionary of marketplace codes to domains
    """
    return MARKETPLACE_TO_DOMAIN.copy()
