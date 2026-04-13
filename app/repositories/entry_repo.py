import uuid
from datetime import date, datetime

from sqlalchemy import cast, select
from sqlalchemy import Date as SADate
from sqlalchemy.orm import Session, selectinload

from app.models.entry import Entry


class EntryRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, entry_id: uuid.UUID) -> Entry | None:
        return self.db.execute(
            select(Entry).where(Entry.id == entry_id)
        ).scalar_one_or_none()

    def list_for_user(
        self, user_id: uuid.UUID, filter_date: date | None = None
    ) -> list[Entry]:
        stmt = (
            select(Entry)
            .options(selectinload(Entry.project))
            .where(Entry.user_id == user_id)
        )
        if filter_date is not None:
            stmt = stmt.where(
                cast(Entry.start_time, SADate) == filter_date
            )
        stmt = stmt.order_by(Entry.start_time)
        return list(self.db.execute(stmt).scalars().all())

    def create(
        self,
        user_id: uuid.UUID,
        title: str,
        start_time: datetime,
        end_time: datetime,
        project_id: uuid.UUID | None = None,
        category: str | None = None,
    ) -> Entry:
        entry = Entry(
            user_id=user_id,
            title=title,
            start_time=start_time,
            end_time=end_time,
            project_id=project_id,
            category=category,
        )
        self.db.add(entry)
        self.db.commit()
        self.db.refresh(entry)
        return entry

    def assign_project(self, entry: Entry, project_id: uuid.UUID | None) -> Entry:
        entry.project_id = project_id
        self.db.commit()
        self.db.refresh(entry)
        return entry

    def delete(self, entry: Entry) -> None:
        self.db.delete(entry)
        self.db.commit()
