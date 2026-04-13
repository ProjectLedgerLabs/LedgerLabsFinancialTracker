from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse
from typing import Dict, List
from pydantic import BaseModel
from datetime import datetime
from app.routers import templates
from app.dependencies.auth import AuthDep
from app.utilities.flash import get_flashed_messages

router = APIRouter(prefix="/expenses", tags=["expenses"])

class ExpenseCreate(BaseModel):
    name: str
    category: str
    amount: float
    date: str


class ExpensesService:
    def __init__(self):
        self.expenses = [
            {"name": "Grocery shopping", "category": "Food", "amount": 156.32, "date": "2026-04-05"},
            {"name": "Gas station", "category": "Transportation", "amount": 65.00, "date": "2026-04-03"},
            {"name": "Restaurant dinner", "category": "Food", "amount": 89.50, "date": "2026-04-01"},
            {"name": "Coffee shop", "category": "Food", "amount": 12.75, "date": "2026-04-08"},
            {"name": "Movie tickets", "category": "Entertainment", "amount": 34.00, "date": "2026-04-06"},
            {"name": "Gym membership", "category": "Health", "amount": 49.99, "date": "2026-04-01"},
            {"name": "Netflix", "category": "Software", "amount": 15.99, "date": "2026-04-01"},
            {"name": "Spotify", "category": "Software", "amount": 9.99, "date": "2026-04-01"},
            {"name": "Internet bill", "category": "Utilities", "amount": 80.00, "date": "2026-04-01"},
            {"name": "Electric bill", "category": "Utilities", "amount": 100.00, "date": "2026-04-02"},
        ]
    
    def get_all_expenses(self) -> List[Dict]:
        return self.expenses
    
    def get_expenses_by_category(self) -> Dict[str, Dict]:
        categories = {}
        for expense in self.expenses:
            cat = expense["category"]
            if cat not in categories:
                categories[cat] = {
                    "entries": [],
                    "total": 0,
                    "count": 0
                }
            categories[cat]["entries"].append(expense)
            categories[cat]["total"] += expense["amount"]
            categories[cat]["count"] += 1
        return categories
    
    def get_total_expenditure(self) -> float:
        return sum(expense["amount"] for expense in self.expenses)
    
    def add_expense(self, expense: ExpenseCreate) -> Dict:
        new_expense = expense.dict()
        self.expenses.insert(0, new_expense)
        return new_expense

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