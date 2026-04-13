from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from typing import Dict, List
from app.models.user import ReportsService
from app.routers import templates
from app.dependencies.auth import AuthDep
from app.utilities.flash import get_flashed_messages

router = APIRouter(prefix="/reports", tags=["reports"])

reports_service = ReportsService()

@router.get("/", response_class=HTMLResponse)
async def reports_page(request: Request, user: AuthDep):
    spending_insights = reports_service.get_spending_insights()
    subscription_summary = reports_service.get_subscription_summary()
    savings_summary = reports_service.get_savings_summary()
    top_categories = reports_service.get_top_expense_categories()
    
    return templates.TemplateResponse(
        request=request,
        name="reports.html",
        context={
            "flash_messages": get_flashed_messages(request),
            "user": user,
            "active_page": "reports",
            "monthly_labels": reports_service.monthly_labels,
            "monthly_spending": reports_service.monthly_spending,
            "monthly_income": reports_service.monthly_income,
            "category_labels": list(reports_service.category_data.keys()),
            "category_values": list(reports_service.category_data.values()),
            "spending_insights": spending_insights,
            "subscription_summary": subscription_summary,
            "savings_summary": savings_summary,
            "top_categories": top_categories,
        }
    )