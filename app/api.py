import logging
import time
from contextlib import asynccontextmanager
from typing import Any

from fastapi import Depends, FastAPI, Header, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse, Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from sqlalchemy.orm import Session
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR

from app.config import settings
from app.db import Base, engine, get_db
from app.errors import ApiError, error_payload, success
from app.health import check_openai_key, check_redis
from app.logging_ext import set_request_id, setup_logging
from app.models import ChatMessage
from app.rate_limit_redis import check_rate_limit
from app.schemas import ChatHistoryOut
from app.security_ext import RefreshIn, decode_access_token, decode_refresh_token, issue_token_pair
from app.token_store import is_refresh_used, is_token_revoked, mark_refresh_used, revoke_token_jti

setup_logging(settings.log_level)
logger = logging.getLogger(__name__)

METRICS = {"requests_total": 0, "errors_total": 0, "chat_requests_total": 0, "last_request_ms": 0.0}
REQ_COUNTER = Counter("aris_http_requests_total", "Total HTTP requests", ["method", "path", "status"])
ERR_COUNTER = Counter("aris_http_errors_total", "Total HTTP error responses", ["path", "status"])
LATENCY = Histogram("aris_http_request_duration_seconds", "Request latency", ["method", "path"])


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging(settings.log_level)
    Base.metadata.create_all(bind=engine)
    logger.info("startup", extra={"event": "startup", "request_id": "", "status_code": 200, "duration_ms": 0})
    yield
    logger.info("shutdown", extra={"event": "shutdown", "request_id": "", "status_code": 200, "duration_ms": 0})


