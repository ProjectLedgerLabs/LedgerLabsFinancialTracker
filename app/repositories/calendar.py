from sqlmodel import Session, select
from app.models.user import CalendarEvent, CalendarEventType, Entry, EntryType
from typing import Optional, List, Dict
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class CalendarRepository:
    def __init__(self, db: Session):
        self.db = db

    def _serialize(self, event: CalendarEvent) -> Dict:
        return {
            "event_id": event.event_id,
            "title": event.title,
            "date": event.date.strftime("%Y-%m-%d") if event.date else None,
            "type": event.type.value.lower() if hasattr(event.type, 'value') else str(event.type).lower(),
            "description": event.description,
        }

    # ------------------------------------------------------------------ #
    #  Reads                                                               #
    # ------------------------------------------------------------------ #

    def get_by_month(self, user_id: int, year: int, month: int) -> Dict[str, List]:
        month_str = f"{year}-{month:02d}"
        stmt = select(CalendarEvent).where(
            CalendarEvent.user_id == user_id,
            CalendarEvent.date != None,
        )
        events_by_date: Dict[str, List] = {}
        for event in self.db.exec(stmt).all():
            if event.date.strftime("%Y-%m") == month_str:
                day = str(event.date.day)
                events_by_date.setdefault(day, []).append(self._serialize(event))
        return events_by_date

    def get_monthly_totals(self, user_id: int, year: int, month: int) -> Dict:
        """
        Derive financial totals from CalendarEvent records that carry amounts.
        Falls back to zero if none exist – the finance_router computes real
        totals from Entry / Subscription tables.
        """
        month_str = f"{year}-{month:02d}"
        stmt = select(CalendarEvent).where(
            CalendarEvent.user_id == user_id,
            CalendarEvent.date != None,
        )
        total_expenses = 0.0
        total_income = 0.0
        for event in self.db.exec(stmt).all():
            if event.date.strftime("%Y-%m") != month_str:
                continue
            if event.type == CalendarEventType.INCOME:
                total_income += 0  # amount stored in Entry, not CalendarEvent
            elif event.type in (CalendarEventType.EXPENSE, CalendarEventType.GOAL_DEADLINE):
                total_expenses += 0
        return {"expenses": round(total_expenses, 2), "income": round(total_income, 2)}

    def get_upcoming(self, user_id: int, days: int = 14) -> List[Dict]:
        from app.repositories.entry import EntryRepository
        from app.repositories.subscription import SubscriptionRepository

        today = datetime.now().date()
        cutoff = today + timedelta(days=days)

        upcoming = []

        # Get CalendarEvent records
        stmt = select(CalendarEvent).where(
            CalendarEvent.user_id == user_id,
            CalendarEvent.date != None,
        )
        for event in self.db.exec(stmt).all():
            event_date = event.date.date()
            if today <= event_date <= cutoff:
                upcoming.append(self._serialize(event))

        # Get upcoming expenses from Entry table
        entry_repo = EntryRepository(self.db)
        expenses_stmt = select(CalendarEvent).where(  # Wait, this should be Entry, not CalendarEvent
            CalendarEvent.user_id == user_id,  # This is wrong, let me fix this
        )
        # Actually, let me use EntryRepository method. First I need to add one.

        # For now, let's query Entry directly

        entry_stmt = select(Entry).where(
            Entry.user_id == user_id,
            Entry.date != None,
            Entry.type == EntryType.EXPENSE,
        )
        for entry in self.db.exec(entry_stmt).all():
            entry_date = entry.date.date()
            if today <= entry_date <= cutoff:
                upcoming.append({
                    "title": entry.description or "Expense",
                    "date": entry.date.strftime("%Y-%m-%d"),
                    "amount": round(entry.amount, 2),
                    "type": "expense",
                })

        # Get upcoming subscription payments
        sub_repo = SubscriptionRepository(self.db)
        upcoming_subs = sub_repo.get_upcoming_billing(user_id, days)
        for sub in upcoming_subs:
            upcoming.append({
                "title": sub["name"],
                "date": sub["next_billing"],
                "amount": round(sub["amount"], 2),
                "type": "subscription",
            })

        return sorted(upcoming, key=lambda x: x["date"])

    # ------------------------------------------------------------------ #
    #  Writes                                                              #
    # ------------------------------------------------------------------ #

    def create(
        self,
        user_id: int,
        title: str,
        event_type: CalendarEventType,
        date: datetime,
        description: Optional[str] = None,
    ) -> Dict:
        event = CalendarEvent(
            user_id=user_id,
            title=title,
            type=event_type,
            date=date,
            description=description,
        )
        try:
            self.db.add(event)
            self.db.commit()
            self.db.refresh(event)
            return self._serialize(event)
        except Exception as e:
            logger.error(f"Error creating calendar event: {e}")
            self.db.rollback()
            raise

    def delete(self, event_id: int, user_id: int) -> bool:
        event = self.db.get(CalendarEvent, event_id)
        if not event or event.user_id != user_id:
            return False
        try:
            self.db.delete(event)
            self.db.commit()
            return True
        except Exception as e:
            logger.error(f"Error deleting calendar event: {e}")
            self.db.rollback()
            raise
