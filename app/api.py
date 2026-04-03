from fastapi import Depends, FastAPI, Request
from pydantic import BaseModel

from app.agent import handle_user_message
from app.logging_config import setup_logging
from app.security import create_access_token, enforce_rate_limit, verify_token

import logging

setup_logging()
logger = logging.getLogger("aris.api")

app = FastAPI(title="ARIS API", version="2.2.1")


class ChatIn(BaseModel):
    message: str


class TokenIn(BaseModel):
    username: str


@app.get("/health")
def health():
    return {"ok": True}


@app.post("/auth/token")
def issue_token(body: TokenIn):
    token = create_access_token(body.username)
    return {"access_token": token, "token_type": "bearer"}


@app.post("/chat")
def chat(
    body: ChatIn,
    request: Request,
    _auth=Depends(verify_token),
):
    enforce_rate_limit(request)

    logger.info(
        "chat_request",
        extra={
            "extra_data": {
                "path": "/chat",
                "client_ip": request.client.host if request.client else "unknown",
                "message_len": len(body.message),
            }
        },
    )

    result = handle_user_message(body.message)

    logger.info(
        "chat_response",
        extra={
            "extra_data": {
                "path": "/chat",
                "client_ip": request.client.host if request.client else "unknown",
                "status": "ok",
            }
        },
    )
    return result