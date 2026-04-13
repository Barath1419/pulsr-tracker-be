import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class CategoryCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    type: str = "custom"


class CategoryUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    type: str | None = None


class ActivityInCategory(BaseModel):
    id: uuid.UUID
    name: str
    description: Optional[str]
    type: str
    project_id: Optional[uuid.UUID]

    model_config = {"from_attributes": True}


class ProjectInCategory(BaseModel):
    id: uuid.UUID
    name: str
    activities: list[ActivityInCategory] = []

    model_config = {"from_attributes": True}


class CategoryOut(BaseModel):
    id: uuid.UUID
    name: str
    type: str
    created_at: datetime
    projects: list[ProjectInCategory] = []
    activities: list[ActivityInCategory] = []  # activities with no project

    model_config = {"from_attributes": True}
