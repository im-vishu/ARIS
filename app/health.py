import os
from typing import Tuple

import redis


def check_redis() -> Tuple[bool, str]:
    url = os.getenv("REDIS_URL", "redis://redis:6379/0")
    try:
        client = redis.Redis.from_url(url, decode_responses=True, socket_connect_timeout=1, socket_timeout=1)
        client.ping()
        return True, "ok"
    except Exception as e:
        return False, f"redis_error: {e.__class__.__name__}"


def check_openai_key() -> Tuple[bool, str]:
    key = os.getenv("OPENAI_API_KEY", "").strip()
    if not key:
        return False, "missing"
    if not key.startswith("sk-"):
        return False, "invalid_format"
    return True, "ok"