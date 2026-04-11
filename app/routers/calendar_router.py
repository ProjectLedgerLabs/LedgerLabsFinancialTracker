from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse
from typing import Dict, List
from pydantic import BaseModel
from datetime import datetime, timedelta
from calendar import monthrange
from app.routers.sidebar import get_sidebar_html

router = APIRouter(prefix="/calendar", tags=["calendar"])

# Schemas
class CalendarEvent(BaseModel):
    title: str
    date: str
    amount: float
    type: str

# Service layer
class CalendarService:
    def __init__(self):
        self.events = [
            {"title": "Grocery shopping", "date": "2026-04-05", "amount": 156.32, "type": "expense"},
            {"title": "Gas station", "date": "2026-04-03", "amount": 65.00, "type": "expense"},
            {"title": "Restaurant dinner", "date": "2026-04-01", "amount": 89.50, "type": "expense"},
            {"title": "Coffee shop", "date": "2026-04-08", "amount": 12.75, "type": "expense"},
            {"title": "Movie tickets", "date": "2026-04-06", "amount": 34.00, "type": "expense"},
            {"title": "Gym membership", "date": "2026-04-10", "amount": 49.99, "type": "subscription"},
            {"title": "Netflix", "date": "2026-04-15", "amount": 15.99, "type": "subscription"},
            {"title": "Spotify", "date": "2026-04-20", "amount": 9.99, "type": "subscription"},
            {"title": "Internet bill", "date": "2026-04-01", "amount": 80.00, "type": "bill"},
            {"title": "Electric bill", "date": "2026-04-02", "amount": 100.00, "type": "bill"},
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
    
    def get_upcoming_events(self, days: int = 7) -> List[Dict]:
        today = datetime.now().date()
        upcoming = []
        for event in self.events:
            event_date = datetime.strptime(event["date"], "%Y-%m-%d").date()
            if today <= event_date <= today + timedelta(days=days):
                upcoming.append(event)
        return sorted(upcoming, key=lambda x: x["date"])
    
    def add_event(self, event: CalendarEvent) -> Dict:
        new_event = event.dict()
        self.events.append(new_event)
        return new_event

calendar_service = CalendarService()

# Page Route

@router.get("/", response_class=HTMLResponse)
async def calendar_page(request: Request):
    """Render the calendar page with inline HTML"""
    
    now = datetime.now()
    current_year = now.year
    current_month = now.month
    
    year = int(request.query_params.get("year", current_year))
    month = int(request.query_params.get("month", current_month))
    
    events_by_date = calendar_service.get_events_by_month(year, month)
    monthly_totals = calendar_service.get_monthly_totals(year, month)
    upcoming_events = calendar_service.get_upcoming_events(14)
    
    first_day_of_month = datetime(year, month, 1)
    start_weekday = first_day_of_month.weekday()
    start_weekday = (start_weekday + 1) % 7
    
    days_in_month = monthrange(year, month)[1]
    
    if month == 1:
        prev_year, prev_month = year - 1, 12
    else:
        prev_year, prev_month = year, month - 1
    
    if month == 12:
        next_year, next_month = year + 1, 1
    else:
        next_year, next_month = year, month + 1
    

    calendar_html = '<div class="calendar-grid">'
    
    day_names = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    for day_name in day_names:
        calendar_html += f'<div class="calendar-day-header">{day_name}</div>'
    
    for i in range(start_weekday):
        calendar_html += '<div class="calendar-day empty"></div>'
    
    for day in range(1, days_in_month + 1):
        day_str = str(day)
        has_events = day_str in events_by_date
        events_html = ""
        
        if has_events:
            for event in events_by_date[day_str]:
                event_class = event["type"]
                events_html += f'''
                    <div class="calendar-event {event_class}" title="{event['title']} - ${event['amount']:.2f}">
                        <span class="event-dot"></span>
                        <span class="event-title">{event['title'][:15]}</span>
                    </div>
                '''
        
        calendar_html += f'''
            <div class="calendar-day {'has-events' if has_events else ''}">
                <div class="day-number">{day}</div>
                <div class="day-events">
                    {events_html}
                </div>
            </div>
        '''
    
    calendar_html += '</div>'
    
    upcoming_html = ""
    for event in upcoming_events:
        event_date = datetime.strptime(event["date"], "%Y-%m-%d")
        formatted_date = event_date.strftime("%b %d, %Y")
        
        if event["type"] == "expense":
            badge_class = "danger"
            icon = "shopping_cart"
        elif event["type"] == "subscription":
            badge_class = "warning"
            icon = "subscriptions"
        elif event["type"] == "bill":
            badge_class = "info"
            icon = "receipt"
        else:
            badge_class = "success"
            icon = "attach_money"
        
        upcoming_html += f'''
            <div class="upcoming-event-item">
                <div class="event-date">{formatted_date}</div>
                <div class="event-info">
                    <span class="material-symbols-outlined event-icon">{icon}</span>
                    <span class="event-title">{event['title']}</span>
                </div>
                <div class="event-amount text-{badge_class}">${event['amount']:.2f}</div>
            </div>
        '''
    
    username = "User"
    if hasattr(request, "session") and request.session:
        username = request.session.get("username", "User")

    sidebar_html = get_sidebar_html(active_page="calendar")
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>FinancePlan - Calendar</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20,100,1,200" rel="stylesheet">
        <link rel="stylesheet" href="/static/css/calendar.css">
    </head>
    <body>
        <div id="wrapper">
            {sidebar_html}
            
            <div id="content">
                <nav class="navbar navbar-expand-lg bg-white mb-4 px-3 rounded-3 shadow-sm">
                    <button class="btn btn-outline-secondary" id="menu-toggle">
                        <span class="material-symbols-outlined">menu</span>
                    </button>
                    <div class="ms-auto d-flex align-items-center gap-3">
                        <span class="fw-semibold">Welcome, {username}</span>
                    </div>
                </nav>
                
                <div class="container-fluid">
                    <div class="d-flex justify-content-between align-items-center mb-4">
                        <div>
                            <h1>Calendar View</h1>
                            <p class="text-muted">Track spending and income by date</p>
                        </div>
                        <div class="month-navigation">
                            <a href="/calendar/?year={prev_year}&month={prev_month}" class="btn btn-outline-secondary me-2">
                                <span class="material-symbols-outlined">chevron_left</span>
                            </a>
                            <span class="current-month">{datetime(year, month, 1).strftime("%B %Y")}</span>
                            <a href="/calendar/?year={next_year}&month={next_month}" class="btn btn-outline-secondary ms-2">
                                <span class="material-symbols-outlined">chevron_right</span>
                            </a>
                        </div>
                    </div>
                    
                    <div class="row mb-4">
                        <div class="col-md-6">
                            <div class="summary-card income-card">
                                <div class="summary-icon">
                                    <span class="material-symbols-outlined">trending_up</span>
                                </div>
                                <div class="summary-details">
                                    <span class="summary-label">Monthly Income</span>
                                    <span class="summary-value">${monthly_totals['income']:.2f}</span>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="summary-card expense-card">
                                <div class="summary-icon">
                                    <span class="material-symbols-outlined">trending_down</span>
                                </div>
                                <div class="summary-details">
                                    <span class="summary-label">Monthly Expenses</span>
                                    <span class="summary-value text-danger">${monthly_totals['expenses']:.2f}</span>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="calendar-container">
                        {calendar_html}
                    </div>
                    
                    <div class="upcoming-events-container mt-4">
                        <div class="upcoming-header">
                            <h3>Upcoming Events</h3>
                            <span class="material-symbols-outlined">notifications_active</span>
                        </div>
                        <div class="upcoming-events-list">
                            {upcoming_html if upcoming_html else '<div class="text-center text-muted py-4">No upcoming events</div>'}
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/js/bootstrap.bundle.min.js"></script>
        <script src="/static/js/calendar.js"></script>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content)

# API Routes

@router.get("/api/events")
async def get_events(year: int = None, month: int = None):
    if year and month:
        return calendar_service.get_events_by_month(year, month)
    return {"events": calendar_service.events}

@router.get("/api/upcoming")
async def get_upcoming(days: int = 7):
    return {"events": calendar_service.get_upcoming_events(days)}

@router.post("/api/events/add")
async def add_event(event: CalendarEvent):
    try:
        result = calendar_service.add_event(event)
        return {"success": True, "event": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))