from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import Dict, List
from app.routers.sidebar import get_sidebar_html
import json

router = APIRouter(prefix="/reports", tags=["reports"])

templates = Jinja2Templates(directory="app/templates")


# Service Layer

class ReportsService:
    def __init__(self):
        # Monthly spending data (last 6 months)
        self.monthly_data = {
            "labels": ["Nov", "Dec", "Jan", "Feb", "Mar", "Apr"],
            "spending": [4200, 3800, 3433, 3100, 2950, 2800],
            "income": [5000, 5000, 5000, 5000, 5000, 5000]
        }

        self.category_data = {
            "Food": 258.57,
            "Transportation": 65.00,
            "Entertainment": 34.00,
            "Health": 49.99,
            "Software": 30.98,
            "Utilities": 180.00
        }

        self.subscriptions = [
            {"name": "Gym Membership", "amount": 49.99, "nextBilling": "2026-04-10"},
            {"name": "Software Subscription", "amount": 20.00, "nextBilling": "2026-04-12"},
            {"name": "Streaming Service A", "amount": 15.99, "nextBilling": "2026-04-15"},
            {"name": "Music Streaming", "amount": 9.99, "nextBilling": "2026-04-20"}
        ]

        self.current_month_spending = 2800.00
        self.previous_month_spending = 3100.00
        self.average_monthly_spending = 3433.33

        self.savings_data = {
            "total_saved": 9550.00,
            "total_target": 15500.00,
            "progress": 61.6
        }

    def get_monthly_trend(self) -> Dict:
        return self.monthly_data

    def get_category_breakdown(self) -> Dict:
        return self.category_data

    def get_subscription_summary(self) -> Dict:
        total_monthly = sum(sub["amount"] for sub in self.subscriptions)
        total_yearly = total_monthly * 12
        return {
            "monthly_cost": total_monthly,
            "yearly_projection": total_yearly,
            "active_services": len(self.subscriptions),
            "subscriptions": self.subscriptions
        }

    def get_spending_insights(self) -> Dict:
        month_over_month = ((self.current_month_spending - self.previous_month_spending) / self.previous_month_spending) * 100
        return {
            "current_month": self.current_month_spending,
            "previous_month": self.previous_month_spending,
            "average_monthly": self.average_monthly_spending,
            "month_over_month": round(month_over_month, 1),
            "is_decreasing": month_over_month < 0
        }

    def get_savings_summary(self) -> Dict:
        return self.savings_data

    def get_top_expense_categories(self, limit: int = 3) -> List[Dict]:
        sorted_categories = sorted(self.category_data.items(), key=lambda x: x[1], reverse=True)
        return [{"name": cat, "amount": amt} for cat, amt in sorted_categories[:limit]]


reports_service = ReportsService()


# Page Route

@router.get("/", response_class=HTMLResponse)
async def reports_page(request: Request):
    """Render the reports page using a Jinja2 template"""

    username = "User"
    if hasattr(request, "session") and request.session:
        username = request.session.get("username", "User")

    monthly_data = reports_service.get_monthly_trend()
    category_data = reports_service.get_category_breakdown()
    subscription_summary = reports_service.get_subscription_summary()
    spending_insights = reports_service.get_spending_insights()
    savings_summary = reports_service.get_savings_summary()
    top_categories = reports_service.get_top_expense_categories()
    sidebar_html = get_sidebar_html(active_page="reports")

    monthly_labels_json = json.dumps(monthly_data["labels"])
    monthly_spending_json = json.dumps(monthly_data["spending"])
    monthly_income_json = json.dumps(monthly_data["income"])
    category_labels_json = json.dumps(list(category_data.keys()))
    category_values_json = json.dumps(list(category_data.values()))

    return templates.TemplateResponse("reports.html", {
        "request": request,
        "username": username,
        "monthly_data": monthly_data,
        "category_data": category_data,
        "subscription_summary": subscription_summary,
        "spending_insights": spending_insights,
        "savings_summary": savings_summary,
        "top_categories": top_categories,
        "sidebar_html": sidebar_html,
        "monthly_labels_json": monthly_labels_json,
        "monthly_spending_json": monthly_spending_json,
        "monthly_income_json": monthly_income_json,
        "category_labels_json": category_labels_json,
        "category_values_json": category_values_json,
    })


# API Routes

@router.get("/api/monthly-trend")
async def get_monthly_trend():
    return reports_service.get_monthly_trend()

@router.get("/api/category-breakdown")
async def get_category_breakdown():
    return reports_service.get_category_breakdown()

@router.get("/api/subscriptions")
async def get_subscriptions():
    return reports_service.get_subscription_summary()

@router.get("/api/spending-insights")
async def get_spending_insights():
    return reports_service.get_spending_insights()

@router.get("/api/savings-summary")
async def get_savings_summary():
    return reports_service.get_savings_summary()