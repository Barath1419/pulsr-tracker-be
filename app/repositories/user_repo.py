import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: uuid.UUID) -> User | None:
        return self.db.execute(
            select(User).where(User.id == user_id)
        ).scalar_one_or_none()

    def get_by_email(self, email: str) -> User | None:
        return self.db.execute(
            select(User).where(User.email == email)
        ).scalar_one_or_none()

    def get_by_google_id(self, google_id: str) -> User | None:
        return self.db.execute(
            select(User).where(User.google_id == google_id)
        ).scalar_one_or_none()

    def create(self, email: str, password_hash: str | None = None, google_id: str | None = None) -> User:
        user = User(email=email, password_hash=password_hash, google_id=google_id)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def set_google_id(self, user: User, google_id: str) -> User:
        user.google_id = google_id
        self.db.commit()
        self.db.refresh(user)
        return user
