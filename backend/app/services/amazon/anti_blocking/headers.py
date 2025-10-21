"""
Header Rotation for Amazon Scraper
Provides realistic browser headers to avoid detection
"""

import random
from typing import Dict


# Accept-Language variations
ACCEPT_LANGUAGES = [
    "en-US,en;q=0.9",
    "en-US,en;q=0.9,es;q=0.8",
    "en-GB,en;q=0.9,en-US;q=0.8",
    "en-US,en;q=0.9,fr;q=0.8",
    "en-US,en;q=0.9,de;q=0.8",
]

# Referers (looks like natural browsing)
REFERERS = [
    "https://www.amazon.com/",
    "https://www.amazon.com/s?k=",
    "https://www.google.com/",
    "https://www.bing.com/",
]


def get_random_headers(user_agent: str) -> Dict[str, str]:
    """
    Generate realistic browser headers with randomization
    
    Args:
        user_agent: The user agent string to use
        
    Returns:
        Dict of HTTP headers
    """
    headers = {
        "User-Agent": user_agent,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Language": random.choice(ACCEPT_LANGUAGES),
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Cache-Control": "max-age=0",
    }
    
    # Add Referer for some requests (makes it look more natural)
    if random.random() > 0.3:  # 70% chance of having referer
        headers["Referer"] = random.choice(REFERERS)
    
    # Add sec-ch-ua headers for Chrome-based browsers
    if "Chrome" in user_agent:
        # Extract Chrome version
        chrome_version = "131"
        if "Chrome/" in user_agent:
            try:
                chrome_version = user_agent.split("Chrome/")[1].split(".")[0]
            except:
                pass
        
        headers["sec-ch-ua"] = f'"Chromium";v="{chrome_version}", "Google Chrome";v="{chrome_version}", "Not.A/Brand";v="24"'
        headers["sec-ch-ua-mobile"] = "?0"
        headers["sec-ch-ua-platform"] = '"Windows"' if "Windows" in user_agent else '"macOS"'
    
    return headers


def get_amazon_session_headers() -> Dict[str, str]:
    """
    Additional headers that make requests look like they're part of a browsing session
    """
    return {
        "DNT": "1",  # Do Not Track
        "Sec-GPC": "1",  # Global Privacy Control
    }

