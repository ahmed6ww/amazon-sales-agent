"""
Scrapy Middlewares for Anti-Blocking
Automatically rotates user agents, headers, and proxies
"""

import random
import logging
from typing import Optional

from scrapy import signals
from scrapy.http import Request, Response
from scrapy.downloadermiddlewares.retry import RetryMiddleware
from scrapy.utils.response import response_status_message

from .user_agents import get_random_user_agent
from .headers import get_random_headers, get_amazon_session_headers
from .proxy_manager import get_proxy_manager

# Module logger for fallback
logger = logging.getLogger(__name__)


def safe_log(spider, level: str, message: str):
    """Safely log to spider logger or fallback to module logger"""
    try:
        if hasattr(spider, 'logger') and spider.logger:
            getattr(spider.logger, level)(message)
        else:
            getattr(logger, level)(message)
    except Exception:
        pass  # Fail silently if logging fails


class RotateUserAgentMiddleware:
    """Rotate user agent for each request"""
    
    def process_request(self, request: Request, spider):
        try:
            user_agent = get_random_user_agent()
            request.headers['User-Agent'] = user_agent
            safe_log(spider, 'debug', f"Using User-Agent: {user_agent[:50]}...")
        except Exception as e:
            safe_log(spider, 'warning', f"Failed to rotate user agent: {e}")


class RotateHeadersMiddleware:
    """Rotate headers for each request to look more natural"""
    
    def process_request(self, request: Request, spider):
        try:
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
            
            safe_log(spider, 'debug', f"Applied randomized headers with Referer: {headers.get('Referer', 'None')}")
        except Exception as e:
            safe_log(spider, 'warning', f"Failed to rotate headers: {e}")


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
        try:
            if self.proxy_manager.has_proxies():
                safe_log(spider, 'info', f"✅ Proxy rotation enabled with {self.proxy_manager.proxy_count()} proxies")
            else:
                safe_log(spider, 'warning', "⚠️ No proxies configured - requests will use direct connection")
        except Exception as e:
            safe_log(spider, 'warning', f"Proxy manager initialization warning: {e}")
    
    def process_request(self, request: Request, spider):
        try:
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
                safe_log(spider, 'debug', f"Using proxy: {proxy.split('@')[-1] if '@' in proxy else proxy[:30]}...")
        except Exception as e:
            safe_log(spider, 'warning', f"Failed to apply proxy: {e}")


class RandomDelayMiddleware:
    """
    Add random delays between requests via Scrapy's DOWNLOAD_DELAY
    IMPORTANT: Don't use time.sleep() - it blocks Scrapy's reactor
    """
    
    def __init__(self):
        self.min_delay = 2.0
        self.max_delay = 5.0
    
    @classmethod
    def from_crawler(cls, crawler):
        middleware = cls()
        settings = crawler.settings
        middleware.min_delay = settings.getfloat('RANDOM_DELAY_MIN', 2.0)
        middleware.max_delay = settings.getfloat('RANDOM_DELAY_MAX', 5.0)
        crawler.signals.connect(middleware.spider_opened, signal=signals.spider_opened)
        return middleware
    
    def spider_opened(self, spider):
        safe_log(spider, 'info', f"✅ Random delay enabled: {self.min_delay}-{self.max_delay}s between requests")
    
    def process_request(self, request: Request, spider):
        try:
            # Set random delay on request meta - Scrapy will handle it
            delay = random.uniform(self.min_delay, self.max_delay)
            request.meta['download_delay'] = delay
            safe_log(spider, 'debug', f"💤 Setting delay: {delay:.2f}s for next request")
        except Exception as e:
            safe_log(spider, 'warning', f"Failed to set delay: {e}")


class SmartRetryMiddleware(RetryMiddleware):
    """
    Enhanced retry middleware that handles Amazon-specific blocks
    """
    
    def process_response(self, request: Request, response: Response, spider):
        try:
            # Detect captcha or blocking
            if response.status in (403, 503):
                safe_log(spider, 'warning', f"⚠️ Received {response.status} - Amazon might be blocking")
                reason = f"amazon_block_{response.status}"
                return self._retry(request, reason, spider) or response
            
            # Check if response is text-based before accessing response.text
            content_type = response.headers.get('Content-Type', b'').decode('utf-8').lower()
            is_text = any(t in content_type for t in ['text/html', 'text/plain', 'application/json', 'application/xml'])
            
            if not is_text:
                safe_log(spider, 'error', f"🚫 Non-text response detected (Content-Type: {content_type}) - Amazon likely blocking with image/captcha")
                reason = "non_text_response"
                return self._retry(request, reason, spider) or response
            
            # Check for captcha in response body (only if text-based)
            if "captcha" in response.text.lower():
                safe_log(spider, 'error', "🚫 CAPTCHA detected - consider using better proxies or slower rate")
                reason = "captcha_detected"
                return self._retry(request, reason, spider) or response
            
            # Check for insufficient content (might be blocked)
            if len(response.text) < 5000:
                safe_log(spider, 'warning', f"⚠️ Response too small ({len(response.text)} bytes) - might be blocked")
                reason = "insufficient_content"
                return self._retry(request, reason, spider) or response
            
            return response
        except Exception as e:
            safe_log(spider, 'error', f"Error in SmartRetryMiddleware: {e}")
            return response


class BrowserFingerprintMiddleware:
    """
    Adds browser fingerprint headers to make requests look more authentic
    """
    
    def process_request(self, request: Request, spider):
        try:
            # Add platform-specific headers (Chrome-based)
            user_agent = request.headers.get('User-Agent', b'').decode('utf-8')
            if "Chrome" in user_agent:
                request.headers['sec-ch-viewport-width'] = str(random.choice([1920, 1366, 1536, 1440, 1600]))
                request.headers['sec-ch-viewport-height'] = str(random.choice([1080, 768, 864, 900]))
        except Exception as e:
            safe_log(spider, 'debug', f"Failed to apply fingerprint headers: {e}")
