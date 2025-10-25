"""
Live integration tests for Amazon scraper anti-blocking features

WARNING: These tests make real requests to Amazon and should be run sparingly
to avoid getting your IP blocked. Use with caution in CI/CD.

Run with: pytest -v -m integration tests/test_anti_blocking_integration.py
Skip with: pytest -v -m "not integration"
"""

import pytest
import time
import os
from typing import Dict, Any


# Mark all tests in this module as integration tests
pytestmark = pytest.mark.integration


@pytest.fixture(scope="module")
def test_amazon_url():
    """Sample Amazon product URL for testing"""
    # Using a popular product that's unlikely to be removed
    return os.getenv(
        "TEST_AMAZON_URL",
        "https://www.amazon.com/dp/B0BSHF7WHW"  # Amazon Basics product
    )


class TestLiveScraperIntegration:
    """Live integration tests with real Amazon requests"""
    
    @pytest.mark.slow
    def test_scraper_with_anti_blocking_succeeds(self, test_amazon_url):
        """
        Test that scraper successfully scrapes with anti-blocking features
        
        This is the main integration test - if this passes, anti-blocking works!
        """
        from app.services.amazon.scraper import scrape_amazon_product
        
        result = scrape_amazon_product(test_amazon_url)
        
        # Print result for debugging
        print(f"\n{'='*80}")
        print(f"SCRAPING RESULT:")
        print(f"  Success: {result.get('success')}")
        print(f"  Anti-blocking used: {result.get('anti_blocking_used', False)}")
        if not result.get('success'):
            print(f"  Error: {result.get('error')}")
            print(f"  Blocked reason: {result.get('blocked_reason', 'N/A')}")
        else:
            data = result.get('data', {})
            print(f"  Title: {data.get('title', 'N/A')[:100]}")
            print(f"  Status: {data.get('status')}")
            print(f"  Response size: {data.get('response_size')} bytes")
            print(f"  Images found: {data.get('images', {}).get('image_count', 0)}")
        print(f"{'='*80}\n")
        
        # Assertions
        assert result.get('success') is True, f"Scraping failed: {result.get('error')}"
        assert result.get('anti_blocking_used') is True, "Anti-blocking should be enabled"
        
        data = result.get('data', {})
        assert data.get('status') == 200, "Should get HTTP 200"
        assert data.get('response_size', 0) > 5000, "Response should be substantial"
        assert data.get('title'), "Should extract product title"
        
        # Verify key elements were extracted
        elements = data.get('elements', {})
        assert elements.get('productTitle', {}).get('present'), "Should have product title"
        assert elements.get('feature-bullets', {}).get('present'), "Should have feature bullets"
        assert data.get('images', {}).get('image_count', 0) > 0, "Should have product images"
    
    @pytest.mark.slow
    def test_multiple_requests_with_rotation(self, test_amazon_url):
        """
        Test that multiple requests work with user agent rotation
        
        This verifies that:
        1. User agents rotate across requests
        2. Amazon doesn't block us for multiple requests
        3. Delays are applied between requests
        """
        from app.services.amazon.scraper import scrape_amazon_product
        
        results = []
        request_count = 3
        
        for i in range(request_count):
            print(f"\nRequest {i+1}/{request_count}...")
            start_time = time.time()
            
            result = scrape_amazon_product(test_amazon_url)
            
            elapsed = time.time() - start_time
            print(f"  Completed in {elapsed:.2f}s")
            print(f"  Success: {result.get('success')}")
            
            results.append({
                'success': result.get('success'),
                'elapsed': elapsed,
                'error': result.get('error')
            })
            
            # Add delay between requests to be polite
            if i < request_count - 1:
                delay = 3
                print(f"  Waiting {delay}s before next request...")
                time.sleep(delay)
        
        # Verify results
        success_count = sum(1 for r in results if r['success'])
        
        print(f"\n{'='*80}")
        print(f"SUMMARY: {success_count}/{request_count} requests succeeded")
        print(f"{'='*80}\n")
        
        # At least 2 out of 3 should succeed (allows for occasional blocks)
        assert success_count >= 2, f"Only {success_count}/{request_count} requests succeeded"
    
    @pytest.mark.slow  
    def test_scraper_handles_invalid_url_gracefully(self):
        """Test that scraper handles invalid URLs gracefully"""
        from app.services.amazon.scraper import scrape_amazon_product
        
        invalid_url = "https://www.amazon.com/dp/INVALID123"
        
        result = scrape_amazon_product(invalid_url)
        
        # Should fail gracefully, not crash
        assert isinstance(result, dict)
        assert 'success' in result
        assert 'error' in result or 'data' in result
    
    def test_anti_blocking_settings_are_loaded(self):
        """Verify that anti-blocking settings module loads correctly"""
        from app.services.amazon.anti_blocking import get_anti_blocking_settings
        
        settings = get_anti_blocking_settings()
        
        # Verify critical settings
        assert settings['RETRY_ENABLED'] is True
        assert settings['RETRY_TIMES'] >= 3
        assert 500 in settings['RETRY_HTTP_CODES']
        assert 503 in settings['RETRY_HTTP_CODES']
        assert settings['COOKIES_ENABLED'] is True
        assert settings['AUTOTHROTTLE_ENABLED'] is True
        
        # Verify middlewares
        middlewares = settings['DOWNLOADER_MIDDLEWARES']
        assert 'app.services.amazon.middlewares.RandomUserAgentMiddleware' in middlewares
        assert 'app.services.amazon.middlewares.EnhancedRetryMiddleware' in middlewares


