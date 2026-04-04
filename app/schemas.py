from datetime import datetime

from pydantic import BaseModel


class ChatHistoryOut(BaseModel):
    id: int
    username: str
    role: str
    message: str
    reply: str
    created_at: datetime

    class Config:
        from_attributes = True