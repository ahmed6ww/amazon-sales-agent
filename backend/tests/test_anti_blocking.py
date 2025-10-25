"""
Comprehensive tests for Amazon scraper anti-blocking features

Tests verify:
1. User Agent rotation works correctly
2. Retry middleware detects and retries on blocking
3. CAPTCHA detection triggers retry
4. Random delays are applied
5. Referer headers are set correctly
6. Settings are loaded properly
"""

import pytest
import os
from unittest.mock import Mock, patch, MagicMock
from scrapy.http import Request, Response, HtmlResponse
from scrapy.exceptions import IgnoreRequest


class TestUserAgentRotation:
    """Test User Agent rotation middleware"""
    
    def test_user_agent_pool_not_empty(self):
        """Verify we have multiple user agents available"""
        from app.services.amazon.user_agents import USER_AGENTS
        
        assert len(USER_AGENTS) >= 10, "Should have at least 10 user agents"
        assert all(isinstance(ua, str) for ua in USER_AGENTS), "All user agents should be strings"
        assert all(len(ua) > 50 for ua in USER_AGENTS), "User agents should be realistic length"
    
    def test_user_agent_contains_browser_info(self):
        """Verify user agents look like real browsers"""
        from app.services.amazon.user_agents import USER_AGENTS
        
        browser_keywords = ['Chrome', 'Firefox', 'Safari', 'Edge', 'AppleWebKit', 'Gecko']
        
        for ua in USER_AGENTS:
            has_browser = any(keyword in ua for keyword in browser_keywords)
            assert has_browser, f"User agent should contain browser info: {ua}"
    
    def test_random_user_agent_returns_valid_agent(self):
        """Test get_random_user_agent returns a valid user agent"""
        from app.services.amazon.user_agents import get_random_user_agent, USER_AGENTS
        
        for _ in range(10):
            ua = get_random_user_agent()
            assert ua in USER_AGENTS, "Should return an agent from the pool"
    
    def test_middleware_sets_user_agent_on_request(self):
        """Test RandomUserAgentMiddleware sets User-Agent header"""
        from app.services.amazon.middlewares import RandomUserAgentMiddleware
        
        middleware = RandomUserAgentMiddleware()
        request = Request('https://amazon.com')
        spider = Mock()
        
        # Process request
        middleware.process_request(request, spider)
        
        # Verify User-Agent header was set
        assert 'User-Agent' in request.headers
        user_agent = request.headers.get('User-Agent').decode('utf-8')
        assert len(user_agent) > 50, "User-Agent should be realistic"
    
    def test_middleware_rotates_user_agents(self):
        """Test that User-Agent actually rotates across requests"""
        from app.services.amazon.middlewares import RandomUserAgentMiddleware
        
        middleware = RandomUserAgentMiddleware()
        spider = Mock()
        
        user_agents = set()
        for _ in range(20):
            request = Request('https://amazon.com')
            middleware.process_request(request, spider)
            ua = request.headers.get('User-Agent').decode('utf-8')
            user_agents.add(ua)
        
        # Should have at least 2 different user agents in 20 requests
        assert len(user_agents) >= 2, "User agents should rotate"


