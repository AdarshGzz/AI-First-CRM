"""
Redis-backed fixed-window rate limiter (Upstash REST).
Sits between the WebSocket router and agent_service — checked before
the agent is invoked so every Groq call is covered by a single gate.
"""

from app.cache.redis_client import get_redis
from app.core.config import settings
import time


def check_rate_limit() -> tuple[bool, int]:
    """
    Check if the current request is within the rate limit.
    
    Returns:
        (allowed, retry_after_seconds)
        - allowed=True: proceed with the request
        - allowed=False: rate limited, wait retry_after_seconds
    """
    r = get_redis()

    # Fixed-window key based on current minute bucket
    window = settings.rate_limit_window_seconds
    current_bucket = int(time.time()) // window
    key = f"rate:groq:{current_bucket}"

    # Atomic increment
    count = r.incr(key)

    # Set expiry on first increment only
    if count == 1:
        r.expire(key, window)

    if count > settings.rate_limit_max_requests:
        # Calculate how many seconds remain in this window
        ttl = r.ttl(key)
        retry_after = max(ttl, 1)
        return False, retry_after

    return True, 0
