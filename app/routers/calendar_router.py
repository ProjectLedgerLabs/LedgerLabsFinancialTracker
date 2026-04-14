from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from calendar import monthrange
from app.routers import templates
from app.dependencies.auth import AuthDep
from app.dependencies.session import SessionDep
from app.utilities.flash import get_flashed_messages
from app.repositories.calendar import CalendarRepository
from app.repositories.entry import EntryRepository
from app.repositories.subscription import SubscriptionRepository
from app.models.user import CalendarEventType

router = APIRouter(prefix="/calendar", tags=["calendar"])

MONTH_NAMES = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]


class CalendarEventCreate(BaseModel):
    title: str
    date: str
    type: str
    description: Optional[str] = None


def _build_calendar_events(user_id: int, year: int, month: int, db) -> dict:
    """
    Merge CalendarEvent DB rows with expense/subscription entries for the month.
    Returns a {day: [event, ...]} dict.
    """
    cal_repo = CalendarRepository(db)
    entry_repo = EntryRepository(db)
    sub_repo = SubscriptionRepository(db)

    events_by_date = cal_repo.get_by_month(user_id, year, month)

    # Inject expenses from Entry table
    for exp in entry_repo.get_expenses_by_month(user_id, year, month):
        day = str(datetime.strptime(exp["date"], "%Y-%m-%d").day)
        events_by_date.setdefault(day, []).append({
            "title": exp["name"], "date": exp["date"],
            "amount": exp["amount"], "type": "expense",
        })

    # Inject subscriptions billing in this month
    month_str = f"{year}-{month:02d}"
    for sub in sub_repo.get_active(user_id):
        if sub["next_billing"] and sub["next_billing"].startswith(month_str):
            day = str(datetime.strptime(sub["next_billing"], "%Y-%m-%d").day)
            events_by_date.setdefault(day, []).append({
                "title": sub["name"], "date": sub["next_billing"],
                "amount": sub["amount"], "type": "subscription",
            })

    return events_by_date


# ------------------------------------------------------------------ #
#  Page route                                                          #
# ------------------------------------------------------------------ #

@router.get("/", response_class=HTMLResponse)
async def calendar_page(request: Request, user: AuthDep, db: SessionDep):
    now = datetime.now()
    year = int(request.query_params.get("year", now.year))
    month = int(request.query_params.get("month", now.month))

    events_by_date = _build_calendar_events(user.user_id, year, month, db)

    # Monthly totals from Entry table and subscription billing
    entry_repo = EntryRepository(db)
    sub_repo = SubscriptionRepository(db)
    expense_entries = entry_repo.get_expenses_by_month(user.user_id, year, month)
    total_expenses = sum(e["amount"] for e in expense_entries)

    month_str = f"{year}-{month:02d}"
    subscription_expenses = sum(
        sub["amount"]
        for sub in sub_repo.get_active(user.user_id)
        if sub["next_billing"] and sub["next_billing"].startswith(month_str)
    )
    total_expenses = round(total_expenses + subscription_expenses, 2)

    income_history = entry_repo.get_monthly_income_totals(user.user_id, num_months=1)
    total_income = income_history["totals"][0] if income_history["totals"] else 0.0

    upcoming_events = CalendarRepository(db).get_upcoming(user.user_id, days=14)

    first_day = datetime(year, month, 1)
    start_weekday = (first_day.weekday() + 1) % 7
    days_in_month = monthrange(year, month)[1]

    prev_year, prev_month = (year - 1, 12) if month == 1 else (year, month - 1)
    next_year, next_month = (year + 1, 1) if month == 12 else (year, month + 1)

    return templates.TemplateResponse(
        request=request, name="calendar.html",
        context={
            "flash_messages": get_flashed_messages(request),
            "user": user, "active_page": "calendar",
            "year": year, "month": month,
            "current_month_name": MONTH_NAMES[month - 1],
            "prev_year": prev_year, "prev_month": prev_month,
            "next_year": next_year, "next_month": next_month,
            "start_weekday": start_weekday, "days_in_month": days_in_month,
            "events_by_date": events_by_date,
            "monthly_totals": {"expenses": round(total_expenses, 2), "income": round(total_income, 2)},
            "upcoming_events": upcoming_events,
        },
    )


# ------------------------------------------------------------------ #
#  API routes                                                          #
# ------------------------------------------------------------------ #

@router.get("/api/events")
async def get_events(user: AuthDep, db: SessionDep, year: int = None, month: int = None):
    now = datetime.now()
    year = year or now.year
    month = month or now.month
    return {"events": _build_calendar_events(user.user_id, year, month, db)}


@router.get("/api/upcoming")
async def get_upcoming(user: AuthDep, db: SessionDep, days: int = 14):
    return {"events": CalendarRepository(db).get_upcoming(user.user_id, days=days)}


@router.post("/api/events/add")
async def add_event(event: CalendarEventCreate, user: AuthDep, db: SessionDep):
    try:
        result = CalendarRepository(db).create(
            user_id=user.user_id,
            title=event.title,
            event_type=CalendarEventType(event.type),
            date=datetime.strptime(event.date, "%Y-%m-%d"),
            description=event.description,
        )
        return {"success": True, "event": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/api/events/{event_id}")
async def delete_event(event_id: int, user: AuthDep, db: SessionDep):
    deleted = CalendarRepository(db).delete(event_id, user.user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Event not found")
    return {"success": True}