class TestEnhancedRetryMiddleware:
    """Test enhanced retry middleware for CAPTCHA and blocking detection"""
    
    def test_retries_on_500_status(self):
        """Test that HTTP 500 triggers retry"""
        from app.services.amazon.middlewares import EnhancedRetryMiddleware
        
        middleware = EnhancedRetryMiddleware()
        request = Request('https://amazon.com/dp/B123')
        response = Response('https://amazon.com/dp/B123', status=500, body=b'Internal Server Error')
        spider = Mock()
        spider.name = 'test_spider'
        
        # Mock the _retry method to track if it was called
        with patch.object(middleware, '_retry') as mock_retry:
            mock_retry.return_value = request
            result = middleware.process_response(request, response, spider)
            
            # Verify retry was attempted
            mock_retry.assert_called_once()
            call_args = mock_retry.call_args[0]
            assert 'HTTP 500' in call_args[1], "Should mention HTTP 500 in reason"
    
    def test_retries_on_503_status(self):
        """Test that HTTP 503 (service unavailable) triggers retry"""
        from app.services.amazon.middlewares import EnhancedRetryMiddleware
        
        middleware = EnhancedRetryMiddleware()
        request = Request('https://amazon.com/dp/B123')
        response = Response('https://amazon.com/dp/B123', status=503, body=b'Service Unavailable')
        spider = Mock()
        spider.name = 'test_spider'
        
        with patch.object(middleware, '_retry') as mock_retry:
            mock_retry.return_value = request
            result = middleware.process_response(request, response, spider)
            
            mock_retry.assert_called_once()
    
    def test_detects_captcha_by_content_type(self):
        """Test CAPTCHA detection via non-HTML Content-Type"""
        from app.services.amazon.middlewares import EnhancedRetryMiddleware
        
        middleware = EnhancedRetryMiddleware()
        request = Request('https://amazon.com/dp/B123')
        
        # Create response with image content type (CAPTCHA indicator)
        response = Response(
            'https://amazon.com/dp/B123',
            status=200,
            headers={'Content-Type': 'image/jpeg'},
            body=b'fake image data'
        )
        spider = Mock()
        spider.name = 'test_spider'
        
        with patch.object(middleware, '_retry') as mock_retry:
            mock_retry.return_value = request
            result = middleware.process_response(request, response, spider)
            
            # Should trigger retry for non-HTML response
            mock_retry.assert_called_once()
            call_args = mock_retry.call_args[0]
            assert 'Non-HTML' in call_args[1], "Should mention non-HTML response"
    
    def test_detects_captcha_by_body_content(self):
        """Test CAPTCHA detection via keywords in response body"""
        from app.services.amazon.middlewares import EnhancedRetryMiddleware
        
        middleware = EnhancedRetryMiddleware()
        request = Request('https://amazon.com/dp/B123')
        
        # Create response with CAPTCHA keyword in body
        html_with_captcha = b'''
        <html>
            <head><title>Amazon CAPTCHA</title></head>
            <body>
                <h1>Enter the characters you see below</h1>
                <p>Sorry, we just need to make sure you're not a robot.</p>
                <img src="/captcha.jpg">
            </body>
        </html>
        '''
        
        response = HtmlResponse(
            'https://amazon.com/dp/B123',
            status=200,
            headers={'Content-Type': 'text/html'},
            body=html_with_captcha
        )
        spider = Mock()
        spider.name = 'test_spider'
        
        with patch.object(middleware, '_retry') as mock_retry:
            mock_retry.return_value = request
            result = middleware.process_response(request, response, spider)
            
            # Should trigger retry for CAPTCHA page
            mock_retry.assert_called_once()
            call_args = mock_retry.call_args[0]
            assert 'CAPTCHA' in call_args[1], "Should mention CAPTCHA detection"
    
    def test_detects_robot_keyword(self):
        """Test detection of 'robot' keyword in response"""
        from app.services.amazon.middlewares import EnhancedRetryMiddleware
        
        middleware = EnhancedRetryMiddleware()
        request = Request('https://amazon.com/dp/B123')
        
        html_with_robot = b'''
        <html><body>
            <h1>Are you a robot?</h1>
        </body></html>
        '''
        
        response = HtmlResponse(
            'https://amazon.com/dp/B123',
            status=200,
            body=html_with_robot
        )
        spider = Mock()
        spider.name = 'test_spider'
        
        with patch.object(middleware, '_retry') as mock_retry:
            mock_retry.return_value = request
            middleware.process_response(request, response, spider)
            
            mock_retry.assert_called_once()
    
    def test_allows_successful_html_response(self):
        """Test that valid HTML responses are not retried"""
        from app.services.amazon.middlewares import EnhancedRetryMiddleware
        
        middleware = EnhancedRetryMiddleware()
        request = Request('https://amazon.com/dp/B123')
        
        # Valid product page HTML (large enough, no CAPTCHA)
        valid_html = b'<html><head><title>Product</title></head><body>' + b'x' * 15000 + b'</body></html>'
        
        response = HtmlResponse(
            'https://amazon.com/dp/B123',
            status=200,
            headers={'Content-Type': 'text/html'},
            body=valid_html
        )
        spider = Mock()
        spider.name = 'test_spider'
        
        with patch.object(middleware, '_retry') as mock_retry:
            result = middleware.process_response(request, response, spider)
            
            # Should NOT trigger retry for valid response
            mock_retry.assert_not_called()
            assert result == response


