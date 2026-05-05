from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.user import Token, UserCreate, UserLogin
from app.services.user_service import UserService

router = APIRouter(prefix="/auth", tags=["auth"])


class GoogleTokenPayload(BaseModel):
    id_token: str


@router.post("/signup", response_model=Token, status_code=201)
def signup(payload: UserCreate, db: Session = Depends(get_db)) -> Token:
    return UserService(db).signup(email=payload.email, password=payload.password)


@router.post("/login", response_model=Token)
def login(payload: UserLogin, db: Session = Depends(get_db)) -> Token:
    return UserService(db).login(email=payload.email, password=payload.password)


@router.post("/google", response_model=Token)
def google_signin(payload: GoogleTokenPayload, db: Session = Depends(get_db)) -> Token:
    return UserService(db).google_signin(payload.id_token)
