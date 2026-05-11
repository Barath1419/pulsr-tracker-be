import uuid
from datetime import date, datetime

from pydantic import BaseModel


class ReflectionUpsert(BaseModel):
    date: date
    content: str


class ReflectionOut(BaseModel):
    id: uuid.UUID
    date: date
    content: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
