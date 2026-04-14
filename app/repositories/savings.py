from sqlmodel import Session, select, func
from app.models.user import SavingsGoal
from typing import Optional, List, Dict
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class SavingsRepository:
    def __init__(self, db: Session):
        self.db = db

    def _serialize(self, goal: SavingsGoal) -> Dict:
        today = datetime.now().date()
        days_left = 0
        if goal.deadline:
            days_left = max(0, (goal.deadline.date() - today).days)
        target = goal.target_amount or 0.0
        current = goal.current_amount or 0.0
        progress = round((current / target) * 100, 1) if target > 0 else 0.0
        return {
            "goal_id": goal.goal_id,
            "name": goal.name,
            "current": round(current, 2),
            "target": round(target, 2),
            "target_date": goal.deadline.strftime("%Y-%m-%d") if goal.deadline else None,
            "days_left": days_left,
            "progress": progress,
            "description": goal.description,
        }

    # ------------------------------------------------------------------ #
    #  Reads                                                               #
    # ------------------------------------------------------------------ #

    def get_all(self, user_id: int) -> List[Dict]:
        stmt = select(SavingsGoal).where(SavingsGoal.user_id == user_id)
        return [self._serialize(g) for g in self.db.exec(stmt).all()]

    def get_total_saved(self, user_id: int) -> float:
        stmt = select(func.sum(SavingsGoal.current_amount)).where(
            SavingsGoal.user_id == user_id
        )
        return round(self.db.exec(stmt).one() or 0.0, 2)

    def get_total_target(self, user_id: int) -> float:
        stmt = select(func.sum(SavingsGoal.target_amount)).where(
            SavingsGoal.user_id == user_id
        )
        return round(self.db.exec(stmt).one() or 0.0, 2)

    def get_overall_progress(self, user_id: int) -> float:
        saved = self.get_total_saved(user_id)
        target = self.get_total_target(user_id)
        return round((saved / target) * 100, 1) if target > 0 else 0.0

    # ------------------------------------------------------------------ #
    #  Writes                                                              #
    # ------------------------------------------------------------------ #

    def create(
        self,
        user_id: int,
        name: str,
        target_amount: float,
        deadline: Optional[datetime] = None,
        description: Optional[str] = None,
    ) -> Dict:
        goal = SavingsGoal(
            user_id=user_id,
            name=name,
            target_amount=target_amount,
            current_amount=0.0,
            deadline=deadline,
            description=description,
        )
        try:
            self.db.add(goal)
            self.db.commit()
            self.db.refresh(goal)
            return self._serialize(goal)
        except Exception as e:
            logger.error(f"Error creating savings goal: {e}")
            self.db.rollback()
            raise

    def contribute(self, goal_id: int, user_id: int, amount: float) -> Optional[Dict]:
        goal = self.db.get(SavingsGoal, goal_id)
        if not goal or goal.user_id != user_id:
            return None
        goal.current_amount = round((goal.current_amount or 0.0) + amount, 2)
        try:
            self.db.add(goal)
            self.db.commit()
            self.db.refresh(goal)
            return self._serialize(goal)
        except Exception as e:
            logger.error(f"Error contributing to savings goal: {e}")
            self.db.rollback()
            raise

    def delete(self, goal_id: int, user_id: int) -> bool:
        goal = self.db.get(SavingsGoal, goal_id)
        if not goal or goal.user_id != user_id:
            return False
        try:
            self.db.delete(goal)
            self.db.commit()
            return True
        except Exception as e:
            logger.error(f"Error deleting savings goal: {e}")
            self.db.rollback()
            raise
