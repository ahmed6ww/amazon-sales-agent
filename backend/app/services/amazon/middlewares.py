"""
Custom Scrapy middlewares for anti-blocking
Based on Scrapy middleware best practices from documentation
"""

import random
import logging
from scrapy import signals
from scrapy.downloadermiddlewares.retry import RetryMiddleware
from scrapy.utils.response import response_status_message
from .user_agents import USER_AGENTS

logger = logging.getLogger(__name__)


class RandomUserAgentMiddleware:
    """
    Rotates User-Agent for each request
    Based on Scrapy UserAgentMiddleware documentation
    
    Priority: 400 (before default UserAgentMiddleware at 500)
    """
    
    def __init__(self):
        self.user_agents = USER_AGENTS
        
    @classmethod
    def from_crawler(cls, crawler):
        middleware = cls()
        crawler.signals.connect(middleware.spider_opened, signal=signals.spider_opened)
        return middleware
    
    def spider_opened(self, spider):
        logger.info(f"RandomUserAgentMiddleware enabled with {len(self.user_agents)} user agents")
    
    def process_request(self, request, spider):
        """Set a random User-Agent for each request"""
        user_agent = random.choice(self.user_agents)
        request.headers['User-Agent'] = user_agent
        logger.debug(f"Using User-Agent: {user_agent[:50]}...")


class EnhancedRetryMiddleware(RetryMiddleware):
    """
    Enhanced retry middleware with better error handling
    Based on Scrapy RetryMiddleware documentation
    
    Handles:
    - HTTP 500, 502, 503, 504 (server errors)
    - HTTP 429 (rate limiting)
    - HTTP 403 (forbidden/blocked)
    - Non-text responses (CAPTCHA)
    """
    
    def process_response(self, request, response, spider):
        """
        Process responses and retry on blocking indicators
        """
        # Check for CAPTCHA/blocking indicators
        if response.status == 500 or response.status == 503:
            reason = f'HTTP {response.status} (Amazon blocking)'
            logger.warning(f"Blocking detected: {reason} for {request.url}")
            return self._retry(request, reason, spider) or response
        
        # Check content type for non-HTML responses (CAPTCHA images)
        content_type = response.headers.get('Content-Type', b'').decode('utf-8', errors='ignore').lower()
        if response.status == 200 and 'text/html' not in content_type:
            reason = f'Non-HTML response (Content-Type: {content_type})'
            logger.warning(f"CAPTCHA suspected: {reason} for {request.url}")
            return self._retry(request, reason, spider) or response
        
        # Check for CAPTCHA in response body
        if response.status == 200 and len(response.text) < 10000:
            if 'captcha' in response.text.lower() or 'robot' in response.text.lower():
                reason = 'CAPTCHA page detected in response'
                logger.warning(f"CAPTCHA detected: {reason} for {request.url}")
                return self._retry(request, reason, spider) or response
        
        # Use default retry middleware logic for other cases
        return super().process_response(request, response, spider)


class RandomDelayMiddleware:
    """
    Add random delays between requests to appear more human-like
    Based on Scrapy DOWNLOAD_DELAY settings documentation
    """
    
    def __init__(self, min_delay=2.0, max_delay=5.0):
        self.min_delay = min_delay
        self.max_delay = max_delay
    
    @classmethod
    def from_crawler(cls, crawler):
        min_delay = crawler.settings.getfloat('RANDOM_DELAY_MIN', 2.0)
        max_delay = crawler.settings.getfloat('RANDOM_DELAY_MAX', 5.0)
        return cls(min_delay, max_delay)
    
    def process_request(self, request, spider):
        """Add random delay to request meta"""
        delay = random.uniform(self.min_delay, self.max_delay)
        request.meta['download_delay'] = delay
        logger.debug(f"Adding {delay:.2f}s delay for {request.url}")


class RefererMiddleware:
    """
    Set proper Referer headers to appear more legitimate
    Based on Scrapy RefererMiddleware documentation
    """
    
    def process_request(self, request, spider):
        """Set referer to Amazon homepage"""
        if 'Referer' not in request.headers:
            # Set referer to Amazon homepage for the marketplace
            if 'amazon.com' in request.url:
                request.headers['Referer'] = 'https://www.amazon.com/'
            elif 'amazon.co.uk' in request.url:
                request.headers['Referer'] = 'https://www.amazon.co.uk/'
            elif 'amazon.de' in request.url:
                request.headers['Referer'] = 'https://www.amazon.de/'
            # Add more marketplaces as needed
