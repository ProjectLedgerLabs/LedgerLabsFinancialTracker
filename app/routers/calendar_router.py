from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse
from typing import Dict, List
from pydantic import BaseModel
from datetime import datetime, timedelta
from calendar import monthrange
from app.models.user import CalendarService
from app.routers import templates
from app.dependencies.auth import AuthDep
from app.utilities.flash import get_flashed_messages

router = APIRouter(prefix="/calendar", tags=["calendar"])

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
