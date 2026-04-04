import json
import logging
import os
import time
import uuid
from typing import Any

from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.responses import JSONResponse

from app.config import settings
from app.health import check_openai_key, check_redis
from app.rate_limit_redis import check_rate_limit
from app.security_ext import RefreshIn, decode_refresh_token, issue_token_pair

app = FastAPI(title="ARIS API", version="2.4.2")

logger = logging.getLogger("aris.api")
logging.basicConfig(level=getattr(logging, settings.log_level.upper(), logging.INFO))


@app.middleware("http")
async def request_context_middleware(request: Request, call_next):
    request_id = request.headers.get("x-request-id", str(uuid.uuid4()))
    start = time.perf_counter()
    try:
        response = await call_next(request)
    except Exception:
        duration_ms = round((time.perf_counter() - start) * 1000, 2)
        log = {
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "status_code": 500,
            "duration_ms": duration_ms,
        }
        logger.exception(json.dumps(log))
        raise

    duration_ms = round((time.perf_counter() - start) * 1000, 2)
    response.headers["x-request-id"] = request_id
    log = {
        "request_id": request_id,
        "method": request.method,
        "path": request.url.path,
        "status_code": response.status_code,
        "duration_ms": duration_ms,
    }
    logger.info(json.dumps(log))
    return response


@app.on_event("startup")
async def startup_checks():
    logger.info(
        json.dumps(
            {
                "event": "startup",
                "app_env": settings.app_env,
                "log_level": settings.log_level,
                "rate_limit_enabled": settings.rate_limit_enabled,
                "rate_limit_per_minute": settings.rate_limit_per_minute,
            }
        )
    )


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/ready")
def ready():
    redis_ok, redis_detail = check_redis()
    openai_ok, openai_detail = check_openai_key()

    ok = redis_ok and openai_ok
    payload: dict[str, Any] = {
        "status": "ready" if ok else "not_ready",
        "checks": {
            "redis": {"ok": redis_ok, "detail": redis_detail},
            "openai_key": {"ok": openai_ok, "detail": openai_detail},
        },
        "env": settings.app_env,
    }
    code = 200 if ok else 503
    return JSONResponse(status_code=code, content=payload)


@app.post("/auth/token")
def auth_token(body: dict):
    username = body.get("username")
    role = body.get("role", "user")
    if not username:
        raise HTTPException(status_code=400, detail="username required")
    return issue_token_pair(username=username, role=role)


@app.post("/auth/refresh")
def auth_refresh(body: RefreshIn):
    payload = decode_refresh_token(body.refresh_token)
    username = payload.get("sub")
    role = payload.get("role", "user")
    if not username:
        raise HTTPException(status_code=401, detail="invalid refresh token")
    return issue_token_pair(username=username, role=role)


@app.post("/chat")
def chat(body: dict, authorization: str | None = Header(default=None)):
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="missing bearer token")

    token = authorization.split(" ", 1)[1].strip()
    if not token:
        raise HTTPException(status_code=401, detail="invalid bearer token")

    msg = body.get("message", "").strip()
    if not msg:
        raise HTTPException(status_code=400, detail="message required")

    if settings.rate_limit_enabled:
        allowed = check_rate_limit(key=f"chat:{token[:12]}", limit=settings.rate_limit_per_minute, window_sec=60)
        if not allowed:
            raise HTTPException(status_code=429, detail="rate limit exceeded")

    # placeholder response for ops phase
    return {"reply": f"echo: {msg}"}