from sqlmodel import Session, select, func
from app.models.user import Subscription, Category, Status, BillingCycle
from typing import Optional, List, Dict
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class SubscriptionRepository:
    def __init__(self, db: Session):
        self.db = db

    def _category_name(self, category_id: Optional[int]) -> str:
        if category_id is None:
            return "Uncategorized"
        cat = self.db.get(Category, category_id)
        return cat.name if cat else "Uncategorized"

    def _serialize(self, sub: Subscription) -> Dict:
        return {
            "id": sub.subscription_id,
            "name": sub.name,
            "amount": round(sub.amount, 2),
            "category": self._category_name(sub.category_id),
            "category_id": sub.category_id,
            "billing_cycle": sub.billing_cycle,
            "next_billing": sub.next_billing_date.strftime("%Y-%m-%d") if sub.next_billing_date else None,
            "active": sub.status == Status.ACTIVE,
            "description": sub.description,
        }

    # ------------------------------------------------------------------ #
    #  Reads                                                               #
    # ------------------------------------------------------------------ #

    def get_active(self, user_id: int) -> List[Dict]:
        stmt = select(Subscription).where(
            Subscription.user_id == user_id,
            Subscription.status == Status.ACTIVE,
        )
        return [self._serialize(s) for s in self.db.exec(stmt).all()]

    def get_all(self, user_id: int) -> List[Dict]:
        stmt = select(Subscription).where(Subscription.user_id == user_id)
        return [self._serialize(s) for s in self.db.exec(stmt).all()]

    def get_monthly_cost(self, user_id: int) -> float:
        stmt = select(func.sum(Subscription.amount)).where(
            Subscription.user_id == user_id,
            Subscription.status == Status.ACTIVE,
        )
        return round(self.db.exec(stmt).one() or 0.0, 2)

    def get_upcoming_billing(self, user_id: int, days: int = 30) -> List[Dict]:
        today = datetime.now().date()
        cutoff = today + timedelta(days=days)
        stmt = select(Subscription).where(
            Subscription.user_id == user_id,
            Subscription.status == Status.ACTIVE,
            Subscription.next_billing_date != None,
        )
        upcoming = []
        for sub in self.db.exec(stmt).all():
            next_date = sub.next_billing_date.date()
            if today <= next_date <= cutoff:
                serialized = self._serialize(sub)
                serialized["days_until"] = (next_date - today).days
                upcoming.append(serialized)
        return sorted(upcoming, key=lambda x: x["days_until"])

    # ------------------------------------------------------------------ #
    #  Writes                                                              #
    # ------------------------------------------------------------------ #

    def create(
        self,
        user_id: int,
        name: str,
        amount: float,
        billing_cycle: BillingCycle,
        next_billing_date: Optional[datetime],
        category_id: Optional[int] = None,
        description: Optional[str] = None,
    ) -> Dict:
        sub = Subscription(
            user_id=user_id,
            name=name,
            amount=amount,
            billing_cycle=billing_cycle,
            next_billing_date=next_billing_date,
            category_id=category_id,
            description=description,
            status=Status.ACTIVE,
        )
        try:
            self.db.add(sub)
            self.db.commit()
            self.db.refresh(sub)
            return self._serialize(sub)
        except Exception as e:
            logger.error(f"Error creating subscription: {e}")
            self.db.rollback()
            raise

    def update(self, sub_id: int, user_id: int, updates: Dict) -> Optional[Dict]:
        sub = self.db.get(Subscription, sub_id)
        if not sub or sub.user_id != user_id:
            return None
        for key, value in updates.items():
            if hasattr(sub, key) and value is not None:
                setattr(sub, key, value)
        try:
            self.db.add(sub)
            self.db.commit()
            self.db.refresh(sub)
            return self._serialize(sub)
        except Exception as e:
            logger.error(f"Error updating subscription: {e}")
            self.db.rollback()
            raise

    def delete(self, sub_id: int, user_id: int) -> bool:
        sub = self.db.get(Subscription, sub_id)
        if not sub or sub.user_id != user_id:
            return False
        try:
            self.db.delete(sub)
            self.db.commit()
            return True
        except Exception as e:
            logger.error(f"Error deleting subscription: {e}")
            self.db.rollback()
            raise
