import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.db import TicketStatus


class TicketCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str = ""
    idempotency_key: str | None = Field(default=None, max_length=255)


class TicketOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    description: str
    status: TicketStatus
    error_reason: str | None
    created_at: datetime
    updated_at: datetime


class TicketList(BaseModel):
    items: list[TicketOut]
    total: int