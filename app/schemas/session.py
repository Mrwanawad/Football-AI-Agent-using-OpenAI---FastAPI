from datetime import datetime
from pydantic import BaseModel, Field
from app.models.message import MessageRole


class SessionCreate(BaseModel):
    title: str = Field(default="New Session", max_length=255)


class SessionResponse(BaseModel):
    id: int
    title: str
    agent_id: int
    user_id: int
    created_at: datetime

    model_config = {"from_attributes": True}


class MessageCreate(BaseModel):
    content: str = Field(..., min_length=1)


class MessageResponse(BaseModel):
    id: int
    session_id: int
    role: MessageRole
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ChatResponse(BaseModel):
    user_message: MessageResponse
    agent_message: MessageResponse


class SessionWithMessages(SessionResponse):
    messages: list[MessageResponse] = []