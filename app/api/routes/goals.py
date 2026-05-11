import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.repositories.goal_repo import GoalRepository
from app.schemas.goal import GoalCreate, GoalOut, GoalUpdate

router = APIRouter(prefix="/goals", tags=["goals"])


@router.get("", response_model=list[GoalOut])
def list_goals(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[GoalOut]:
    return GoalRepository(db).list_for_user(current_user.id)


@router.post("", response_model=GoalOut, status_code=201)
def create_goal(
    payload: GoalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> GoalOut:
    return GoalRepository(db).create(
        user_id=current_user.id,
        name=payload.name,
        target_minutes=payload.target_minutes,
        period=payload.period,
        color=payload.color,
    )


@router.patch("/{goal_id}", response_model=GoalOut)
def update_goal(
    goal_id: uuid.UUID,
    payload: GoalUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> GoalOut:
    repo = GoalRepository(db)
    goal = repo.get(goal_id, current_user.id)
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    return repo.update(
        goal,
        name=payload.name,
        target_minutes=payload.target_minutes,
        current_minutes=payload.current_minutes,
        period=payload.period,
        color=payload.color,
    )


@router.delete("/{goal_id}", status_code=204)
def delete_goal(
    goal_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    repo = GoalRepository(db)
    goal = repo.get(goal_id, current_user.id)
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    repo.delete(goal)
