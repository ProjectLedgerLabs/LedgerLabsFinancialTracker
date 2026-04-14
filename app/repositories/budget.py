from sqlmodel import Session, select
from app.models.user import BudgetLimit, Category
from app.repositories.category import CategoryRepository
from typing import Optional, List, Dict
import logging

logger = logging.getLogger(__name__)

# Fallback color palette for categories without an explicit color mapping
CATEGORY_COLORS = {
    "Food": "#006699",
    "Transportation": "#669900",
    "Entertainment": "#ff6600",
    "Health": "#cc3399",
    "Software": "#99cc33",
    "Utilities": "#ffcc00",
}
DEFAULT_COLOR = "#888888"


class BudgetRepository:
    def __init__(self, db: Session):
        self.db = db

    # ------------------------------------------------------------------ #
    #  Internal helpers                                                    #
    # ------------------------------------------------------------------ #

    def _category_name(self, category_id: Optional[int]) -> str:
        if category_id is None:
            return "Uncategorized"
        cat = self.db.get(Category, category_id)
        return cat.name if cat else "Uncategorized"

    def _color_for(self, category_name: str) -> str:
        return CATEGORY_COLORS.get(category_name, DEFAULT_COLOR)

    def _serialize(self, bl: BudgetLimit, spent: float = 0.0) -> Dict:
        name = self._category_name(bl.category_id)
        limit = round(bl.limit_amount, 2)
        spent = round(spent, 2)
        remaining = round(limit - spent, 2)
        percentage = round((spent / limit) * 100, 1) if limit > 0 else 0.0
        return {
            "budget_id": bl.budget_id,
            "category": name,
            "category_id": bl.category_id,
            "limit": limit,
            "spent": spent,
            "remaining": remaining,
            "percentage": min(percentage, 100),
            "over_budget": spent > limit,
            "color": self._color_for(name),
        }

    # ------------------------------------------------------------------ #
    #  Reads                                                               #
    # ------------------------------------------------------------------ #

    def get_all(self, user_id: int, spending: Dict[str, float]) -> List[Dict]:
        """
        Return all budget limits for the user, enriched with live spending data.
        `spending` should be the dict from EntryRepository.get_category_spending().
        """
        stmt = select(BudgetLimit).where(BudgetLimit.user_id == user_id)
        rows = self.db.exec(stmt).all()
        return [self._serialize(bl, spending.get(self._category_name(bl.category_id), 0.0))
                for bl in rows]

    def get_by_category(self, user_id: int, category_id: int) -> Optional[BudgetLimit]:
        return self.db.exec(
            select(BudgetLimit).where(
                BudgetLimit.user_id == user_id,
                BudgetLimit.category_id == category_id,
            )
        ).one_or_none()

    # ------------------------------------------------------------------ #
    #  Writes                                                              #
    # ------------------------------------------------------------------ #

    def set_limit(self, user_id: int, category_name: str, limit_amount: float) -> Dict:
        """
        Create or update the budget limit for a category.
        Uses get_or_create so a new Category row is made if needed.
        """
        cat_repo = CategoryRepository(self.db)
        category = cat_repo.get_or_create(user_id, category_name)

        existing = self.get_by_category(user_id, category.category_id)
        if existing:
            existing.limit_amount = limit_amount
            record = existing
        else:
            record = BudgetLimit(
                user_id=user_id,
                category_id=category.category_id,
                limit_amount=limit_amount,
            )

        try:
            self.db.add(record)
            self.db.commit()
            self.db.refresh(record)
            return self._serialize(record)
        except Exception as e:
            logger.error(f"Error setting budget limit: {e}")
            self.db.rollback()
            raise

    def delete(self, budget_id: int, user_id: int) -> bool:
        record = self.db.get(BudgetLimit, budget_id)
        if not record or record.user_id != user_id:
            return False
        try:
            self.db.delete(record)
            self.db.commit()
            return True
        except Exception as e:
            logger.error(f"Error deleting budget limit: {e}")
            self.db.rollback()
            raise
