import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.goal import Goal


class GoalRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_for_user(self, user_id: uuid.UUID) -> list[Goal]:
        return list(
            self.db.execute(
                select(Goal).where(Goal.user_id == user_id).order_by(Goal.created_at)
            ).scalars().all()
        )

    def get(self, goal_id: uuid.UUID, user_id: uuid.UUID) -> Goal | None:
        return self.db.execute(
            select(Goal).where(Goal.id == goal_id, Goal.user_id == user_id)
        ).scalar_one_or_none()

    def create(self, user_id: uuid.UUID, name: str, target_minutes: int,
               period: str, color: str | None) -> Goal:
        goal = Goal(user_id=user_id, name=name, target_minutes=target_minutes,
                    period=period, color=color)
        self.db.add(goal)
        self.db.commit()
        self.db.refresh(goal)
        return goal

    def update(self, goal: Goal, **kwargs) -> Goal:
        for k, v in kwargs.items():
            if v is not None or k == "color":
                setattr(goal, k, v)
        self.db.commit()
        self.db.refresh(goal)
        return goal

    def delete(self, goal: Goal) -> None:
        self.db.delete(goal)
        self.db.commit()
