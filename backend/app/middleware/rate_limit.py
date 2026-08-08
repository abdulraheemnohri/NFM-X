"""
NFM-X Rate Limiting Middleware
Redis-based rate limiting for distributed environments
"""

from fastapi import Request, HTTPException, status
from typing import Optional
import logging
from datetime import datetime, timezone
import os

from backend.app.config import settings

logger = logging.getLogger(__name__)


class RateLimiter:
    """Rate limiter with Redis support for distributed environments"""
    
    def __init__(self):
        rate_limit_config = getattr(settings, 'rate_limit', None)
        if hasattr(rate_limit_config, 'model_dump'):
            # It is a Pydantic model
            rate_limit_dict = rate_limit_config.model_dump()
        elif isinstance(rate_limit_config, dict):
            rate_limit_dict = rate_limit_config
        else:
            rate_limit_dict = {}

        self.enabled = rate_limit_dict.get('enabled', False)
        self.requests_per_minute = rate_limit_dict.get('requests_per_minute', 100)
        self.burst_requests = rate_limit_dict.get('burst_requests', 10)
        self.whitelist = set(rate_limit_dict.get('whitelist', []))
        
        # Try to use Redis if available
        self.redis_client = None
        try:
            import redis
            redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
            self.redis_client = redis.from_url(redis_url, decode_responses=True)
            self.redis_client.ping()
            logger.info("Using Redis for rate limiting")
        except Exception as e:
            logger.warning(f"Redis not available: {e}, using in-memory rate limiting")
            self.memory_store = {}
    
    async def check_rate_limit(self, client_ip: str, endpoint: str) -> bool:
        """Check if the client has exceeded rate limits"""
        if not self.enabled:
            return True
        
        if client_ip in self.whitelist:
            return True
        
        key = f"rate_limit:{client_ip}:{endpoint}"
        
        if self.redis_client:
            return await self._check_redis_rate_limit(key)
        else:
            return self._check_memory_rate_limit(key)
    
    async def _check_redis_rate_limit(self, key: str) -> bool:
        """Check rate limit using Redis"""
        try:
            current = await self.redis_client.get(key)
            if current and int(current) >= self.requests_per_minute:
                return False
            
            pipe = self.redis_client.pipeline()
            pipe.incr(key)
            pipe.expire(key, 60)  # 1 minute window
            await pipe.execute()
            return True
        except Exception as e:
            logger.error(f"Redis rate limit check failed: {e}")
            return True  # Fail open
    
    def _check_memory_rate_limit(self, key: str) -> bool:
        """Check rate limit using in-memory store (per-worker)"""
        now = datetime.now(timezone.utc).timestamp()
        window_start = now - 60  # 1 minute window
        
        if key not in self.memory_store:
            self.memory_store[key] = []
        
        # Remove old requests
        self.memory_store[key] = [
            t for t in self.memory_store[key] 
            if t > window_start
        ]
        
        # Check if limit exceeded
        if len(self.memory_store[key]) >= self.requests_per_minute:
            return False
        
        # Add current request
        self.memory_store[key].append(now)
        return True
    
    async def get_remaining_requests(self, client_ip: str, endpoint: str) -> int:
        """Get remaining requests for a client"""
        if not self.enabled:
            return float('inf')
        
        if client_ip in self.whitelist:
            return float('inf')
        
        key = f"rate_limit:{client_ip}:{endpoint}"
        
        if self.redis_client:
            try:
                current = await self.redis_client.get(key)
                return max(0, self.requests_per_minute - (int(current) if current else 0))
            except Exception:
                return self.requests_per_minute
        else:
            if key in self.memory_store:
                return max(0, self.requests_per_minute - len(self.memory_store[key]))
            return self.requests_per_minute


# Global rate limiter instance
rate_limiter = RateLimiter()


def init_rate_limiter():
    """Initialize or reset the global rate limiter."""
    global rate_limiter
    rate_limiter = RateLimiter()
    return rate_limiter


def get_rate_limiter():
    """Retrieve the global rate limiter."""
    return rate_limiter


async def rate_limit_middleware(request: Request, call_next):
    """Rate limiting middleware for FastAPI"""
    if not rate_limiter.enabled:
        return await call_next(request)
    
    client_ip = request.client.host if request.client else "unknown"
    endpoint = request.url.path
    
    if not await rate_limiter.check_rate_limit(client_ip, endpoint):
        remaining = await rate_limiter.get_remaining_requests(client_ip, endpoint)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "error": "Rate limit exceeded",
                "message": f"You have exceeded the rate limit of {rate_limiter.requests_per_minute} requests per minute",
                "retry_after": 60,
                "limit": rate_limiter.requests_per_minute,
                "remaining": 0
            }
        )
    
    response = await call_next(request)
    remaining = await rate_limiter.get_remaining_requests(client_ip, endpoint)
    
    # Add rate limit headers
    response.headers["X-RateLimit-Limit"] = str(rate_limiter.requests_per_minute)
    response.headers["X-RateLimit-Remaining"] = str(remaining)
    response.headers["X-RateLimit-Reset"] = str(int(datetime.now(timezone.utc).timestamp()) + 60)
    
    return response