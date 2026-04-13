import uuid
from typing import Optional

from pydantic import BaseModel, Field


class ActivityCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    category_id: uuid.UUID
    project_id: Optional[uuid.UUID] = None
    description: Optional[str] = None
    type: str = "task"


class ActivityUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    project_id: Optional[uuid.UUID] = None
    description: Optional[str] = None
    type: str | None = None


class ActivityOut(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    category_id: uuid.UUID
    project_id: Optional[uuid.UUID]
    name: str
    description: Optional[str]
    type: str

    model_config = {"from_attributes": True}
