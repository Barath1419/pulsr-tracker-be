import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class GoalCreate(BaseModel):
    name: str = Field(..., max_length=100)
    target_minutes: int = Field(..., gt=0)
    current_minutes: int = Field(default=0, ge=0)
    period: str = Field(default="weekly")
    color: str | None = None


class GoalUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=100)
    target_minutes: int | None = Field(default=None, gt=0)
    current_minutes: int | None = Field(default=None, ge=0)
    period: str | None = None
    color: str | None = None


class GoalOut(BaseModel):
    id: uuid.UUID
    name: str
    target_minutes: int
    current_minutes: int
    period: str
    color: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