class TestRandomDelayMiddleware:
    """Test random delay middleware"""
    
    def test_adds_download_delay_to_request_meta(self):
        """Test that random delay is added to request meta"""
        from app.services.amazon.middlewares import RandomDelayMiddleware
        
        middleware = RandomDelayMiddleware(min_delay=2.0, max_delay=5.0)
        request = Request('https://amazon.com')
        spider = Mock()
        
        middleware.process_request(request, spider)
        
        # Verify delay was added
        assert 'download_delay' in request.meta
        delay = request.meta['download_delay']
        assert 2.0 <= delay <= 5.0, f"Delay {delay} should be between 2.0 and 5.0"
    
    def test_delay_is_random(self):
        """Test that delays vary across requests"""
        from app.services.amazon.middlewares import RandomDelayMiddleware
        
        middleware = RandomDelayMiddleware(min_delay=1.0, max_delay=3.0)
        spider = Mock()
        
        delays = []
        for _ in range(10):
            request = Request('https://amazon.com')
            middleware.process_request(request, spider)
            delays.append(request.meta['download_delay'])
        
        # Should have at least 3 different delay values in 10 requests
        unique_delays = len(set(delays))
        assert unique_delays >= 3, "Delays should be random and varied"
    
    def test_from_crawler_loads_settings(self):
        """Test that middleware loads settings from crawler"""
        from app.services.amazon.middlewares import RandomDelayMiddleware
        
        crawler = Mock()
        crawler.settings.getfloat = Mock(side_effect=lambda key, default: {
            'RANDOM_DELAY_MIN': 3.0,
            'RANDOM_DELAY_MAX': 6.0
        }.get(key, default))
        
        middleware = RandomDelayMiddleware.from_crawler(crawler)
        
        assert middleware.min_delay == 3.0
        assert middleware.max_delay == 6.0


class TestRefererMiddleware:
    """Test referer header middleware"""
    
    def test_sets_referer_for_amazon_com(self):
        """Test that Referer is set for amazon.com URLs"""
        from app.services.amazon.middlewares import RefererMiddleware
        
        middleware = RefererMiddleware()
        request = Request('https://www.amazon.com/dp/B123456789')
        spider = Mock()
        
        middleware.process_request(request, spider)
        
        assert 'Referer' in request.headers
        referer = request.headers.get('Referer').decode('utf-8')
        assert referer == 'https://www.amazon.com/'
    
    def test_sets_referer_for_amazon_uk(self):
        """Test that Referer is set for amazon.co.uk URLs"""
        from app.services.amazon.middlewares import RefererMiddleware
        
        middleware = RefererMiddleware()
        request = Request('https://www.amazon.co.uk/dp/B123456789')
        spider = Mock()
        
        middleware.process_request(request, spider)
        
        referer = request.headers.get('Referer').decode('utf-8')
        assert referer == 'https://www.amazon.co.uk/'
    
    def test_sets_referer_for_amazon_de(self):
        """Test that Referer is set for amazon.de URLs"""
        from app.services.amazon.middlewares import RefererMiddleware
        
        middleware = RefererMiddleware()
        request = Request('https://www.amazon.de/dp/B123456789')
        spider = Mock()
        
        middleware.process_request(request, spider)
        
        referer = request.headers.get('Referer').decode('utf-8')
        assert referer == 'https://www.amazon.de/'
    
    def test_does_not_override_existing_referer(self):
        """Test that existing Referer headers are not overridden"""
        from app.services.amazon.middlewares import RefererMiddleware
        
        middleware = RefererMiddleware()
        request = Request(
            'https://www.amazon.com/dp/B123456789',
            headers={'Referer': 'https://example.com'}
        )
        spider = Mock()
        
        middleware.process_request(request, spider)
        
        referer = request.headers.get('Referer').decode('utf-8')
        assert referer == 'https://example.com', "Should not override existing Referer"