app = FastAPI(title="ARIS API", version="5.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.allowed_hosts)


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

        path = request.url.path
        status_code = response.status_code
        REQ_COUNTER.labels(method=request.method, path=path, status=str(status_code)).inc()
        LATENCY.labels(method=request.method, path=path).observe(duration_ms / 1000)

        if status_code >= 400:
            METRICS["errors_total"] += 1
            ERR_COUNTER.labels(path=path, status=str(status_code)).inc()

        return response
    except Exception:
        METRICS["errors_total"] += 1
        duration_ms = round((time.perf_counter() - start) * 1000, 2)
        path = request.url.path
        ERR_COUNTER.labels(path=path, status="500").inc()
        REQ_COUNTER.labels(method=request.method, path=path, status="500").inc()
        LATENCY.labels(method=request.method, path=path).observe(duration_ms / 1000)
        logger.exception("request_failed", extra={"request_id": rid, "path": path, "status_code": 500, "duration_ms": duration_ms})
        raise


@app.exception_handler(ApiError)
async def api_error_handler(request: Request, exc: ApiError):
    rid = set_request_id(request.headers.get("x-request-id"))
    return JSONResponse(status_code=exc.status_code, content=error_payload(exc.code, exc.message, rid, exc.details))


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    rid = set_request_id(request.headers.get("x-request-id"))
    code_map = {400: "bad_request", 401: "unauthorized", 403: "forbidden", 404: "not_found", 409: "conflict", 429: "rate_limited", 503: "service_unavailable"}
    err_code = code_map.get(exc.status_code, "internal_error")
    message = exc.detail if isinstance(exc.detail, str) else "request failed"
    return JSONResponse(status_code=exc.status_code, content=error_payload(err_code, message, rid))


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    rid = set_request_id(request.headers.get("x-request-id"))
    return JSONResponse(status_code=400, content=error_payload("bad_request", "validation failed", rid, {"errors": exc.errors()}))


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    rid = set_request_id(request.headers.get("x-request-id"))
    return JSONResponse(status_code=HTTP_500_INTERNAL_SERVER_ERROR, content=error_payload("internal_error", "internal server error", rid))


def _ready_payload() -> tuple[bool, dict[str, Any]]:
    redis_ok, redis_detail = check_redis()
    openai_ok, openai_detail = check_openai_key()
    ok = redis_ok and openai_ok
    return ok, {
        "status": "ready" if ok else "not_ready",
        "checks": {"redis": {"ok": redis_ok, "detail": redis_detail}, "openai_key": {"ok": openai_ok, "detail": openai_detail}},
        "env": settings.app_env,
    }


@app.get("/v1/health")
def v1_health(request: Request):
    rid = set_request_id(request.headers.get("x-request-id"))
    return success({"status": "ok"}, rid)


@app.get("/v1/ready")
def v1_ready(request: Request):
    rid = set_request_id(request.headers.get("x-request-id"))
    ok, payload = _ready_payload()
    if not ok:
        raise HTTPException(status_code=503, detail="service not ready")
    return success(payload, rid)


@app.get("/v1/metrics-lite")
def v1_metrics_lite(request: Request):
    rid = set_request_id(request.headers.get("x-request-id"))
    return success(METRICS, rid)


@app.get("/v1/metrics")
def v1_metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.post("/v1/auth/token")
def v1_auth_token(body: dict, request: Request):
    rid = set_request_id(request.headers.get("x-request-id"))
    username = body.get("username")
    role = body.get("role", "user")
    if not username:
        raise HTTPException(status_code=400, detail="username required")
    return success(issue_token_pair(username=username, role=role), rid)


@app.post("/v1/auth/refresh")
def v1_auth_refresh(body: RefreshIn, request: Request):
    rid = set_request_id(request.headers.get("x-request-id"))
    payload = decode_refresh_token(body.refresh_token)
    jti = payload["jti"]
    exp = payload["exp"]

    if is_token_revoked(jti):
        raise HTTPException(status_code=401, detail="refresh token revoked")
    if is_refresh_used(jti):
        raise HTTPException(status_code=401, detail="refresh token already used")

    mark_refresh_used(jti, exp)
    revoke_token_jti(jti, exp)
    return success(issue_token_pair(username=payload["sub"], role=payload.get("role", "user")), rid)


@app.post("/v1/auth/logout")
def v1_auth_logout(body: RefreshIn, request: Request):
    rid = set_request_id(request.headers.get("x-request-id"))
    payload = decode_refresh_token(body.refresh_token)
    revoke_token_jti(payload["jti"], payload["exp"])
    return success({"ok": True}, rid)


@app.post("/v1/chat")
def v1_chat(
    body: dict,
    request: Request,
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    rid = set_request_id(request.headers.get("x-request-id"))

    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="missing bearer token")

    token = authorization.split(" ", 1)[1].strip()
    if not token:
        raise HTTPException(status_code=401, detail="invalid bearer token")

    claims = decode_access_token(token)
    if is_token_revoked(claims["jti"]):
        raise HTTPException(status_code=401, detail="access token revoked")

    username = claims["sub"]
    role = claims.get("role", "user")

    msg = body.get("message", "").strip()
    if not msg:
        raise HTTPException(status_code=400, detail="message required")

    if settings.rate_limit_enabled:
        allowed = check_rate_limit(key=f"chat:{username}", limit=settings.rate_limit_per_minute, window_sec=60)
        if not allowed:
            raise HTTPException(status_code=429, detail="rate limit exceeded")

    reply = f"echo: {msg}"
    row = ChatMessage(username=username, role=role, message=msg, reply=reply)
    db.add(row)
    db.commit()
    db.refresh(row)

    METRICS["chat_requests_total"] += 1
    return success({"reply": reply, "message_id": row.id}, rid)


@app.get("/v1/chat/history")
def v1_chat_history(
    request: Request,
    limit: int = 20,
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    rid = set_request_id(request.headers.get("x-request-id"))

    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="missing bearer token")

    token = authorization.split(" ", 1)[1].strip()
    claims = decode_access_token(token)
    if is_token_revoked(claims["jti"]):
        raise HTTPException(status_code=401, detail="access token revoked")

    username = claims["sub"]
    role = claims.get("role", "user")

    limit = max(1, min(limit, 100))
    q = db.query(ChatMessage).order_by(ChatMessage.id.desc())
    if role != "admin":
        q = q.filter(ChatMessage.username == username)

    rows = q.limit(limit).all()
    data = [ChatHistoryOut.model_validate(r).model_dump() for r in rows]
    return success(data, rid)