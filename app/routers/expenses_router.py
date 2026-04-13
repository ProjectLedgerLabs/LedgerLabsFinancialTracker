from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse
from typing import Dict, List
from pydantic import BaseModel
from datetime import datetime
from app.models.user import ExpenseCreate, ExpensesService
from app.routers import templates
from app.dependencies.auth import AuthDep
from app.utilities.flash import get_flashed_messages

router = APIRouter(prefix="/expenses", tags=["expenses"])

expenses_service = ExpensesService()

# Page Route
@router.get("/", response_class=HTMLResponse)
async def expenses_page(request: Request, user: AuthDep):
    """Render the expenses page"""
    categories = expenses_service.get_expenses_by_category()
    total_expenses = expenses_service.get_total_expenditure()
    
    return templates.TemplateResponse(
        request=request,
        name="expenses.html",
        context={
            "flash_messages": get_flashed_messages(request),
            "user": user,
            "active_page": "expenses",
            "categories": categories,
            "total_expenses": total_expenses,
        }
    )


# API Routes
@router.get("/api/expenses")
async def get_expenses():
    return {"expenses": expenses_service.get_all_expenses()}

@router.get("/api/expenses/categories")
async def get_expenses_by_category():
    return expenses_service.get_expenses_by_category()

@router.get("/api/expenses/total")
async def get_total_expenditure():
    return {"total": expenses_service.get_total_expenditure()}

@router.post("/api/expenses/add")
async def add_expense(expense: ExpenseCreate):
    try:
        result = expenses_service.add_expense(expense)
        return {"success": True, "expense": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))