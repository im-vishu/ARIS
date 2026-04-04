from datetime import datetime, timezone

from app.config import settings

# In-memory fallback for tests/dev when redis is unavailable
_REVOKED = set()
_USED_REFRESH = set()


def _exp_to_ttl(exp: int) -> int:
    now = int(datetime.now(timezone.utc).timestamp())
    ttl = exp - now
    return ttl if ttl > 0 else 1


def _redis_client():
    try:
        import redis  # lazy import
        return redis.from_url(settings.redis_url, decode_responses=True)
    except Exception:
        return None


def revoke_token_jti(jti: str, exp: int) -> None:
    r = _redis_client()
    if r is None:
        _REVOKED.add(jti)
        return
    try:
        r.setex(f"revoked:{jti}", _exp_to_ttl(exp), "1")
    except Exception:
        _REVOKED.add(jti)


def is_token_revoked(jti: str) -> bool:
    r = _redis_client()
    if r is None:
        return jti in _REVOKED
    try:
        return bool(r.get(f"revoked:{jti}"))
    except Exception:
        return jti in _REVOKED


def mark_refresh_used(jti: str, exp: int) -> None:
    r = _redis_client()
    if r is None:
        _USED_REFRESH.add(jti)
        return
    try:
        r.setex(f"used_refresh:{jti}", _exp_to_ttl(exp), "1")
    except Exception:
        _USED_REFRESH.add(jti)


def is_refresh_used(jti: str) -> bool:
    r = _redis_client()
    if r is None:
        return jti in _USED_REFRESH
    try:
        return bool(r.get(f"used_refresh:{jti}"))
    except Exception:
        return jti in _USED_REFRESH