import os
import time
import redis

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)


def check_rate_limit(key: str, limit: int = 20, window_sec: int = 60) -> bool:
    """
    Fixed-window rate limit.
    Returns True if request allowed, False if exceeded.
    """
    now = int(time.time())
    window = now // window_sec
    redis_key = f"rl:{key}:{window}"

    try:
        count = _client.incr(redis_key)
        if count == 1:
            _client.expire(redis_key, window_sec)
        return count <= limit
    except Exception:
        # fail-open so API still works if Redis is temporarily unavailable
        return True