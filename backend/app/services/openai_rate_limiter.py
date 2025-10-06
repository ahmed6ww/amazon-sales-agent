import asyncio
import time
import random
import logging
import threading
from typing import Dict, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class RateLimitConfig:
    """Configuration for rate limiting"""
    requests_per_minute: int = 15  # Conservative limit
    requests_per_second: int = 2    # Conservative limit
    max_retries: int = 3
    base_retry_delay: float = 1.0
    max_retry_delay: float = 30.0
    jitter_range: float = 0.5

class OpenAIRateLimiter:
    """Advanced rate limiter for OpenAI API requests with exponential backoff"""
    
    def __init__(self, config: RateLimitConfig = None):
        self.config = config or RateLimitConfig()
        self.request_times = []
        self.last_request_time = 0
        self.lock = threading.Lock()  # Use thread-safe lock instead of asyncio
        self.retry_counts = {}  # Track retries per request type
    
    async def wait_for_rate_limit(self):
        """Wait if necessary to respect rate limits"""
        # Use thread-safe approach for rate limiting
        with self.lock:
            now = time.time()
            
            # Clean old requests (older than 1 minute)
            self.request_times = [t for t in self.request_times if now - t < 60]
            
            # Check per-minute limit
            if len(self.request_times) >= self.config.requests_per_minute:
                wait_time = 60 - (now - self.request_times[0])
                if wait_time > 0:
                    logger.info(f"Rate limit: Waiting {wait_time:.1f}s for per-minute limit")
                    await asyncio.sleep(wait_time)
                    now = time.time()
            
            # Check per-second limit
            time_since_last = now - self.last_request_time
            if time_since_last < (1.0 / self.config.requests_per_second):
                wait_time = (1.0 / self.config.requests_per_second) - time_since_last
                logger.info(f"Rate limit: Waiting {wait_time:.1f}s for per-second limit")
                await asyncio.sleep(wait_time)
                now = time.time()
            
            # Record this request
            self.request_times.append(now)
            self.last_request_time = now
    
    async def wait_with_exponential_backoff(self, request_id: str, attempt: int):
        """Wait with exponential backoff for retries"""
        if attempt == 0:
            return
        
        # Track retry count for this request
        with self.lock:
            if request_id not in self.retry_counts:
                self.retry_counts[request_id] = 0
            self.retry_counts[request_id] += 1
        
        # Exponential backoff with jitter
        delay = self.config.base_retry_delay * (2 ** attempt)
        jitter = random.uniform(-self.config.jitter_range, self.config.jitter_range)
        delay = max(0, delay + jitter)
        
        # Cap at max delay
        delay = min(delay, self.config.max_retry_delay)
        
        logger.warning(f"Exponential backoff: Waiting {delay:.1f}s before retry {attempt} for {request_id}")
        await asyncio.sleep(delay)
    
    def should_retry(self, request_id: str) -> bool:
        """Check if we should retry based on retry count"""
        with self.lock:
            retry_count = self.retry_counts.get(request_id, 0)
            return retry_count < self.config.max_retries
    
    def reset_retry_count(self, request_id: str):
        """Reset retry count for successful request"""
        with self.lock:
            if request_id in self.retry_counts:
                del self.retry_counts[request_id]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get rate limiter statistics"""
        with self.lock:
            now = time.time()
            recent_requests = [t for t in self.request_times if now - t < 60]
            return {
                "requests_last_minute": len(recent_requests),
                "max_requests_per_minute": self.config.requests_per_minute,
                "active_retries": len(self.retry_counts),
                "total_retry_attempts": sum(self.retry_counts.values())
            }

# Global rate limiter instance
rate_limiter = OpenAIRateLimiter()