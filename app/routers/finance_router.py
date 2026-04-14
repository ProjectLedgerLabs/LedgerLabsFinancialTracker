from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from datetime import datetime
from app.routers import templates
from app.dependencies.auth import AuthDep
from app.dependencies.session import SessionDep
from app.utilities.flash import get_flashed_messages
from app.repositories.entry import EntryRepository
from app.repositories.budget import BudgetRepository
from app.models.user import EntryType

router = APIRouter(prefix="/finance", tags=["finance"])

CATEGORY_COLORS = {
    "Food": "#006699", "Transportation": "#669900", "Entertainment": "#ff6600",
    "Health": "#cc3399", "Software": "#99cc33", "Utilities": "#ffcc00",
}


class IncomeUpdate(BaseModel):
    income: float


def _build_budgets(user_id: int, db) -> list:
    """Build budget data using actual budgets from database instead of hardcoded limits."""
    repo = EntryRepository(db)
    category_spending = repo.get_category_spending(user_id)
    budget_repo = BudgetRepository(db)
    budgets = budget_repo.get_all(user_id, category_spending)
    return budgets


def _get_dashboard_data(user_id: int, db) -> dict:
    repo = EntryRepository(db)
    monthly_income = repo.get_monthly_income(user_id)
    total_expenses = repo.get_total_expenses(user_id)
    burn_rate = round(monthly_income - total_expenses, 2)
    savings_rate = round((burn_rate / monthly_income) * 100, 1) if monthly_income > 0 else 0.0

    category_spending = repo.get_category_spending(user_id)
    recent_expenses = repo.get_recent_expenses(user_id, limit=5)
    budgets = _build_budgets(user_id, db)
    expense_history = repo.get_monthly_expense_totals(user_id, num_months=6)

    return {
        "monthly_income": monthly_income,
        "total_expenses": total_expenses,
        "burn_rate": burn_rate,
        "savings_rate": savings_rate,
        "recent_expenses": recent_expenses,
        "budgets": budgets,
        "category_labels": list(category_spending.keys()),
        "category_values": list(category_spending.values()),
        "monthly_expenses_data": expense_history["totals"],
        "monthly_labels": expense_history["labels"],
    }


@router.get("/dashboard", response_class=HTMLResponse)
async def finance_dashboard(request: Request, user: AuthDep, db: SessionDep):
    data = _get_dashboard_data(user.user_id, db)
    return templates.TemplateResponse(
        request=request, name="dashboard.html",
        context={"flash_messages": get_flashed_messages(request), "user": user,
                 "active_page": "dashboard", **data},
    )


@router.get("/api/dashboard-data")
async def get_dashboard_data(user: AuthDep, db: SessionDep):
    return _get_dashboard_data(user.user_id, db)


@router.get("/api/expenses")
async def get_expenses(user: AuthDep, db: SessionDep):
    return {"expenses": EntryRepository(db).get_expenses(user.user_id)}


@router.get("/api/budgets")
async def get_budgets(user: AuthDep, db: SessionDep):
    spending = EntryRepository(db).get_category_spending(user.user_id)
    budget_repo = BudgetRepository(db)
    budgets = budget_repo.get_all(user.user_id, spending)
    return {"budgets": budgets}


@router.post("/api/update-income")
async def update_income(income_data: IncomeUpdate, user: AuthDep, db: SessionDep):
    repo = EntryRepository(db)
    repo.set_monthly_income(user.user_id, income_data.income, date=datetime.now())
    monthly_income = repo.get_monthly_income(user.user_id)
    total_expenses = repo.get_total_expenses(user.user_id)
    burn_rate = round(monthly_income - total_expenses, 2)
    savings_rate = round((burn_rate / monthly_income) * 100, 1) if monthly_income > 0 else 0.0
    return {"income": monthly_income, "burn_rate": burn_rate, "savings_rate": savings_rate}
