import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, model_validator


class EntryCreate(BaseModel):
    title: str
    start_time: datetime
    end_time: datetime
    project_id: Optional[uuid.UUID] = None
    category: Optional[str] = None

    @model_validator(mode="after")
    def end_must_be_after_start(self) -> "EntryCreate":
        if self.end_time <= self.start_time:
            raise ValueError("end_time must be after start_time")
        return self


class AssignProjectPayload(BaseModel):
    project_id: Optional[uuid.UUID] = None


class EntryOut(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    project_id: Optional[uuid.UUID] = None
    category: Optional[str] = None
    title: str
    start_time: datetime
    end_time: datetime
    created_at: datetime

    model_config = {"from_attributes": True}
