from sqlmodel import Session, select, func
from app.models.user import Entry, Category, EntryType, Subscription, Status, BillingCycle
from typing import Optional, List, Dict
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def _monthly_sub_amount(amount: float, billing_cycle: str) -> float:
    """Normalise a subscription charge to its monthly equivalent."""
    cycle = billing_cycle.lower() if isinstance(billing_cycle, str) else billing_cycle.value.lower()
    if cycle == BillingCycle.WEEKLY.value:
        return round(amount * 52 / 12, 2)
    if cycle == BillingCycle.YEARLY.value:
        return round(amount / 12, 2)
    return round(amount, 2)  # monthly (default)


class EntryRepository:
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

    def _serialize(self, entry: Entry) -> Dict:
        return {
            "entry_id": entry.entry_id,
            "name": entry.description or "",
            "category": self._category_name(entry.category_id),
            "category_id": entry.category_id,
            "amount": round(entry.amount, 2),
            "date": entry.date.strftime("%Y-%m-%d") if entry.date else None,
            "type": entry.type,
        }

    def _active_subs(self, user_id: int) -> List[Subscription]:
        return self.db.exec(
            select(Subscription).where(
                Subscription.user_id == user_id,
                Subscription.status == Status.ACTIVE,
            )
        ).all()

    def _sub_monthly_total(self, user_id: int) -> float:
        """Total monthly cost of all active subscriptions."""
        return round(
            sum(_monthly_sub_amount(s.amount, s.billing_cycle) for s in self._active_subs(user_id)),
            2,
        )

    def _sub_category_spending(self, user_id: int) -> Dict[str, float]:
        """Subscription costs grouped by category, normalised to monthly."""
        totals: Dict[str, float] = {}
        for sub in self._active_subs(user_id):
            cat = self._category_name(sub.category_id)
            totals[cat] = round(
                totals.get(cat, 0) + _monthly_sub_amount(sub.amount, sub.billing_cycle), 2
            )
        return totals

    def _sub_as_expense_rows(self, user_id: int) -> List[Dict]:
        """Return active subscriptions serialised as expense-like dicts."""
        today = datetime.now().strftime("%Y-%m-%d")
        rows = []
        for sub in self._active_subs(user_id):
            rows.append({
                "entry_id": None,
                "name": sub.name,
                "category": self._category_name(sub.category_id),
                "category_id": sub.category_id,
                "amount": round(_monthly_sub_amount(sub.amount, sub.billing_cycle), 2),
                "date": sub.next_billing_date.strftime("%Y-%m-%d") if sub.next_billing_date else today,
                "type": "subscription",
            })
        return rows

    # ------------------------------------------------------------------ #
    #  Reads — expenses only (no subscriptions)                            #
    # ------------------------------------------------------------------ #

    def get_expenses(self, user_id: int) -> List[Dict]:
        """Raw Entry rows of type EXPENSE, newest first."""
        stmt = (
            select(Entry)
            .where(Entry.user_id == user_id, Entry.type == EntryType.EXPENSE)
            .order_by(Entry.date.desc())
        )
        return [self._serialize(e) for e in self.db.exec(stmt).all()]

    def get_income_entries(self, user_id: int) -> List[Dict]:
        stmt = (
            select(Entry)
            .where(Entry.user_id == user_id, Entry.type == EntryType.INCOME)
            .order_by(Entry.date.desc())
        )
        return [self._serialize(e) for e in self.db.exec(stmt).all()]

    # ------------------------------------------------------------------ #
    #  Reads — combined (expenses + subscriptions)                         #
    # ------------------------------------------------------------------ #

    def get_all_spending(self, user_id: int) -> List[Dict]:
        """All expenses AND active subscriptions, sorted by date descending."""
        entries = self.get_expenses(user_id)
        subs = self._sub_as_expense_rows(user_id)
        combined = entries + subs
        combined.sort(key=lambda x: x["date"] or "", reverse=True)
        return combined

    def get_recent_expenses(self, user_id: int, limit: int = 5) -> List[Dict]:
        """Most recent spending across expenses + subscriptions."""
        return self.get_all_spending(user_id)[:limit]

    def get_total_expenses(self, user_id: int) -> float:
        """Sum of Entry expenses PLUS monthly subscription costs."""
        stmt = select(func.sum(Entry.amount)).where(
            Entry.user_id == user_id, Entry.type == EntryType.EXPENSE
        )
        entry_total = round(self.db.exec(stmt).one() or 0.0, 2)
        return round(entry_total + self._sub_monthly_total(user_id), 2)

    def get_monthly_income(self, user_id: int) -> float:
        """Sum of all INCOME entries for the current calendar month."""
        now = datetime.now()
        stmt = select(func.sum(Entry.amount)).where(
            Entry.user_id == user_id,
            Entry.type == EntryType.INCOME,
            func.to_char(Entry.date, 'YYYY-MM') == now.strftime("%Y-%m"),
        )
        return round(self.db.exec(stmt).one() or 0.0, 2)

    def get_category_spending(self, user_id: int) -> Dict[str, float]:
        """
        Category totals combining Entry expenses + monthly subscription costs.
        """
        totals: Dict[str, float] = {}

        # Entry-based expenses
        for e in self.db.exec(
            select(Entry).where(Entry.user_id == user_id, Entry.type == EntryType.EXPENSE)
        ).all():
            cat = self._category_name(e.category_id)
            totals[cat] = round(totals.get(cat, 0) + e.amount, 2)

        # Subscription costs merged into the same categories
        for cat, amount in self._sub_category_spending(user_id).items():
            totals[cat] = round(totals.get(cat, 0) + amount, 2)

        return totals

    def get_expenses_by_month(self, user_id: int, year: int, month: int) -> List[Dict]:
        """Entry expenses for a specific month (used by calendar)."""
        month_str = f"{year}-{month:02d}"
        stmt = (
            select(Entry)
            .where(
                Entry.user_id == user_id,
                Entry.type == EntryType.EXPENSE,
                func.to_char(Entry.date, 'YYYY-MM') == month_str,
            )
            .order_by(Entry.date)
        )
        return [self._serialize(e) for e in self.db.exec(stmt).all()]

    def get_monthly_expense_totals(self, user_id: int, num_months: int = 6) -> Dict:
        """
        Monthly totals (Entry expenses + subscription costs) for the last
        *num_months* calendar months.
        """
        from calendar import month_abbr
        now = datetime.now()
        sub_monthly = self._sub_monthly_total(user_id)
        labels = []
        totals = []
        for delta in range(num_months - 1, -1, -1):
            month_offset = now.month - delta - 1
            year = now.year + month_offset // 12
            month = month_offset % 12 + 1
            month_str = f"{year}-{month:02d}"
            stmt = select(func.sum(Entry.amount)).where(
                Entry.user_id == user_id,
                Entry.type == EntryType.EXPENSE,
                func.to_char(Entry.date, 'YYYY-MM') == month_str,
            )
            entry_total = round(self.db.exec(stmt).one() or 0.0, 2)
            # Add subscription costs to every month they're active
            total = round(entry_total + sub_monthly, 2)
            labels.append(month_abbr[month])
            totals.append(total)
        return {"labels": labels, "totals": totals}

    def get_monthly_income_totals(self, user_id: int, num_months: int = 6) -> Dict:
        from calendar import month_abbr
        now = datetime.now()
        labels = []
        totals = []
        for delta in range(num_months - 1, -1, -1):
            month_offset = now.month - delta - 1
            year = now.year + month_offset // 12
            month = month_offset % 12 + 1
            month_str = f"{year}-{month:02d}"
            stmt = select(func.sum(Entry.amount)).where(
                Entry.user_id == user_id,
                Entry.type == EntryType.INCOME,
                func.to_char(Entry.date, 'YYYY-MM') == month_str,
            )
            total = round(self.db.exec(stmt).one() or 0.0, 2)
            labels.append(month_abbr[month])
            totals.append(total)
        return {"labels": labels, "totals": totals}

    # ------------------------------------------------------------------ #
    #  Writes                                                              #
    # ------------------------------------------------------------------ #

    def create_entry(
        self,
        user_id: int,
        description: str,
        amount: float,
        entry_type: EntryType,
        category_id: Optional[int],
        date: Optional[datetime] = None,
    ) -> Dict:
        entry = Entry(
            user_id=user_id,
            description=description,
            amount=amount,
            type=entry_type,
            category_id=category_id,
            date=date or datetime.now(),
        )
        try:
            self.db.add(entry)
            self.db.commit()
            self.db.refresh(entry)
            return self._serialize(entry)
        except Exception as e:
            logger.error(f"Error creating entry: {e}")
            self.db.rollback()
            raise

    def set_monthly_income(self, user_id: int, amount: float, date: Optional[datetime] = None) -> Dict:
        """Replace the manual income entry for the current month with a new amount."""
        date = date or datetime.now()
        month_str = date.strftime("%Y-%m")
        existing_entries = self.db.exec(
            select(Entry).where(
                Entry.user_id == user_id,
                Entry.type == EntryType.INCOME,
                func.to_char(Entry.date, 'YYYY-MM') == month_str,
                Entry.description == "Manual income update",
            )
        ).all()

        for entry in existing_entries:
            self.db.delete(entry)
        if existing_entries:
            self.db.commit()

        return self.create_entry(
            user_id=user_id,
            description="Manual income update",
            amount=amount,
            entry_type=EntryType.INCOME,
            category_id=None,
            date=date,
        )

    def delete_entry(self, entry_id: int, user_id: int) -> bool:
        entry = self.db.get(Entry, entry_id)
        if not entry or entry.user_id != user_id:
            return False
        try:
            self.db.delete(entry)
            self.db.commit()
            return True
        except Exception as e:
            logger.error(f"Error deleting entry: {e}")
            self.db.rollback()
            raise
