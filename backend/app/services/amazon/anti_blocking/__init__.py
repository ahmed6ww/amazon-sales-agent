"""
Anti-Blocking Module for Amazon Scraper

Provides comprehensive anti-detection features:
- User Agent Rotation
- Header Randomization
- Residential Proxy Rotation
- Random Delays (Human-like behavior)
- Browser Fingerprint Masking
- Smart Retry Logic

Usage:
    from app.services.amazon.anti_blocking import get_anti_blocking_settings
    
    settings = get_anti_blocking_settings()
    process = CrawlerProcess(settings)
"""

from .user_agents import (
    get_random_user_agent,
    get_desktop_user_agent,
    get_chrome_user_agent,
)
from .headers import get_random_headers, get_amazon_session_headers
from .proxy_manager import ProxyManager, get_proxy_manager
from .middlewares import (
    RotateUserAgentMiddleware,
    RotateHeadersMiddleware,
    RotateProxyMiddleware,
    RandomDelayMiddleware,
    SmartRetryMiddleware,
    BrowserFingerprintMiddleware,
)


def get_anti_blocking_settings() -> dict:
    """
    Get Scrapy settings with all anti-blocking features enabled
    
    Returns:
        dict: Scrapy settings with middlewares and configuration
    """
    return {
        # Disable robots.txt (Amazon blocks scrapers)
        "ROBOTSTXT_OBEY": False,
        
        # Logging
        "LOG_LEVEL": "INFO",
        
        # Enable cookies (maintain session)
        "COOKIES_ENABLED": True,
        
        # Timeouts
        "DOWNLOAD_TIMEOUT": 45,
        
        # Concurrent requests (keep low to avoid detection)
        "CONCURRENT_REQUESTS": 1,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 1,
        
        # Random delays (CRITICAL for avoiding detection)
        "RANDOM_DELAY_MIN": 2.0,
        "RANDOM_DELAY_MAX": 5.0,
        
        # Retry settings
        "RETRY_ENABLED": True,
        "RETRY_TIMES": 3,
        "RETRY_HTTP_CODES": [429, 500, 502, 503, 504, 522, 524, 408, 403],
        
        # Disable AutoThrottle (we use custom delay middleware)
        "AUTOTHROTTLE_ENABLED": False,
        
        # Downloader Middlewares (order matters!)
        "DOWNLOADER_MIDDLEWARES": {
            # Disable default retry (we use custom)
            "scrapy.downloadermiddlewares.retry.RetryMiddleware": None,
            
            # Our custom middlewares
            "app.services.amazon.anti_blocking.middlewares.RotateUserAgentMiddleware": 400,
            "app.services.amazon.anti_blocking.middlewares.RotateHeadersMiddleware": 410,
            "app.services.amazon.anti_blocking.middlewares.BrowserFingerprintMiddleware": 420,
            "app.services.amazon.anti_blocking.middlewares.RotateProxyMiddleware": 500,
            "app.services.amazon.anti_blocking.middlewares.RandomDelayMiddleware": 550,
            "app.services.amazon.anti_blocking.middlewares.SmartRetryMiddleware": 600,
        },
    }


__all__ = [
    "get_random_user_agent",
    "get_desktop_user_agent",
    "get_chrome_user_agent",
    "get_random_headers",
    "get_amazon_session_headers",
    "ProxyManager",
    "get_proxy_manager",
    "RotateUserAgentMiddleware",
    "RotateHeadersMiddleware",
    "RotateProxyMiddleware",
    "RandomDelayMiddleware",
    "SmartRetryMiddleware",
    "BrowserFingerprintMiddleware",
    "get_anti_blocking_settings",
]

