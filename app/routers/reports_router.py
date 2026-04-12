from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from typing import Dict, List
from app.routers import templates
from app.dependencies.auth import AuthDep
from app.utilities.flash import get_flashed_messages

router = APIRouter(prefix="/reports", tags=["reports"])

class ReportsService:
    def __init__(self):
        self.monthly_labels = ["Nov", "Dec", "Jan", "Feb", "Mar", "Apr"]
        self.monthly_spending = [4200, 3800, 3433, 3100, 2950, 2800]
        self.monthly_income = [5000, 5000, 5000, 5000, 5000, 5000]
        
        self.category_data = {
            "Food": 258.57, "Transportation": 65.00, "Entertainment": 34.00,
            "Health": 49.99, "Software": 30.98, "Utilities": 180.00
        }
        
        self.current_month_spending = 2800.00
        self.previous_month_spending = 3100.00
        self.average_monthly_spending = 3433.33
        
        self._savings_data = {
            "total_saved": 9550.00,
            "total_target": 15500.00,
            "progress": 61.6
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
    
    def get_subscription_summary(self) -> Dict:
        subscriptions = [
            {"name": "Gym Membership", "amount": 49.99, "nextBilling": "2026-04-10"},
            {"name": "Software Subscription", "amount": 20.00, "nextBilling": "2026-04-12"},
            {"name": "Streaming Service A", "amount": 15.99, "nextBilling": "2026-04-15"},
            {"name": "Music Streaming", "amount": 9.99, "nextBilling": "2026-04-20"}
        ]
        total_monthly = sum(sub["amount"] for sub in subscriptions)
        return {
            "monthly_cost": total_monthly,
            "yearly_projection": total_monthly * 12,
            "active_services": len(subscriptions),
            "subscriptions": subscriptions
        }
    
    def get_savings_summary(self) -> Dict:
        return self._savings_data
    
    def get_top_expense_categories(self, limit: int = 3) -> List[Dict]:
        sorted_categories = sorted(self.category_data.items(), key=lambda x: x[1], reverse=True)
        return [{"name": cat, "amount": amt} for cat, amt in sorted_categories[:limit]]

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