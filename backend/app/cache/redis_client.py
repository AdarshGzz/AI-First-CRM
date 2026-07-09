"""
Redis client using Upstash REST API.
Used for rate limiting and HCP profile caching.
"""

from upstash_redis import Redis
from app.core.config import settings

# Global Redis client (Upstash REST — synchronous but lightweight HTTP calls)
_redis_client: Redis | None = None


def get_redis() -> Redis:
    """Get or create the Upstash Redis client."""
    global _redis_client
    if _redis_client is None:
        _redis_client = Redis(
            url=settings.redis_url,
            token=settings.upstash_redis_rest_token,
        )
    return _redis_client


def close_redis():
    """Reset Redis client on shutdown."""
    global _redis_client
    _redis_client = None


def get_cache(key: str) -> str | None:
    """Get a cached value by key."""
    r = get_redis()
    return r.get(key)


def set_cache(key: str, value: str, expire_seconds: int = 300):
    """Set a cached value with optional TTL (default 5 min)."""
    r = get_redis()
    r.set(key, value, ex=expire_seconds)


def delete_cache(key: str):
    """Delete a cached key."""
    r = get_redis()
    r.delete(key)
