from fastapi import HTTPException, status
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.repositories.user_repo import UserRepository
from app.schemas.user import Token


class UserService:
    def __init__(self, db: Session):
        self.repo = UserRepository(db)

    def signup(self, email: str, password: str) -> Token:
        existing = self.repo.get_by_email(email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered",
            )
        password_hash = hash_password(password)
        user = self.repo.create(email=email, password_hash=password_hash)
        token = create_access_token(subject=str(user.id))
        return Token(access_token=token)

    def login(self, email: str, password: str) -> Token:
        user = self.repo.get_by_email(email)
        if not user or not verify_password(password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        token = create_access_token(subject=str(user.id))
        return Token(access_token=token)

    def google_signin(self, id_token_str: str) -> Token:
        try:
            idinfo = id_token.verify_oauth2_token(
                id_token_str,
                google_requests.Request(),
                settings.GOOGLE_CLIENT_ID,
            )
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Google token",
            )

        google_id = idinfo["sub"]
        email = idinfo["email"]

        # Find by google_id first, then by email
        user = self.repo.get_by_google_id(google_id)
        if not user:
            user = self.repo.get_by_email(email)
            if user:
                # Existing email user — link their Google account
                self.repo.set_google_id(user, google_id)
            else:
                # Brand new user
                user = self.repo.create(email=email, google_id=google_id)

        token = create_access_token(subject=str(user.id))
        return Token(access_token=token)

    def get_by_id(self, user_id) -> User:
        user = self.repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        return user
