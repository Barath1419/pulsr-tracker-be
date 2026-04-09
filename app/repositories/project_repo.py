import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.project import Project


class ProjectRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, project_id: uuid.UUID) -> Project | None:
        return self.db.execute(
            select(Project).where(Project.id == project_id)
        ).scalar_one_or_none()

    def list_for_user(self, user_id: uuid.UUID) -> list[Project]:
        return list(
            self.db.execute(
                select(Project).where(Project.user_id == user_id).order_by(Project.created_at.desc())
            ).scalars().all()
        )

    def create(self, user_id: uuid.UUID, **kwargs) -> Project:
        project = Project(user_id=user_id, **kwargs)
        self.db.add(project)
        self.db.commit()
        self.db.refresh(project)
        return project

    def update(self, project: Project, **kwargs) -> Project:
        for key, value in kwargs.items():
            setattr(project, key, value)
        self.db.commit()
        self.db.refresh(project)
        return project

    def delete(self, project: Project) -> None:
        self.db.delete(project)
        self.db.commit()
