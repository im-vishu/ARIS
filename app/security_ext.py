from datetime import datetime, timedelta, timezone

import jwt
from fastapi import HTTPException
from pydantic import BaseModel

from app.config import settings


class RefreshIn(BaseModel):
    refresh_token: str


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _encode(payload: dict) -> str:
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_alg)


def _decode(token: str) -> dict:
    try:
        return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_alg])
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="invalid token")


def issue_token_pair(username: str, role: str = "user") -> dict:
    now = _now()
    access_exp = now + timedelta(minutes=settings.access_token_expire_min)
    refresh_exp = now + timedelta(minutes=settings.refresh_token_expire_min)

    access_payload = {
        "sub": username,
        "role": role,
        "type": "access",
        "iat": int(now.timestamp()),
        "exp": int(access_exp.timestamp()),
    }
    refresh_payload = {
        "sub": username,
        "role": role,
        "type": "refresh",
        "iat": int(now.timestamp()),
        "exp": int(refresh_exp.timestamp()),
    }

    return {
        "access_token": _encode(access_payload),
        "refresh_token": _encode(refresh_payload),
        "token_type": "bearer",
        "expires_in": settings.access_token_expire_min * 60,
    }


def decode_access_token(token: str) -> dict:
    payload = _decode(token)
    if payload.get("type") != "access":
        raise HTTPException(status_code=401, detail="invalid access token")
    if not payload.get("sub"):
        raise HTTPException(status_code=401, detail="invalid access token")
    return payload


def decode_refresh_token(token: str) -> dict:
    payload = _decode(token)
    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="invalid refresh token")
    if not payload.get("sub"):
        raise HTTPException(status_code=401, detail="invalid refresh token")
    return payload