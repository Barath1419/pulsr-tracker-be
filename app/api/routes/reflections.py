from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.repositories.reflection_repo import ReflectionRepository
from app.schemas.reflection import ReflectionOut, ReflectionUpsert

router = APIRouter(prefix="/reflections", tags=["reflections"])


@router.get("", response_model=list[ReflectionOut])
def list_reflections(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[ReflectionOut]:
    return ReflectionRepository(db).list_recent(current_user.id, limit=10)


@router.post("", response_model=ReflectionOut)
def upsert_reflection(
    payload: ReflectionUpsert,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ReflectionOut:
    return ReflectionRepository(db).upsert(
        user_id=current_user.id,
        reflection_date=payload.date,
        content=payload.content,
    )
