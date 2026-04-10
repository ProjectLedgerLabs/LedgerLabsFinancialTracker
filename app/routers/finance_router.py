from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import Dict, List
from pydantic import BaseModel
from datetime import datetime
import os

router = APIRouter(prefix="/finance", tags=["finance"])

# Get the absolute path to templates
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

# Create templates instance with NO cache
templates = Jinja2Templates(directory=TEMPLATES_DIR)
# Disable template caching completely
templates.env.cache = {}

# ========== SCHEMAS ==========
class IncomeUpdate(BaseModel):
    income: float

# ========== SERVICE LAYER ==========
class FinanceService:
    def __init__(self):
        self.monthly_income = 5000.00
        self.expenses = [
            {"name": "Grocery shopping", "category": "Food", "amount": 156.32, "date": datetime(2026, 4, 5)},
            {"name": "Gas station", "category": "Transportation", "amount": 65.00, "date": datetime(2026, 4, 3)},
            {"name": "Restaurant dinner", "category": "Food", "amount": 89.50, "date": datetime(2026, 4, 1)},
            {"name": "Coffee shop", "category": "Food", "amount": 12.75, "date": datetime(2026, 4, 8)},
            {"name": "Movie tickets", "category": "Entertainment", "amount": 34.00, "date": datetime(2026, 4, 6)},
            {"name": "Gym membership", "category": "Health", "amount": 49.99, "date": datetime(2026, 4, 1)},
            {"name": "Netflix", "category": "Software", "amount": 15.99, "date": datetime(2026, 4, 1)},
            {"name": "Spotify", "category": "Software", "amount": 9.99, "date": datetime(2026, 4, 1)},
            {"name": "Internet bill", "category": "Utilities", "amount": 80.00, "date": datetime(2026, 4, 1)},
            {"name": "Electric bill", "category": "Utilities", "amount": 100.00, "date": datetime(2026, 4, 2)},
        ]
        
        self.budget_limits = {
            "Food": 600, "Transportation": 300, "Entertainment": 200,
            "Health": 150, "Software": 100, "Utilities": 200
        }
        
        self.monthly_expenses_history = [450, 520, 380, 465]
    
    def get_total_expenses(self) -> float:
        return sum(expense["amount"] for expense in self.expenses)
    
    def get_category_spending(self) -> Dict[str, float]:
        categories = {}
        for expense in self.expenses:
            cat = expense["category"]
            amount = expense["amount"]
            categories[cat] = categories.get(cat, 0) + amount
        return categories
    
    def get_burn_rate(self) -> float:
        return self.monthly_income - self.get_total_expenses()
    
    def get_savings_rate(self) -> float:
        burn_rate = self.get_burn_rate()
        return round((burn_rate / self.monthly_income) * 100, 1)
    
    def get_budgets(self) -> List[Dict]:
        spending = self.get_category_spending()
        budgets = []
        color_map = {
            "Food": "blue", "Transportation": "teal", "Entertainment": "sky",
            "Health": "orange", "Software": "brown", "Utilities": "blue"
        }
        
        for category, limit in self.budget_limits.items():
            spent = spending.get(category, 0)
            percentage = round((spent / limit) * 100, 1)
            budgets.append({
                "category": category,
                "limit": limit,
                "spent": round(spent, 2),
                "percentage": percentage,
                "color": color_map.get(category, "blue")
            })
        return budgets
    
    def get_recent_expenses(self, limit: int = 5) -> List[Dict]:
        sorted_expenses = sorted(self.expenses, key=lambda x: x["date"], reverse=True)
        recent = sorted_expenses[:limit]
        return [
            {
                "name": exp["name"],
                "category": exp["category"],
                "amount": round(exp["amount"], 2),
                "date": exp["date"].strftime("%Y-%m-%d")
            }
            for exp in recent
        ]
    
    def get_all_expenses(self) -> List[Dict]:
        return [
            {
                "name": exp["name"],
                "category": exp["category"],
                "amount": round(exp["amount"], 2),
                "date": exp["date"].strftime("%Y-%m-%d")
            }
            for exp in self.expenses
        ]
    
    def update_income(self, new_income: float) -> Dict:
        self.monthly_income = new_income
        return {
            "income": self.monthly_income,
            "burn_rate": round(self.get_burn_rate(), 2),
            "savings_rate": self.get_savings_rate()
        }
    
    def get_dashboard_data(self) -> Dict:
        category_spending = self.get_category_spending()
        return {
            "monthly_income": self.monthly_income,
            "total_expenses": self.get_total_expenses(),
            "burn_rate": self.get_burn_rate(),
            "savings_rate": self.get_savings_rate(),
            "recent_expenses": self.get_recent_expenses(),
            "budgets": self.get_budgets(),
            "category_labels": list(category_spending.keys()),
            "category_values": list(category_spending.values()),
            "monthly_expenses": self.monthly_expenses_history
        }

finance_service = FinanceService()

# ========== PAGE ROUTE ==========
# USING THE WORKING INLINE HTML (KEEPING WHAT WORKS)

@router.get("/dashboard", response_class=HTMLResponse)
async def finance_dashboard(request: Request):
    """Render the main finance dashboard"""
    data = finance_service.get_dashboard_data()
    
    # Working inline HTML (keep this as is - it works!)
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Finance Dashboard</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body>
        <div class="container mt-5">
            <h1>Financial Dashboard</h1>
            <div class="row">
                <div class="col-md-3">
                    <div class="card bg-primary text-white">
                        <div class="card-body">
                            <h5>Monthly Income</h5>
                            <h2>${data['monthly_income']:.2f}</h2>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card bg-success text-white">
                        <div class="card-body">
                            <h5>Total Expenses</h5>
                            <h2>${data['total_expenses']:.2f}</h2>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card bg-warning text-white">
                        <div class="card-body">
                            <h5>Burn Rate</h5>
                            <h2>${data['burn_rate']:.2f}</h2>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card bg-info text-white">
                        <div class="card-body">
                            <h5>Savings Rate</h5>
                            <h2>{data['savings_rate']:.1f}%</h2>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="card mt-4">
                <div class="card-header">
                    <h5>Recent Expenses</h5>
                </div>
                <div class="card-body">
                    <table class="table">
                        <thead>
                            <tr><th>Name</th><th>Category</th><th>Date</th><th>Amount</th></tr>
                        </thead>
                        <tbody>
                            {''.join([f'<tr><td>{e["name"]}</td><td>{e["category"]}</td><td>{e["date"]}</td><td class="text-danger">-${e["amount"]:.2f}</td></tr>' for e in data['recent_expenses']])}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content)

# ========== API ROUTES ==========

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