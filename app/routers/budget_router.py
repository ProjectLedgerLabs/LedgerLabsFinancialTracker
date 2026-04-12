from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from app.routers import templates
from app.dependencies.auth import AuthDep
from app.utilities.flash import get_flashed_messages

router = APIRouter(prefix="/budget", tags=["budget"])

CATEGORY_COLORS = {
    "Food": "#006699",
    "Transportation": "#669900",
    "Entertainment": "#ff6600",
    "Health": "#cc3399",
    "Software": "#99cc33",
    "Utilities": "#ffcc00"
}

@router.get("/", response_class=HTMLResponse)
async def budget_page(request: Request, user: AuthDep):
    budgets = [
        {"category": "Food", "limit": 600, "spent": 258.57, "remaining": 341.43, "color": CATEGORY_COLORS["Food"]},
        {"category": "Transportation", "limit": 300, "spent": 65.00, "remaining": 235.00, "color": CATEGORY_COLORS["Transportation"]},
        {"category": "Entertainment", "limit": 200, "spent": 34.00, "remaining": 166.00, "color": CATEGORY_COLORS["Entertainment"]},
        {"category": "Health", "limit": 150, "spent": 49.99, "remaining": 100.01, "color": CATEGORY_COLORS["Health"]},
        {"category": "Software", "limit": 100, "spent": 30.98, "remaining": 69.02, "color": CATEGORY_COLORS["Software"]},
        {"category": "Utilities", "limit": 250, "spent": 180.00, "remaining": 70.00, "color": CATEGORY_COLORS["Utilities"]},
    ]
    
    for b in budgets:
        b["percentage"] = round((b["spent"] / b["limit"]) * 100, 1)
    
    total_allocated = sum(b["limit"] for b in budgets)
    total_spent = sum(b["spent"] for b in budgets)
    overall_progress = round((total_spent / total_allocated) * 100, 1)
    
    return templates.TemplateResponse(
        request=request,
        name="budget.html",
        context={
            "flash_messages": get_flashed_messages(request),
            "user": user,
            "active_page": "budget",
            "budgets": budgets,
            "total_allocated": f"{total_allocated:.2f}",
            "total_spent": f"{total_spent:.2f}",
            "overall_progress": overall_progress,
        }
    )