"""
Scrapy Middlewares for Anti-Blocking
Automatically rotates user agents, headers, and proxies
"""

import random
import time
from typing import Optional

from scrapy import signals
from scrapy.http import Request, Response
from scrapy.downloadermiddlewares.retry import RetryMiddleware
from scrapy.utils.response import response_status_message

from .user_agents import get_random_user_agent
from .headers import get_random_headers, get_amazon_session_headers
from .proxy_manager import get_proxy_manager


class RotateUserAgentMiddleware:
    """Rotate user agent for each request"""
    
    def process_request(self, request: Request, spider):
        user_agent = get_random_user_agent()
        request.headers['User-Agent'] = user_agent
        spider.logger.debug(f"Using User-Agent: {user_agent[:50]}...")


class RotateHeadersMiddleware:
    """Rotate headers for each request to look more natural"""
    
    def process_request(self, request: Request, spider):
        # Get user agent from request
        user_agent = request.headers.get('User-Agent', b'').decode('utf-8')
        if not user_agent:
            user_agent = get_random_user_agent()
        
        # Generate random headers
        headers = get_random_headers(user_agent)
        session_headers = get_amazon_session_headers()
        headers.update(session_headers)
        
        # Apply headers to request
        for key, value in headers.items():
            request.headers[key] = value
        
        spider.logger.debug(f"Applied randomized headers with Referer: {headers.get('Referer', 'None')}")


class RotateProxyMiddleware:
    """
    Rotate proxies for each request
    Uses residential proxies if configured
    """
    
    def __init__(self):
        self.proxy_manager = get_proxy_manager()
        self.rotation_strategy = "random"  # "random", "rotating", or "sequential"
    
    @classmethod
    def from_crawler(cls, crawler):
        middleware = cls()
        crawler.signals.connect(middleware.spider_opened, signal=signals.spider_opened)
        return middleware
    
    def spider_opened(self, spider):
        if self.proxy_manager.has_proxies():
            spider.logger.info(f"✅ Proxy rotation enabled with {self.proxy_manager.proxy_count()} proxies")
        else:
            spider.logger.warning("⚠️ No proxies configured - requests will use direct connection")
    
    def process_request(self, request: Request, spider):
        # Skip if no proxies configured
        if not self.proxy_manager.has_proxies():
            return
        
        # Get proxy based on strategy
        if self.rotation_strategy == "random":
            proxy = self.proxy_manager.get_random_proxy()
        elif self.rotation_strategy == "rotating":
            proxy = self.proxy_manager.get_rotating_proxy()
        else:  # sequential
            proxy = self.proxy_manager.get_next_proxy()
        
        if proxy:
            request.meta['proxy'] = proxy
            spider.logger.debug(f"Using proxy: {proxy.split('@')[-1] if '@' in proxy else proxy[:30]}...")


class RandomDelayMiddleware:
    """
    Add random delays between requests to mimic human behavior
    This is CRITICAL for avoiding detection
    """
    
    def __init__(self):
        self.min_delay = 2.0  # Minimum 2 seconds
        self.max_delay = 5.0  # Maximum 5 seconds
        self.last_request_time = None
    
    @classmethod
    def from_crawler(cls, crawler):
        middleware = cls()
        
        # Allow configuration via settings
        settings = crawler.settings
        middleware.min_delay = settings.getfloat('RANDOM_DELAY_MIN', 2.0)
        middleware.max_delay = settings.getfloat('RANDOM_DELAY_MAX', 5.0)
        
        crawler.signals.connect(middleware.spider_opened, signal=signals.spider_opened)
        return middleware
    
    def spider_opened(self, spider):
        spider.logger.info(f"✅ Random delay enabled: {self.min_delay}-{self.max_delay}s between requests")
    
    def process_request(self, request: Request, spider):
        # Add delay before each request (except the first one)
        if self.last_request_time is not None:
            elapsed = time.time() - self.last_request_time
            delay = random.uniform(self.min_delay, self.max_delay)
            
            # If not enough time has passed, wait
            if elapsed < delay:
                wait_time = delay - elapsed
                spider.logger.debug(f"💤 Waiting {wait_time:.2f}s before next request...")
                time.sleep(wait_time)
        
        self.last_request_time = time.time()


class SmartRetryMiddleware(RetryMiddleware):
    """
    Enhanced retry middleware that handles Amazon-specific blocks
    """
    
    def process_response(self, request: Request, response: Response, spider):
        # Detect captcha or blocking
        if response.status in (403, 503):
            spider.logger.warning(f"⚠️ Received {response.status} - Amazon might be blocking")
            reason = f"amazon_block_{response.status}"
            return self._retry(request, reason, spider) or response
        
        # Check for captcha in response body
        if "captcha" in response.text.lower():
            spider.logger.error("🚫 CAPTCHA detected - consider using better proxies or slower rate")
            reason = "captcha_detected"
            return self._retry(request, reason, spider) or response
        
        # Check for insufficient content (might be blocked)
        if len(response.text) < 5000:
            spider.logger.warning(f"⚠️ Response too small ({len(response.text)} bytes) - might be blocked")
            reason = "insufficient_content"
            return self._retry(request, reason, spider) or response
        
        return response


class BrowserFingerprintMiddleware:
    """
    Adds browser fingerprint headers to make requests look more authentic
    """
    
    def process_request(self, request: Request, spider):
        # Add viewport size (common desktop resolution)
        viewport_sizes = [
            "1920x1080",
            "1366x768",
            "1536x864",
            "1440x900",
            "1600x900",
        ]
        
        # Add platform-specific headers (Chrome-based)
        if "Chrome" in request.headers.get('User-Agent', b'').decode('utf-8'):
            request.headers['sec-ch-viewport-width'] = str(random.choice([1920, 1366, 1536, 1440, 1600]))
            request.headers['sec-ch-viewport-height'] = str(random.choice([1080, 768, 864, 900]))

