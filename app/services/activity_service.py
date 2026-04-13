import uuid
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.activity import Activity
from app.schemas.activity import ActivityCreate, ActivityOut, ActivityUpdate


class ActivityService:
    def __init__(self, db: Session):
        self.db = db

    def list_activities(
        self, user_id: uuid.UUID,
        category_id: Optional[uuid.UUID] = None,
        project_id: Optional[uuid.UUID] = None,
    ) -> list[ActivityOut]:
        stmt = select(Activity).where(Activity.user_id == user_id)
        if category_id:
            stmt = stmt.where(Activity.category_id == category_id)
        if project_id:
            stmt = stmt.where(Activity.project_id == project_id)
        stmt = stmt.order_by(Activity.name)
        rows = list(self.db.execute(stmt).scalars().all())
        return [ActivityOut.model_validate(a) for a in rows]

    def create_activity(self, user_id: uuid.UUID, payload: ActivityCreate) -> ActivityOut:
        a = Activity(
            user_id=user_id,
            category_id=payload.category_id,
            project_id=payload.project_id,
            name=payload.name,
            description=payload.description,
            type=payload.type,
        )
        self.db.add(a)
        self.db.commit()
        self.db.refresh(a)
        return ActivityOut.model_validate(a)

    def update_activity(self, act_id: uuid.UUID, user_id: uuid.UUID, payload: ActivityUpdate) -> ActivityOut:
        a = self._get_owned(act_id, user_id)
        for field, val in payload.model_dump(exclude_unset=True).items():
            setattr(a, field, val)
        self.db.commit()
        self.db.refresh(a)
        return ActivityOut.model_validate(a)

    def delete_activity(self, act_id: uuid.UUID, user_id: uuid.UUID) -> None:
        a = self._get_owned(act_id, user_id)
        self.db.delete(a)
        self.db.commit()

    def _get_owned(self, act_id: uuid.UUID, user_id: uuid.UUID) -> Activity:
        a = self.db.execute(
            select(Activity).where(Activity.id == act_id)
        ).scalar_one_or_none()
        if not a:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Activity not found")
        if a.user_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
        return a
