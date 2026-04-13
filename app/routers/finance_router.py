from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse
from typing import Dict, List
from pydantic import BaseModel
from datetime import datetime
from app.models.user import FinanceService, IncomeUpdate
from app.routers import templates
from app.dependencies.auth import AuthDep
from app.utilities.flash import get_flashed_messages

router = APIRouter(prefix="/finance", tags=["finance"])

finance_service = FinanceService()

@router.get("/dashboard", response_class=HTMLResponse)
async def finance_dashboard(request: Request, user: AuthDep):
    data = finance_service.get_dashboard_data()

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "flash_messages": get_flashed_messages(request),
            "user": user,
            "active_page": "dashboard",
            "monthly_income": data["monthly_income"],
            "total_expenses": data["total_expenses"],
            "burn_rate": data["burn_rate"],
            "savings_rate": data["savings_rate"],
            "recent_expenses": data["recent_expenses"],
            "budgets": data["budgets"],
            "category_labels": data["category_labels"],
            "category_values": data["category_values"],
            "monthly_expenses_data": data["monthly_expenses_data"],
            "monthly_labels": data["monthly_labels"],
        }
    )

@router.get("/api/dashboard-data")
async def get_dashboard_data():
    return finance_service.get_dashboard_data()

@router.post("/api/update-income")
async def update_income(income_data: IncomeUpdate):
    try:
        result = finance_service.update_income(income_data.income)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/expenses")
async def get_expenses():
    try:
        expenses = finance_service.get_all_expenses()
        return {"expenses": expenses}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/budgets")
async def get_budgets():
    try:
        budgets = finance_service.get_budgets()
        return {"budgets": budgets}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))