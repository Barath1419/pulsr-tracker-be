import uuid
from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.entry import AssignProjectPayload, EntryCreate, EntryOut
from app.services.entry_service import EntryService

router = APIRouter(prefix="/entries", tags=["entries"])


@router.post("", response_model=EntryOut, status_code=201)
def create_entry(
    payload: EntryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> EntryOut:
    return EntryService(db).create_entry(
        user_id=current_user.id,
        title=payload.title,
        start_time=payload.start_time,
        end_time=payload.end_time,
        project_id=payload.project_id,
        category=payload.category,
    )


@router.get("", response_model=list[EntryOut])
def list_entries(
    filter_date: date | None = Query(default=None, alias="date"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[EntryOut]:
    return EntryService(db).list_entries(
        user_id=current_user.id, filter_date=filter_date
    )


@router.put("/{entry_id}/assign-project", response_model=EntryOut)
def assign_project(
    entry_id: uuid.UUID,
    payload: AssignProjectPayload,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> EntryOut:
    return EntryService(db).assign_project(
        entry_id=entry_id,
        user_id=current_user.id,
        project_id=payload.project_id,
    )


@router.delete("/{entry_id}", status_code=204)
def delete_entry(
    entry_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    EntryService(db).delete_entry(entry_id=entry_id, user_id=current_user.id)
