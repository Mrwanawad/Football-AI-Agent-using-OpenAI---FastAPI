from datetime import datetime
from pydantic import BaseModel, Field


class AgentCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=128)
    prompt: str = Field(..., min_length=1)


class AgentUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=128)
    prompt: str | None = Field(None, min_length=1)


class AgentResponse(BaseModel):
    id: int
    name: str
    prompt: str
    owner_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}