"""Proxy configuration tests."""

import pytest
import os


def test_proxy_list_format():
    """Test that proxy list is properly formatted."""
    proxy_list = os.getenv("SCRAPER_PROXY_LIST", "")
    
    if proxy_list:
        proxies = [p.strip() for p in proxy_list.split(",")]
        
        for proxy in proxies:
            assert proxy.startswith("http://") or proxy.startswith("https://"), \
                f"Invalid proxy format: {proxy}"
            assert ":" in proxy, f"Proxy missing port: {proxy}"


def test_anti_blocking_config():
    """Test anti-blocking configuration values."""
    retry_times = int(os.getenv("SCRAPER_RETRY_TIMES", "3"))
    delay_min = float(os.getenv("RANDOM_DELAY_MIN", "2.0"))
    delay_max = float(os.getenv("RANDOM_DELAY_MAX", "5.0"))
    
    assert retry_times >= 3, "Should have at least 3 retries"
    assert delay_min > 0, "Delay min should be positive"
    assert delay_max > delay_min, "Delay max should be greater than min"
    assert delay_max <= 20, "Delay max should be reasonable (<=20s)"


def test_proxy_rotation_import():
    """Test that proxy rotation middleware can be imported."""
    try:
        from app.services.amazon.anti_blocking.middlewares import ProxyRotationMiddleware
        assert ProxyRotationMiddleware is not None
    except ImportError as e:
        pytest.fail(f"Failed to import ProxyRotationMiddleware: {e}")

