"""
NFM-X V4 Rate Limiting Middleware
Optional rate limiting for API endpoints
"""

from typing import Callable, Awaitable, Optional, List
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
import time
import logging
from collections import defaultdict

from backend.app.config import get_config

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Token bucket rate limiter
    """
    
    def __init__(self, requests_per_minute: int, burst_requests: int):
        self.requests_per_minute = requests_per_minute
        self.burst_requests = burst_requests
        self.buckets: dict = defaultdict(lambda: {"tokens": burst_requests, "last_refill": time.time()})
        self.whitelist: set = set()
    
    def add_to_whitelist(self, ip: str) -> None:
        """Add IP to whitelist"""
        self.whitelist.add(ip)
    
    def remove_from_whitelist(self, ip: str) -> None:
        """Remove IP from whitelist"""
        self.whitelist.discard(ip)
    
    def is_whitelisted(self, ip: str) -> bool:
        """Check if IP is whitelisted"""
        return ip in self.whitelist
    
    def allow_request(self, ip: str) -> bool:
        """
        Check if a request from the given IP should be allowed
        Uses token bucket algorithm
        """
        if self.is_whitelisted(ip):
            return True
        
        bucket = self.buckets[ip]
        current_time = time.time()
        
        # Refill tokens based on time elapsed
        time_elapsed = current_time - bucket["last_refill"]
        tokens_to_add = time_elapsed * (self.requests_per_minute / 60)
        
        bucket["tokens"] = min(self.burst_requests, bucket["tokens"] + tokens_to_add)
        bucket["last_refill"] = current_time
        
        # Check if we have tokens available
        if bucket["tokens"] >= 1:
            bucket["tokens"] -= 1
            return True
        
        return False
    
    def get_remaining_requests(self, ip: str) -> int:
        """Get remaining requests for an IP"""
        if self.is_whitelisted(ip):
            return float("inf")
        
        bucket = self.buckets[ip]
        current_time = time.time()
        
        # Refill tokens based on time elapsed
        time_elapsed = current_time - bucket["last_refill"]
        tokens_to_add = time_elapsed * (self.requests_per_minute / 60)
        
        current_tokens = min(self.burst_requests, bucket["tokens"] + tokens_to_add)
        return int(current_tokens)
    
    def reset(self, ip: Optional[str] = None) -> None:
        """Reset rate limit counters"""
        if ip:
            self.buckets[ip] = {"tokens": self.burst_requests, "last_refill": time.time()}
        else:
            for ip_address in self.buckets:
                self.buckets[ip_address] = {"tokens": self.burst_requests, "last_refill": time.time()}


# Global rate limiter instance
rate_limiter: Optional[RateLimiter] = None


def init_rate_limiter() -> Optional[RateLimiter]:
    """
    Initialize rate limiter from configuration
    """
    global rate_limiter
    config = get_config()
    
    if not config.rate_limit.enabled:
        logger.info("Rate limiting is disabled")
        return None
    
    rate_limiter = RateLimiter(
        requests_per_minute=config.rate_limit.requests_per_minute,
        burst_requests=config.rate_limit.burst_requests
    )
    
    # Add whitelisted IPs
    for ip in config.rate_limit.whitelist:
        rate_limiter.add_to_whitelist(ip)
    
    logger.info(f"Rate limiting enabled: {config.rate_limit.requests_per_minute} req/min, burst: {config.rate_limit.burst_requests}")
    return rate_limiter


def get_client_ip(request: Request) -> str:
    """
    Get client IP address from request
    """
    # Try to get IP from X-Forwarded-For header (for proxies)
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        # X-Forwarded-For can contain multiple IPs, take the first one
        return forwarded_for.split(",")[0].strip()
    
    # Try X-Real-IP
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip.strip()
    
    # Fall back to client host
    return request.client.host


def rate_limit_middleware(request: Request, call_next: Callable[[Request], Awaitable]) -> Awaitable:
    """
    FastAPI middleware for rate limiting
    """
    global rate_limiter
    
    # Initialize rate limiter if not already done
    if rate_limiter is None:
        rate_limiter = init_rate_limiter()
    
    # If rate limiting is disabled, just pass through
    if rate_limiter is None:
        return call_next(request)
    
    # Get client IP
    client_ip = get_client_ip(request)
    
    # Check rate limit
    if not rate_limiter.allow_request(client_ip):
        remaining = rate_limiter.get_remaining_requests(client_ip)
        logger.warning(f"Rate limit exceeded for IP: {client_ip}")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "error": "Too many requests",
                "message": "Rate limit exceeded",
                "retry_after": 60,
                "remaining_requests": remaining
            }
        )
    
    # Add rate limit headers to response
    response = await call_next(request)
    remaining = rate_limiter.get_remaining_requests(client_ip)
    
    # Add headers to response
    response.headers["X-RateLimit-Limit"] = str(rate_limiter.requests_per_minute)
    response.headers["X-RateLimit-Remaining"] = str(remaining)
    response.headers["X-RateLimit-Reset"] = str(int(time.time() + 60))
    
    return response


def get_rate_limiter() -> Optional[RateLimiter]:
    """Get the rate limiter instance"""
    global rate_limiter
    if rate_limiter is None:
        rate_limiter = init_rate_limiter()
    return rate_limiter