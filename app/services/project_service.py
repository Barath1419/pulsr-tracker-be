import uuid
from datetime import date

from fastapi import HTTPException, status

from app.models.project import Project
from app.repositories.project_repo import ProjectRepository
from app.schemas.project import ProjectCreate, ProjectOut, ProjectUpdate
from sqlalchemy.orm import Session


def _compute_status(start_date: date, end_date: date | None) -> str:
    today = date.today()
    if end_date and end_date < today:
        return "completed"
    if start_date > today:
        return "upcoming"
    return "active"


def _compute_progress(
    start_date: date,
    end_date: date | None,
    override: float | None,
) -> float:
    if override is not None:
        return round(override, 1)
    if not end_date:
        return 0.0
    today = date.today()
    total = (end_date - start_date).days
    if total <= 0:
        return 100.0
    elapsed = (today - start_date).days
    return round(max(0.0, min(100.0, elapsed / total * 100)), 1)


def _to_out(project: Project) -> ProjectOut:
    return ProjectOut(
        id=project.id,
        name=project.name,
        start_date=project.start_date,
        end_date=project.end_date,
        notes=project.notes,
        status=_compute_status(project.start_date, project.end_date),
        progress=_compute_progress(project.start_date, project.end_date, project.progress_override),
        progress_override=project.progress_override,
        created_at=project.created_at,
        updated_at=project.updated_at,
    )


class ProjectService:
    def __init__(self, db: Session):
        self.repo = ProjectRepository(db)

    def list_projects(self, user_id: uuid.UUID) -> list[ProjectOut]:
        return [_to_out(p) for p in self.repo.list_for_user(user_id)]

    def create_project(self, user_id: uuid.UUID, payload: ProjectCreate) -> ProjectOut:
        project = self.repo.create(
            user_id=user_id,
            name=payload.name,
            start_date=payload.start_date,
            end_date=payload.end_date,
            notes=payload.notes,
            progress_override=payload.progress_override,
            category_id=payload.category_id,
        )
        return _to_out(project)

    def update_project(
        self, project_id: uuid.UUID, user_id: uuid.UUID, payload: ProjectUpdate
    ) -> ProjectOut:
        project = self._get_owned(project_id, user_id)
        updates = payload.model_dump(exclude_unset=True)
        project = self.repo.update(project, **updates)
        return _to_out(project)

    def delete_project(self, project_id: uuid.UUID, user_id: uuid.UUID) -> None:
        project = self._get_owned(project_id, user_id)
        self.repo.delete(project)

    def _get_owned(self, project_id: uuid.UUID, user_id: uuid.UUID) -> Project:
        project = self.repo.get_by_id(project_id)
        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
        if project.user_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
        return project
