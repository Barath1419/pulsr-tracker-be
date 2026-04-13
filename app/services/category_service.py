import uuid

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.category import Category
from app.models.project import Project
from app.schemas.category import CategoryCreate, CategoryOut, CategoryUpdate, ActivityInCategory, ProjectInCategory


def _to_out(cat: Category) -> CategoryOut:
    projects_out = []
    for p in cat.projects:
        acts = [
            ActivityInCategory(
                id=a.id, name=a.name, description=a.description,
                type=a.type, project_id=a.project_id,
            )
            for a in p.activities
        ]
        projects_out.append(ProjectInCategory(id=p.id, name=p.name, activities=acts))

    # Activities directly under category (no project)
    direct_acts = [
        ActivityInCategory(
            id=a.id, name=a.name, description=a.description,
            type=a.type, project_id=a.project_id,
        )
        for a in cat.activities if a.project_id is None
    ]

    return CategoryOut(
        id=cat.id,
        name=cat.name,
        type=cat.type,
        created_at=cat.created_at,
        projects=projects_out,
        activities=direct_acts,
    )


class CategoryService:
    def __init__(self, db: Session):
        self.db = db

    def _load_all(self, user_id: uuid.UUID) -> list[Category]:
        stmt = (
            select(Category)
            .options(
                selectinload(Category.projects).selectinload(Project.activities),
                selectinload(Category.activities),
            )
            .where(Category.user_id == user_id)
            .order_by(Category.created_at)
        )
        return list(self.db.execute(stmt).scalars().unique().all())

    def list_categories(self, user_id: uuid.UUID) -> list[CategoryOut]:
        return [_to_out(c) for c in self._load_all(user_id)]

    def create_category(self, user_id: uuid.UUID, payload: CategoryCreate) -> CategoryOut:
        cat = Category(user_id=user_id, name=payload.name, type=payload.type)
        self.db.add(cat)
        self.db.commit()
        self.db.refresh(cat)
        # reload with relationships
        cat = self._get_full(cat.id)
        return _to_out(cat)

    def update_category(self, cat_id: uuid.UUID, user_id: uuid.UUID, payload: CategoryUpdate) -> CategoryOut:
        cat = self._get_owned(cat_id, user_id)
        if payload.name is not None:
            cat.name = payload.name
        if payload.type is not None:
            cat.type = payload.type
        self.db.commit()
        cat = self._get_full(cat.id)
        return _to_out(cat)

    def delete_category(self, cat_id: uuid.UUID, user_id: uuid.UUID) -> None:
        cat = self._get_owned(cat_id, user_id)
        self.db.delete(cat)
        self.db.commit()

    def _get_owned(self, cat_id: uuid.UUID, user_id: uuid.UUID) -> Category:
        cat = self.db.execute(
            select(Category).where(Category.id == cat_id)
        ).scalar_one_or_none()
        if not cat:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
        if cat.user_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
        return cat

    def _get_full(self, cat_id: uuid.UUID) -> Category:
        return self.db.execute(
            select(Category)
            .options(
                selectinload(Category.projects).selectinload(Project.activities),
                selectinload(Category.activities),
            )
            .where(Category.id == cat_id)
        ).scalar_one()
