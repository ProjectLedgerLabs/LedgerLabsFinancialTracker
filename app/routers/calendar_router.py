from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse
from typing import Dict, List
from pydantic import BaseModel
from datetime import datetime, timedelta
from calendar import monthrange
from app.routers import templates
from app.dependencies.auth import AuthDep
from app.utilities.flash import get_flashed_messages

router = APIRouter(prefix="/calendar", tags=["calendar"])

class CalendarEvent(BaseModel):
    title: str
    date: str
    amount: float
    type: str

class CalendarService:
    def __init__(self):
        self.events = [
            {"title": "Grocery shopping", "date": "2026-04-05", "amount": 156.32, "type": "expense"},
            {"title": "Gas station", "date": "2026-04-03", "amount": 65.00, "type": "expense"},
            {"title": "Restaurant dinner", "date": "2026-04-01", "amount": 89.50, "type": "expense"},
            {"title": "Gym membership", "date": "2026-04-10", "amount": 49.99, "type": "subscription"},
            {"title": "Netflix", "date": "2026-04-15", "amount": 15.99, "type": "subscription"},
            {"title": "Internet bill", "date": "2026-04-01", "amount": 80.00, "type": "bill"},
            {"title": "Salary", "date": "2026-04-15", "amount": 5000.00, "type": "income"},
        ]
    
    def get_events_by_month(self, year: int, month: int) -> Dict[str, List]:
        events_by_date = {}
        for event in self.events:
            event_date = datetime.strptime(event["date"], "%Y-%m-%d")
            if event_date.year == year and event_date.month == month:
                day = str(event_date.day)
                if day not in events_by_date:
                    events_by_date[day] = []
                events_by_date[day].append(event)
        return events_by_date
    
    def get_monthly_totals(self, year: int, month: int) -> Dict:
        total_expenses = 0
        total_income = 0
        for event in self.events:
            event_date = datetime.strptime(event["date"], "%Y-%m-%d")
            if event_date.year == year and event_date.month == month:
                if event["type"] in ["expense", "subscription", "bill"]:
                    total_expenses += event["amount"]
                elif event["type"] == "income":
                    total_income += event["amount"]
        return {"expenses": total_expenses, "income": total_income}
    
    def get_upcoming_events(self, days: int = 14) -> List[Dict]:
        today = datetime.now().date()
        upcoming = []
        for event in self.events:
            event_date = datetime.strptime(event["date"], "%Y-%m-%d").date()
            if today <= event_date <= today + timedelta(days=days):
                upcoming.append(event)
        return sorted(upcoming, key=lambda x: x["date"])

calendar_service = CalendarService()

# Page Route
@router.get("/", response_class=HTMLResponse)
async def calendar_page(request: Request, user: AuthDep):
    now = datetime.now()
    current_year = now.year
    current_month = now.month
    
    year = int(request.query_params.get("year", current_year))
    month = int(request.query_params.get("month", current_month))
    
    events_by_date = calendar_service.get_events_by_month(year, month)
    monthly_totals = calendar_service.get_monthly_totals(year, month)
    upcoming_events = calendar_service.get_upcoming_events(14)
    
    first_day_of_month = datetime(year, month, 1)
    start_weekday = (first_day_of_month.weekday() + 1) % 7
    days_in_month = monthrange(year, month)[1]
    
    # Calculate previous/next months
    if month == 1:
        prev_year, prev_month = year - 1, 12
    else:
        prev_year, prev_month = year, month - 1
    
    if month == 12:
        next_year, next_month = year + 1, 1
    else:
        next_year, next_month = year, month + 1
    
    month_names = ["January", "February", "March", "April", "May", "June",
                   "July", "August", "September", "October", "November", "December"]
    
    return templates.TemplateResponse(
        request=request,
        name="calendar.html",
        context={
            "flash_messages": get_flashed_messages(request),
            "user": user,
            "active_page": "calendar",
            "year": year,
            "month": month,
            "current_month_name": month_names[month - 1],
            "prev_year": prev_year,
            "prev_month": prev_month,
            "next_year": next_year,
            "next_month": next_month,
            "start_weekday": start_weekday,
            "days_in_month": days_in_month,
            "events_by_date": events_by_date,
            "monthly_totals": monthly_totals,
            "upcoming_events": upcoming_events,
        }
    )
