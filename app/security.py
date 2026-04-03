import os
import time
from collections import defaultdict, deque
from datetime import datetime, timedelta, timezone
from typing import Dict, Deque, Optional

import jwt
from fastapi import Header, HTTPException, Request, status

JWT_SECRET = os.getenv("ARIS_JWT_SECRET", "change-me-in-prod")
JWT_ALG = os.getenv("ARIS_JWT_ALG", "HS256")
JWT_EXPIRE_MIN = int(os.getenv("ARIS_JWT_EXPIRE_MIN", "60"))

RATE_LIMIT_REQUESTS = int(os.getenv("ARIS_RATE_LIMIT_REQUESTS", "30"))
RATE_LIMIT_WINDOW_SEC = int(os.getenv("ARIS_RATE_LIMIT_WINDOW_SEC", "60"))

# in-memory rate store (good for single-instance; use Redis for multi-instance)
_rate_store: Dict[str, Deque[float]] = defaultdict(deque)


def create_access_token(subject: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": subject,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=JWT_EXPIRE_MIN)).timestamp()),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)


def verify_token(authorization: Optional[str] = Header(default=None)) -> dict:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Authorization header",
        )

    token = authorization.split(" ", 1)[1].strip()
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


def enforce_rate_limit(request: Request) -> None:
    client_ip = request.client.host if request.client else "unknown"
    now = time.time()
    q = _rate_store[client_ip]

    # remove old hits outside window
    cutoff = now - RATE_LIMIT_WINDOW_SEC
    while q and q[0] < cutoff:
        q.popleft()

    if len(q) >= RATE_LIMIT_REQUESTS:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded: max {RATE_LIMIT_REQUESTS}/{RATE_LIMIT_WINDOW_SEC}s",
        )

    q.append(now)