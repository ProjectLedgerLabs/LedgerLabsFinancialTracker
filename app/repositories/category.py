from sqlmodel import Session, select
from app.models.user import Category
from typing import Optional, List, Dict
import logging

logger = logging.getLogger(__name__)


class CategoryRepository:
    def __init__(self, db: Session):
        self.db = db

    def _serialize(self, cat: Category) -> Dict:
        return {"category_id": cat.category_id, "name": cat.name}

    def get_all(self, user_id: int) -> List[Dict]:
        stmt = select(Category).where(Category.user_id == user_id)
        return [self._serialize(c) for c in self.db.exec(stmt).all()]

    def get_by_name(self, user_id: int, name: str) -> Optional[Category]:
        return self.db.exec(
            select(Category).where(Category.user_id == user_id, Category.name == name)
        ).one_or_none()

    def create(self, user_id: int, name: str) -> Dict:
        cat = Category(user_id=user_id, name=name)
        try:
            self.db.add(cat)
            self.db.commit()
            self.db.refresh(cat)
            return self._serialize(cat)
        except Exception as e:
            logger.error(f"Error creating category: {e}")
            self.db.rollback()
            raise

    def get_or_create(self, user_id: int, name: str) -> Category:
        existing = self.get_by_name(user_id, name)
        if existing:
            return existing
        cat = Category(user_id=user_id, name=name)
        self.db.add(cat)
        self.db.commit()
        self.db.refresh(cat)
        return cat
