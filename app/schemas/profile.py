import uuid
from datetime import date, datetime

from pydantic import BaseModel


class GoalOut(BaseModel):
    id: uuid.UUID
    name: str
    target_minutes: int
    current_minutes: int
    period: str
    color: str | None

    model_config = {"from_attributes": True}


class ReflectionOut(BaseModel):
    id: uuid.UUID
    date: date
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ProfileOut(BaseModel):
    id: uuid.UUID
    email: str
    name: str | None
    avatar_url: str | None
    avg_daily_minutes: int
    top_category: str
    most_used_project: str
    current_streak: int
    best_streak: int
    productivity_insight: str
    consistency_insight: str
    goals: list[GoalOut]
    recent_reflections: list[ReflectionOut]


class ProfileUpdate(BaseModel):
    name: str | None = None
    avatar_url: str | None = None
