import uuid
from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, Field


class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    start_date: date
    end_date: date | None = None
    notes: str | None = None
    progress_override: float | None = Field(default=None, ge=0.0, le=100.0)
    category_id: uuid.UUID | None = None


class ProjectUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    start_date: date | None = None
    end_date: date | None = None
    notes: str | None = None
    progress_override: float | None = Field(default=None, ge=0.0, le=100.0)
    category_id: uuid.UUID | None = None


class ProjectOut(BaseModel):
    id: uuid.UUID
    name: str
    start_date: date
    end_date: date | None
    notes: str | None
    status: Literal["active", "upcoming", "completed"]
    progress: float
    progress_override: float | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
