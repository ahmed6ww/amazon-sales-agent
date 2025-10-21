"""
Proxy Rotation Manager for Amazon Scraper
Supports residential proxy rotation to avoid IP-based blocking
"""

import os
import random
from typing import Optional, List
from datetime import datetime, timedelta


class ProxyManager:
    """
    Manages proxy rotation for scraping
    Supports multiple proxy providers and formats
    """
    
    def __init__(self):
        self.proxies: List[str] = []
        self.load_proxies()
        self.last_rotation = datetime.now()
        self.rotation_interval = timedelta(seconds=30)  # Rotate every 30 seconds
        self.current_proxy_index = 0
        
    def load_proxies(self):
        """Load proxies from environment variables"""
        # Single proxy from .env
        single_proxy = os.getenv("SCRAPER_PROXY")
        if single_proxy:
            self.proxies.append(single_proxy)
        
        # Multiple proxies (comma-separated)
        proxy_list = os.getenv("SCRAPER_PROXY_LIST")
        if proxy_list:
            proxies = [p.strip() for p in proxy_list.split(",") if p.strip()]
            self.proxies.extend(proxies)
        
        # Provider-specific formats
        self._load_provider_proxies()
        
    def _load_provider_proxies(self):
        """Load proxies from specific providers"""
        # Bright Data / Luminati
        bright_data_host = os.getenv("BRIGHT_DATA_HOST")
        bright_data_user = os.getenv("BRIGHT_DATA_USER")
        bright_data_pass = os.getenv("BRIGHT_DATA_PASS")
        if all([bright_data_host, bright_data_user, bright_data_pass]):
            proxy = f"http://{bright_data_user}:{bright_data_pass}@{bright_data_host}"
            self.proxies.append(proxy)
        
        # Smartproxy
        smartproxy_host = os.getenv("SMARTPROXY_HOST")
        smartproxy_user = os.getenv("SMARTPROXY_USER")
        smartproxy_pass = os.getenv("SMARTPROXY_PASS")
        if all([smartproxy_host, smartproxy_user, smartproxy_pass]):
            proxy = f"http://{smartproxy_user}:{smartproxy_pass}@{smartproxy_host}"
            self.proxies.append(proxy)
        
        # Oxylabs
        oxylabs_host = os.getenv("OXYLABS_HOST")
        oxylabs_user = os.getenv("OXYLABS_USER")
        oxylabs_pass = os.getenv("OXYLABS_PASS")
        if all([oxylabs_host, oxylabs_user, oxylabs_pass]):
            proxy = f"http://{oxylabs_user}:{oxylabs_pass}@{oxylabs_host}"
            self.proxies.append(proxy)
        
        # IPRoyal
        iproyal_host = os.getenv("IPROYAL_HOST")
        iproyal_user = os.getenv("IPROYAL_USER")
        iproyal_pass = os.getenv("IPROYAL_PASS")
        if all([iproyal_host, iproyal_user, iproyal_pass]):
            proxy = f"http://{iproyal_user}:{iproyal_pass}@{iproyal_host}"
            self.proxies.append(proxy)
    
    def get_random_proxy(self) -> Optional[str]:
        """Get a random proxy from the pool"""
        if not self.proxies:
            return None
        return random.choice(self.proxies)
    
    def get_rotating_proxy(self) -> Optional[str]:
        """
        Get proxy with time-based rotation
        Same proxy for rotation_interval, then switches
        """
        if not self.proxies:
            return None
        
        # Check if we should rotate
        if datetime.now() - self.last_rotation > self.rotation_interval:
            self.current_proxy_index = (self.current_proxy_index + 1) % len(self.proxies)
            self.last_rotation = datetime.now()
        
        return self.proxies[self.current_proxy_index]
    
    def get_next_proxy(self) -> Optional[str]:
        """Get the next proxy in sequence"""
        if not self.proxies:
            return None
        
        self.current_proxy_index = (self.current_proxy_index + 1) % len(self.proxies)
        return self.proxies[self.current_proxy_index]
    
    def has_proxies(self) -> bool:
        """Check if any proxies are configured"""
        return len(self.proxies) > 0
    
    def proxy_count(self) -> int:
        """Get number of configured proxies"""
        return len(self.proxies)


# Global instance
_proxy_manager: Optional[ProxyManager] = None


def get_proxy_manager() -> ProxyManager:
    """Get or create the global proxy manager instance"""
    global _proxy_manager
    if _proxy_manager is None:
        _proxy_manager = ProxyManager()
    return _proxy_manager

