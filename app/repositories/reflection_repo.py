import uuid
from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.reflection import Reflection


class ReflectionRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_date(self, user_id: uuid.UUID, reflection_date: date) -> Reflection | None:
        return self.db.execute(
            select(Reflection).where(
                Reflection.user_id == user_id,
                Reflection.date == reflection_date,
            )
        ).scalar_one_or_none()

    def list_recent(self, user_id: uuid.UUID, limit: int = 10) -> list[Reflection]:
        return list(
            self.db.execute(
                select(Reflection)
                .where(Reflection.user_id == user_id)
                .order_by(Reflection.date.desc())
                .limit(limit)
            ).scalars().all()
        )

    def upsert(self, user_id: uuid.UUID, reflection_date: date, content: str) -> Reflection:
        existing = self.get_by_date(user_id, reflection_date)
        if existing:
            existing.content = content
            self.db.commit()
            self.db.refresh(existing)
            return existing
        reflection = Reflection(user_id=user_id, date=reflection_date, content=content)
        self.db.add(reflection)
        self.db.commit()
        self.db.refresh(reflection)
        return reflection