class TestAntiBlockingSettings:
    """Test anti-blocking settings configuration"""
    
    def test_settings_module_loads(self):
        """Test that anti_blocking module loads without errors"""
        from app.services.amazon.anti_blocking import get_anti_blocking_settings
        
        settings = get_anti_blocking_settings()
        assert isinstance(settings, dict)
        assert len(settings) > 0
    
    def test_retry_settings_configured(self):
        """Test that retry settings are properly configured"""
        from app.services.amazon.anti_blocking import get_anti_blocking_settings
        
        settings = get_anti_blocking_settings()
        
        assert settings['RETRY_ENABLED'] is True
        assert settings['RETRY_TIMES'] >= 3
        assert isinstance(settings['RETRY_HTTP_CODES'], list)
        assert 500 in settings['RETRY_HTTP_CODES']
        assert 503 in settings['RETRY_HTTP_CODES']
        assert 429 in settings['RETRY_HTTP_CODES']
        assert 403 in settings['RETRY_HTTP_CODES']
    
    def test_autothrottle_enabled(self):
        """Test that AutoThrottle is enabled"""
        from app.services.amazon.anti_blocking import get_anti_blocking_settings
        
        settings = get_anti_blocking_settings()
        
        assert settings['AUTOTHROTTLE_ENABLED'] is True
        assert settings['AUTOTHROTTLE_START_DELAY'] >= 1.0
        assert settings['AUTOTHROTTLE_TARGET_CONCURRENCY'] <= 2.0
    
    def test_cookies_enabled(self):
        """Test that cookies are enabled"""
        from app.services.amazon.anti_blocking import get_anti_blocking_settings
        
        settings = get_anti_blocking_settings()
        
        assert settings['COOKIES_ENABLED'] is True
    
    def test_middlewares_configured(self):
        """Test that custom middlewares are configured"""
        from app.services.amazon.anti_blocking import get_anti_blocking_settings
        
        settings = get_anti_blocking_settings()
        
        middlewares = settings['DOWNLOADER_MIDDLEWARES']
        
        # Custom middlewares should be present
        assert 'app.services.amazon.middlewares.RandomUserAgentMiddleware' in middlewares
        assert 'app.services.amazon.middlewares.RefererMiddleware' in middlewares
        assert 'app.services.amazon.middlewares.RandomDelayMiddleware' in middlewares
        assert 'app.services.amazon.middlewares.EnhancedRetryMiddleware' in middlewares
        
        # Built-in UserAgentMiddleware should be disabled (None)
        assert middlewares['scrapy.downloadermiddlewares.useragent.UserAgentMiddleware'] is None
    
    def test_default_headers_configured(self):
        """Test that default headers are configured properly"""
        from app.services.amazon.anti_blocking import get_anti_blocking_settings
        
        settings = get_anti_blocking_settings()
        
        headers = settings['DEFAULT_REQUEST_HEADERS']
        
        assert 'Accept' in headers
        assert 'Accept-Language' in headers
        assert 'Accept-Encoding' in headers
        assert 'gzip' in headers['Accept-Encoding']
        assert 'Sec-Fetch-Dest' in headers
        assert headers['Sec-Fetch-Dest'] == 'document'
    
    def test_concurrent_requests_limited(self):
        """Test that concurrent requests are limited"""
        from app.services.amazon.anti_blocking import get_anti_blocking_settings
        
        settings = get_anti_blocking_settings()
        
        # Should be conservative to avoid detection
        assert settings['CONCURRENT_REQUESTS'] <= 2
        assert settings['CONCURRENT_REQUESTS_PER_DOMAIN'] <= 2
    
    def test_robotstxt_obey_disabled(self):
        """Test that ROBOTSTXT_OBEY is disabled (required for Amazon)"""
        from app.services.amazon.anti_blocking import get_anti_blocking_settings
        
        settings = get_anti_blocking_settings()
        
        assert settings['ROBOTSTXT_OBEY'] is False


class TestScraperIntegration:
    """Integration tests for the scraper with anti-blocking"""
    
    @patch('app.services.amazon.scraper.CrawlerProcess')
    def test_scraper_loads_anti_blocking_settings(self, mock_crawler_process):
        """Test that scraper loads anti-blocking settings"""
        from app.services.amazon.scraper import scrape_amazon_product
        
        # Mock the crawler process
        mock_process = MagicMock()
        mock_crawler = MagicMock()
        mock_crawler.spider.scraped = {'success': True, 'data': {'title': 'Test Product'}}
        mock_crawler.stats.get_value.return_value = {'success': True, 'data': {'title': 'Test'}}
        mock_process.create_crawler.return_value = mock_crawler
        mock_crawler_process.return_value = mock_process
        
        result = scrape_amazon_product('https://amazon.com/dp/B123')
        
        # Verify CrawlerProcess was called with settings
        assert mock_crawler_process.called
        settings = mock_crawler_process.call_args[0][0]
        
        # Verify anti-blocking features are present
        assert 'RETRY_ENABLED' in settings
        assert 'DOWNLOADER_MIDDLEWARES' in settings
    
    def test_anti_blocking_import_error_fallback(self):
        """Test graceful fallback when anti_blocking module fails to import"""
        from app.services.amazon.scraper import scrape_amazon_product
        
        with patch('app.services.amazon.scraper.CrawlerProcess') as mock_crawler_process:
            # Mock import error
            with patch.dict('sys.modules', {'app.services.amazon.anti_blocking': None}):
                mock_process = MagicMock()
                mock_crawler = MagicMock()
                mock_crawler.spider.scraped = {'success': True, 'data': {}}
                mock_crawler.stats.get_value.return_value = {'success': True, 'data': {}}
                mock_process.create_crawler.return_value = mock_crawler
                mock_crawler_process.return_value = mock_process
                
                # Should not crash, should use fallback settings
                result = scrape_amazon_product('https://amazon.com/dp/B123')
                
                # Verify fallback settings were used
                assert mock_crawler_process.called
                settings = mock_crawler_process.call_args[0][0]
                assert 'ROBOTSTXT_OBEY' in settings
                assert 'DOWNLOAD_DELAY' in settings