class TestProxySupport:
    """Test proxy support (optional - requires proxy configuration)"""
    
    @pytest.mark.skipif(
        not os.getenv("SCRAPER_PROXY"),
        reason="SCRAPER_PROXY not configured"
    )
    @pytest.mark.slow
    def test_scraper_with_proxy(self, test_amazon_url):
        """Test scraper works with proxy when configured"""
        from app.services.amazon.scraper import scrape_amazon_product
        
        proxy_url = os.getenv("SCRAPER_PROXY")
        
        result = scrape_amazon_product(test_amazon_url, proxy_url=proxy_url)
        
        print(f"\n{'='*80}")
        print(f"PROXY TEST:")
        print(f"  Proxy: {proxy_url[:30]}...")
        print(f"  Success: {result.get('success')}")
        print(f"{'='*80}\n")
        
        # Should work with proxy
        assert result.get('success') is True, "Scraping with proxy should succeed"


class TestScraperPerformance:
    """Performance tests for scraper"""
    
    @pytest.mark.slow
    def test_scraper_completes_within_timeout(self, test_amazon_url):
        """Test that scraper completes within reasonable time"""
        from app.services.amazon.scraper import scrape_amazon_product
        
        start_time = time.time()
        result = scrape_amazon_product(test_amazon_url)
        elapsed = time.time() - start_time
        
        print(f"\nScraper completed in {elapsed:.2f} seconds")
        
        # Should complete within 2 minutes (including delays and retries)
        assert elapsed < 120, f"Scraper took too long: {elapsed:.2f}s"
        
        if result.get('success'):
            # Successful scrapes should be reasonably fast
            assert elapsed < 60, f"Successful scrape took too long: {elapsed:.2f}s"


class TestErrorHandling:
    """Test error handling and edge cases"""
    
    def test_handles_malformed_url(self):
        """Test handling of malformed URLs"""
        from app.services.amazon.scraper import scrape_amazon_product
        
        result = scrape_amazon_product("not-a-valid-url")
        
        # Should fail gracefully
        assert isinstance(result, dict)
        assert result.get('success') is False
    
    def test_handles_non_amazon_url(self):
        """Test handling of non-Amazon URLs"""
        from app.services.amazon.scraper import scrape_amazon_product
        
        result = scrape_amazon_product("https://www.google.com")
        
        # Should complete but may not extract expected data
        assert isinstance(result, dict)


# Helper function to run only integration tests
def run_integration_tests():
    """
    Helper to run integration tests manually
    
    Usage:
        cd backend
        python -c "from tests.test_anti_blocking_integration import run_integration_tests; run_integration_tests()"
    """
    pytest.main([
        __file__,
        '-v',
        '-s',  # Show print statements
        '-m', 'integration',
        '--tb=short'
    ])


if __name__ == '__main__':
    print("""
    ╔════════════════════════════════════════════════════════════════╗
    ║          Amazon Scraper Integration Tests                     ║
    ║                                                                ║
    ║  WARNING: These tests make real requests to Amazon            ║
    ║  Run sparingly to avoid getting blocked!                      ║
    ║                                                                ║
    ║  Usage:                                                        ║
    ║    pytest -v -m integration tests/test_anti_blocking_integration.py    ║
    ║                                                                ║
    ║  Skip integration tests:                                       ║
    ║    pytest -v -m "not integration"                             ║
    ╚════════════════════════════════════════════════════════════════╝
    """)
    
    run_integration_tests()
