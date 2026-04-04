import logging
import time
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.responses import JSONResponse

from app.config import settings
from app.health import check_openai_key, check_redis
from app.logging_ext import set_request_id, setup_logging
from app.rate_limit_redis import check_rate_limit
from app.security_ext import RefreshIn, decode_refresh_token, issue_token_pair

setup_logging(settings.log_level)
logger = logging.getLogger()

# very-light in-memory metrics
METRICS = {
    "requests_total": 0,
    "errors_total": 0,
    "chat_requests_total": 0,
    "last_request_ms": 0.0,
}


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging(settings.log_level)  # re-apply after server boot
    logger.info(
        "startup",
        extra={"event": "startup", "request_id": "", "status_code": 200, "duration_ms": 0},
    )
    yield
    logger.info(
        "shutdown",
        extra={"event": "shutdown", "request_id": "", "status_code": 200, "duration_ms": 0},
    )


app = FastAPI(title="ARIS API", version="2.6.0", lifespan=lifespan)


@app.middleware("http")
async def request_context_middleware(request: Request, call_next):
    rid = set_request_id(request.headers.get("x-request-id"))
    start = time.perf_counter()
    METRICS["requests_total"] += 1
    try:
        response = await call_next(request)
        duration_ms = round((time.perf_counter() - start) * 1000, 2)
        METRICS["last_request_ms"] = duration_ms
        response.headers["x-request-id"] = rid
        logger.info(
            "request_completed",
            extra={
                "event": "http_request",
                "request_id": rid,
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": duration_ms,
            },
        )
        return response
    except Exception:
        METRICS["errors_total"] += 1
        duration_ms = round((time.perf_counter() - start) * 1000, 2)
        logger.exception(
            "request_failed",
            extra={
                "event": "http_request_error",
                "request_id": rid,
                "method": request.method,
                "path": request.url.path,
                "status_code": 500,
                "duration_ms": duration_ms,
            },
        )
        raise


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    rid = set_request_id(request.headers.get("x-request-id"))
    METRICS["errors_total"] += 1
    logger.exception(
        "unhandled_exception",
        extra={
            "event": "unhandled_exception",
            "request_id": rid,
            "method": request.method,
            "path": request.url.path,
            "status_code": 500,
            "duration_ms": 0,
        },
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "internal server error", "x_request_id": rid},
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
    return JSONResponse(status_code=200 if ok else 503, content=payload)


@app.get("/metrics-lite")
def metrics_lite():
    return METRICS


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
def chat(body: dict, authorization: str | None = Header(default=None), x_request_id: str | None = Header(default=None)):
    rid = set_request_id(x_request_id)
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="missing bearer token")

    token = authorization.split(" ", 1)[1].strip()
    msg = body.get("message", "").strip()
    if not msg:
        raise HTTPException(status_code=400, detail="message required")

    if settings.rate_limit_enabled:
        allowed = check_rate_limit(key=f"chat:{token[:12]}", limit=settings.rate_limit_per_minute, window_sec=60)
        if not allowed:
            raise HTTPException(status_code=429, detail="rate limit exceeded")

    METRICS["chat_requests_total"] += 1
    logger.info(
        "chat_received",
        extra={
            "event": "chat_request",
            "request_id": rid,
            "method": "POST",
            "path": "/chat",
            "status_code": 200,
            "duration_ms": 0,
        },
    )
    return {"reply": f"echo: {msg}"}