class TestEndToEndScenarios:
    """End-to-end scenario tests"""
    
    def test_blocking_detection_and_retry_flow(self):
        """Test complete flow: detect blocking -> retry with new UA"""
        from app.services.amazon.middlewares import (
            EnhancedRetryMiddleware,
            RandomUserAgentMiddleware
        )
        
        # Create middlewares
        retry_mw = EnhancedRetryMiddleware()
        ua_mw = RandomUserAgentMiddleware()
        
        # Simulate first request (gets blocked)
        request1 = Request('https://amazon.com/dp/B123')
        spider = Mock()
        spider.name = 'test_spider'
        
        # Apply user agent
        ua_mw.process_request(request1, spider)
        first_ua = request1.headers.get('User-Agent').decode('utf-8')
        
        # Simulate blocking response (HTTP 500)
        blocked_response = Response(
            'https://amazon.com/dp/B123',
            status=500,
            body=b'Error'
        )
        
        # Process response (should trigger retry)
        with patch.object(retry_mw, '_retry') as mock_retry:
            retry_request = Request('https://amazon.com/dp/B123')
            mock_retry.return_value = retry_request
            
            result = retry_mw.process_response(request1, blocked_response, spider)
            
            # Verify retry was triggered
            assert mock_retry.called
            
            # Apply new user agent to retry request
            ua_mw.process_request(retry_request, spider)
            retry_ua = retry_request.headers.get('User-Agent').decode('utf-8')
            
            # User agent might be different (random rotation)
            assert len(retry_ua) > 50
    
    def test_captcha_detection_triggers_retry_with_delay(self):
        """Test CAPTCHA detection triggers retry with random delay"""
        from app.services.amazon.middlewares import (
            EnhancedRetryMiddleware,
            RandomDelayMiddleware
        )
        
        retry_mw = EnhancedRetryMiddleware()
        delay_mw = RandomDelayMiddleware(min_delay=2.0, max_delay=5.0)
        
        request = Request('https://amazon.com/dp/B123')
        spider = Mock()
        spider.name = 'test_spider'
        
        # CAPTCHA response
        captcha_response = HtmlResponse(
            'https://amazon.com/dp/B123',
            status=200,
            body=b'<html><body>Enter the characters you see below (captcha)</body></html>'
        )
        
        # Process response
        with patch.object(retry_mw, '_retry') as mock_retry:
            retry_request = Request('https://amazon.com/dp/B123')
            mock_retry.return_value = retry_request
            
            retry_mw.process_response(request, captcha_response, spider)
            
            # Verify retry was triggered
            assert mock_retry.called
            
            # Apply delay to retry request
            delay_mw.process_request(retry_request, spider)
            
            # Verify delay was added
            assert 'download_delay' in retry_request.meta
            assert 2.0 <= retry_request.meta['download_delay'] <= 5.0


# Pytest fixtures
@pytest.fixture
def mock_spider():
    """Create a mock spider for testing"""
    spider = Mock()
    spider.name = 'test_spider'
    spider.settings = Mock()
    return spider


@pytest.fixture
def sample_request():
    """Create a sample request for testing"""
    return Request('https://www.amazon.com/dp/B08KT2Z93D')


@pytest.fixture
def blocking_response():
    """Create a mock blocking response (HTTP 500)"""
    return Response(
        'https://www.amazon.com/dp/B08KT2Z93D',
        status=500,
        body=b'Internal Server Error'
    )


@pytest.fixture
def captcha_response():
    """Create a mock CAPTCHA response"""
    html = b'''
    <html>
        <head><title>Amazon CAPTCHA</title></head>
        <body>
            <h1>Enter the characters you see below</h1>
            <p>Sorry, we just need to make sure you're not a robot.</p>
        </body>
    </html>
    '''
    return HtmlResponse(
        'https://www.amazon.com/dp/B08KT2Z93D',
        status=200,
        headers={'Content-Type': 'text/html'},
        body=html
    )


@pytest.fixture
def valid_response():
    """Create a mock valid product page response"""
    html = b'<html><head><title>Product Page</title></head><body>' + b'x' * 20000 + b'</body></html>'
    return HtmlResponse(
        'https://www.amazon.com/dp/B08KT2Z93D',
        status=200,
        headers={'Content-Type': 'text/html'},
        body=html
    )


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
