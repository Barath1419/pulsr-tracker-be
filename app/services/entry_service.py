import uuid
from datetime import date, datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.entry import Entry
from app.repositories.entry_repo import EntryRepository


class EntryService:
    def __init__(self, db: Session):
        self.repo = EntryRepository(db)

    def create_entry(
        self,
        user_id: uuid.UUID,
        title: str,
        start_time: datetime,
        end_time: datetime,
        project_id: uuid.UUID | None = None,
        category: str | None = None,
    ) -> Entry:
        return self.repo.create(
            user_id=user_id,
            title=title,
            start_time=start_time,
            end_time=end_time,
            project_id=project_id,
            category=category,
        )

    def list_entries(
        self, user_id: uuid.UUID, filter_date: date | None = None
    ) -> list[Entry]:
        return self.repo.list_for_user(user_id=user_id, filter_date=filter_date)

    def assign_project(
        self, entry_id: uuid.UUID, user_id: uuid.UUID, project_id: uuid.UUID | None
    ) -> Entry:
        entry = self.repo.get_by_id(entry_id)
        if not entry:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Entry not found",
            )
        if entry.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized",
            )
        return self.repo.assign_project(entry, project_id)

    def delete_entry(self, entry_id: uuid.UUID, user_id: uuid.UUID) -> None:
        entry = self.repo.get_by_id(entry_id)
        if not entry:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Entry not found",
            )
        if entry.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this entry",
            )
        self.repo.delete(entry)
