from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.user import Token, UserCreate, UserLogin
from app.services.user_service import UserService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=Token, status_code=201)
def signup(payload: UserCreate, db: Session = Depends(get_db)) -> Token:
    return UserService(db).signup(email=payload.email, password=payload.password)


@router.post("/login", response_model=Token)
def login(payload: UserLogin, db: Session = Depends(get_db)) -> Token:
    return UserService(db).login(email=payload.email, password=payload.password)
