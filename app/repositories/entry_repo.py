import uuid
from datetime import date, datetime, time, timezone

from sqlalchemy import and_, select
from sqlalchemy.orm import Session

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
        stmt = select(Entry).where(Entry.user_id == user_id)
        if filter_date is not None:
            day_start = datetime.combine(filter_date, time.min).replace(tzinfo=timezone.utc)
            day_end = datetime.combine(filter_date, time.max).replace(tzinfo=timezone.utc)
            stmt = stmt.where(
                and_(Entry.start_time >= day_start, Entry.start_time <= day_end)
            )
        stmt = stmt.order_by(Entry.start_time)
        return list(self.db.execute(stmt).scalars().all())

    def create(
        self,
        user_id: uuid.UUID,
        title: str,
        start_time: datetime,
        end_time: datetime,
    ) -> Entry:
        entry = Entry(
            user_id=user_id,
            title=title,
            start_time=start_time,
            end_time=end_time,
        )
        self.db.add(entry)
        self.db.commit()
        self.db.refresh(entry)
        return entry

    def delete(self, entry: Entry) -> None:
        self.db.delete(entry)
        self.db.commit()
