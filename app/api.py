import logging

from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from openai import (
    RateLimitError,
    AuthenticationError,
    APITimeoutError,
    APIConnectionError,
    APIError,
)

from app.logging_middleware import install_request_logging


from app.agent import handle_user_message
from app.security import verify_token
from app.security_ext import (
    issue_token_pair,
    RefreshIn,
    decode_refresh_token,
    create_access_token,
)
from app.rate_limit_redis import check_rate_limit
from app.errors import install_error_handlers

app = FastAPI()
install_error_handlers(app)
install_request_logging(app)

logger = logging.getLogger("aris.api")


class ChatIn(BaseModel):
    message: str


class TokenIn(BaseModel):
    username: str
    role: str = "user"


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/auth/token")
def auth_token(payload: TokenIn):
    return issue_token_pair(payload.username, payload.role)


@app.post("/auth/refresh")
def auth_refresh(payload: RefreshIn):
    try:
        claims = decode_refresh_token(payload.refresh_token)
        username = claims.get("sub")
        role = claims.get("role", "user")
        scopes = claims.get("scopes", ["chat:write"])
        access_token = create_access_token(username=username, role=role, scopes=scopes)
        return {"access_token": access_token}
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token.")


@app.post("/chat")
def chat(
    payload: ChatIn,
    claims: dict = Depends(verify_token),
):
    user_key = claims.get("sub", "anonymous")
    allowed = check_rate_limit(f"chat:{user_key}", limit=20, window_sec=60)
    if not allowed:
        raise HTTPException(status_code=429, detail="Rate limit exceeded. Try again later.")

    try:
        return handle_user_message(payload.message)

    except RateLimitError:
        raise HTTPException(status_code=429, detail="OpenAI quota exceeded. Please check billing/limits.")
    except AuthenticationError:
        raise HTTPException(status_code=401, detail="OpenAI authentication failed. Check OPENAI_API_KEY.")
    except APITimeoutError:
        raise HTTPException(status_code=504, detail="LLM upstream timeout.")
    except APIConnectionError:
        raise HTTPException(status_code=503, detail="LLM upstream connection error.")
    except APIError:
        raise HTTPException(status_code=502, detail="LLM upstream API error.")
    except Exception as e:
        logger.exception("Unhandled /chat error: %s", e)
        raise HTTPException(status_code=500, detail="Internal server error")