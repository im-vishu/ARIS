from fastapi import FastAPI
from pydantic import BaseModel
from app.agent import handle_user_message

app = FastAPI(title="ARIS API", version="2.2")

class ChatIn(BaseModel):
    message: str

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/chat")
def chat(body: ChatIn):
    result = handle_user_message(body.message)
    return result