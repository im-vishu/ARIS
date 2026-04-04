from datetime import datetime, timedelta, timezone
from typing import Any
import os

import jwt
from pydantic import BaseModel

JWT_SECRET = os.getenv("JWT_SECRET", "change-me")
JWT_ALG = os.getenv("JWT_ALG", "HS256")
ACCESS_TTL_MIN = int(os.getenv("ACCESS_TTL_MIN", "30"))
REFRESH_TTL_DAYS = int(os.getenv("REFRESH_TTL_DAYS", "7"))


class RefreshIn(BaseModel):
    refresh_token: str


def _now() -> datetime:
    return datetime.now(timezone.utc)


def create_access_token(username: str, role: str = "user", scopes: list[str] | None = None) -> str:
    if scopes is None:
        scopes = ["chat:write"]
    now = _now()
    payload: dict[str, Any] = {
        "sub": username,
        "role": role,
        "scopes": scopes,
        "type": "access",
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=ACCESS_TTL_MIN)).timestamp()),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)


def create_refresh_token(username: str, role: str = "user", scopes: list[str] | None = None) -> str:
    if scopes is None:
        scopes = ["chat:write"]
    now = _now()
    payload: dict[str, Any] = {
        "sub": username,
        "role": role,
        "scopes": scopes,
        "type": "refresh",
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(days=REFRESH_TTL_DAYS)).timestamp()),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)


def issue_token_pair(username: str, role: str = "user") -> dict[str, str]:
    return {
        "access_token": create_access_token(username, role),
        "refresh_token": create_refresh_token(username, role),
        "token_type": "bearer",
    }


def decode_refresh_token(token: str) -> dict[str, Any]:
    payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
    if payload.get("type") != "refresh":
        raise ValueError("Invalid token type")
    return payload