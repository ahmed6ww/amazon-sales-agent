"""
Scrapy anti-blocking settings
Based on official Scrapy documentation for avoiding blocks

References from Scrapy docs:
- RetryMiddleware: Handle HTTP errors and timeouts
- UserAgentMiddleware: Rotate user agents
- CookiesMiddleware: Enable cookie handling
- DownloadTimeoutMiddleware: Set proper timeouts
- AutoThrottle: Adaptive rate limiting
"""

import os


def get_anti_blocking_settings():
    """
    Get Scrapy settings optimized for anti-blocking
    
    Based on Scrapy documentation best practices:
    1. ROBOTSTXT_OBEY = False (we need to bypass robots.txt)
    2. RETRY_ENABLED with smart retry codes
    3. COOKIES_ENABLED for session management
    4. AUTOTHROTTLE_ENABLED for adaptive delays
    5. Custom middlewares for rotation
    """
    
    return {
        # =====================================================================
        # CORE SETTINGS (from Scrapy docs)
        # =====================================================================
        "ROBOTSTXT_OBEY": False,  # Required to scrape Amazon
        "LOG_LEVEL": os.getenv("SCRAPER_LOG_LEVEL", "INFO"),
        
        # =====================================================================
        # RETRY MIDDLEWARE (scrapy.downloadermiddlewares.retry)
        # Docs: https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#retry-middleware
        # =====================================================================
        "RETRY_ENABLED": True,
        "RETRY_TIMES": int(os.getenv("SCRAPER_RETRY_TIMES", "5")),  # Increased retries
        "RETRY_HTTP_CODES": [
            500,  # Internal Server Error (Amazon blocking)
            502,  # Bad Gateway
            503,  # Service Unavailable (Amazon rate limiting)
            504,  # Gateway Timeout
            522,  # Connection timed out
            524,  # A timeout occurred
            408,  # Request Timeout
            429,  # Too Many Requests (rate limiting)
            403,  # Forbidden (may be blocking)
        ],
        
        # =====================================================================
        # TIMEOUT SETTINGS (scrapy.downloadermiddlewares.downloadtimeout)
        # Docs: https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#downloadtimeoutmiddleware
        # =====================================================================
        "DOWNLOAD_TIMEOUT": int(os.getenv("SCRAPER_TIMEOUT", "60")),  # Increased timeout
        
        # =====================================================================
        # COOKIE MIDDLEWARE (scrapy.downloadermiddlewares.cookies)
        # Docs: https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#cookiesmiddleware
        # =====================================================================
        "COOKIES_ENABLED": True,
        "COOKIES_DEBUG": False,  # Set to True for debugging
        
        # =====================================================================
        # AUTO THROTTLE (Adaptive rate limiting)
        # Docs: https://docs.scrapy.org/en/latest/topics/autothrottle.html
        # =====================================================================
        "AUTOTHROTTLE_ENABLED": True,
        "AUTOTHROTTLE_START_DELAY": float(os.getenv("SCRAPER_DOWNLOAD_DELAY", "2.0")),
        "AUTOTHROTTLE_MAX_DELAY": 10.0,
        "AUTOTHROTTLE_TARGET_CONCURRENCY": 1.0,  # Conservative for Amazon
        "AUTOTHROTTLE_DEBUG": False,
        
        # =====================================================================
        # CONCURRENT REQUESTS (Limit to avoid detection)
        # Docs: https://docs.scrapy.org/en/latest/topics/settings.html#concurrent-requests
        # =====================================================================
        "CONCURRENT_REQUESTS": 1,  # One request at a time
        "CONCURRENT_REQUESTS_PER_DOMAIN": 1,
        
        # =====================================================================
        # DEFAULT REQUEST HEADERS (Make requests look like real browsers)
        # Docs: https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#defaultheadersmiddleware
        # =====================================================================
        "DEFAULT_REQUEST_HEADERS": {
            # Accept headers (standard browser)
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": os.getenv("SCRAPER_ACCEPT_LANGUAGE", "en-US,en;q=0.9"),
            "Accept-Encoding": "gzip, deflate, br",
            
            # Security headers
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            
            # Browser hints
            "sec-ch-ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            
            # Cache control
            "Cache-Control": "max-age=0",
        },
        
        # =====================================================================
        # DOWNLOADER MIDDLEWARES (Custom + Built-in)
        # Docs: https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
        # Priority order: Lower numbers run first
        # =====================================================================
        "DOWNLOADER_MIDDLEWARES": {
            # Disable built-in UserAgent middleware (we use custom)
            "scrapy.downloadermiddlewares.useragent.UserAgentMiddleware": None,
            
            # Custom middlewares (from our middlewares.py)
            "app.services.amazon.middlewares.RandomUserAgentMiddleware": 400,
            "app.services.amazon.middlewares.RefererMiddleware": 450,
            "app.services.amazon.middlewares.RandomDelayMiddleware": 500,
            
            # Enhanced retry middleware (replaces default)
            "scrapy.downloadermiddlewares.retry.RetryMiddleware": None,
            "app.services.amazon.middlewares.EnhancedRetryMiddleware": 550,
            
            # Keep default middlewares (from DOWNLOADER_MIDDLEWARES_BASE)
            "scrapy.downloadermiddlewares.robotstxt.RobotsTxtMiddleware": 100,
            "scrapy.downloadermiddlewares.httpauth.HttpAuthMiddleware": 300,
            "scrapy.downloadermiddlewares.downloadtimeout.DownloadTimeoutMiddleware": 350,
            "scrapy.downloadermiddlewares.defaultheaders.DefaultHeadersMiddleware": 400,
            "scrapy.downloadermiddlewares.redirect.RedirectMiddleware": 600,
            "scrapy.downloadermiddlewares.cookies.CookiesMiddleware": 700,
            "scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware": 810,
        },
        
        # =====================================================================
        # RANDOM DELAY SETTINGS (for our custom middleware)
        # =====================================================================
        "RANDOM_DELAY_MIN": 2.0,  # Minimum delay between requests
        "RANDOM_DELAY_MAX": 5.0,  # Maximum delay between requests
        
        # =====================================================================
        # HTTP CACHE (Disabled for fresh data)
        # Docs: https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
        # =====================================================================
        "HTTPCACHE_ENABLED": False,
        
        # =====================================================================
        # REDIRECT SETTINGS
        # Docs: https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#redirect-middleware-settings
        # =====================================================================
        "REDIRECT_ENABLED": True,
        "REDIRECT_MAX_TIMES": 20,
        
        # =====================================================================
        # ITEM PIPELINES (None for scraping only)
        # =====================================================================
        "ITEM_PIPELINES": {},
    }
