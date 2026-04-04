from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ChatHistoryOut(BaseModel):
    id: int
    username: str
    role: str
    message: str
    reply: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)