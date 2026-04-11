from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse
from typing import Dict, List
from pydantic import BaseModel
from datetime import datetime
import os

router = APIRouter(prefix="/finance", tags=["finance"])

# Helper functions for HTML rendering
def render_budgets(budgets):
    """Helper to render budget HTML"""
    html = ""
    for budget in budgets:
        html += f'''
        <div class="budget-row mb-3">
            <div class="d-flex justify-content-between mb-1">
                <span>{budget["category"]}</span>
                <span>${budget["spent"]:.2f} / ${budget["limit"]:.2f}</span>
            </div>
            <div class="progress-bar-custom">
                <div class="progress-fill bg-{budget["color"]}" style="width: {budget["percentage"]}%;"></div>
            </div>
        </div>
        '''
    return html

def render_expenses(expenses):
    """Helper to render expenses HTML"""
    html = ""
    for expense in expenses:
        html += f'''
        <div class="list-group-item expense-row d-flex justify-content-between align-items-center">
            <div>
                <h6 class="mb-0">{expense["name"]}</h6>
                <small class="text-muted">{expense["category"]} • {expense["date"]}</small>
            </div>
            <span class="text-danger">-${expense["amount"]:.2f}</span>
        </div>
        '''
    return html

# Schemas
class IncomeUpdate(BaseModel):
    income: float

# Service Layer
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

# Page Route

@router.get("/dashboard", response_class=HTMLResponse)
async def finance_dashboard(request: Request):
    """Render the main finance dashboard with sidebar"""
    data = finance_service.get_dashboard_data()
    
    username = "User"
    if hasattr(request, "session") and request.session:
        username = request.session.get("username", "User")
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>FinancePlan - Financial Dashboard</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20,100,1,200" rel="stylesheet">
        <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                overflow-x: hidden;
                background-color: #f8f9fa;
            }}
            
            #wrapper {{
                display: flex;
            }}
            
            #sidebar {{
                min-width: 250px;
                max-width: 250px;
                min-height: 100vh;
                transition: all 0.3s;
                background: #1b263b;
                color: #fff;
            }}
            
            #sidebar.collapsed {{
                margin-left: -250px;
            }}
            
            #sidebar .nav-link {{
                color: #adb5bd;
                font-weight: 500;
            }}
            
            #sidebar .nav-link:hover,
            #sidebar .nav-link.active {{
                color: #fff;
                background-color: #415a77;
                border-radius: 0.5rem;
            }}
            
            #content {{
                width: 100%;
                padding: 1rem;
                transition: all 0.3s;
                display: flex;
                flex-direction: column;
                background-color: #f8f9fa;
            }}
            
            .card {{
                border: none;
                border-radius: 1rem;
            }}
            
            .stat-card {{
                border-left: 4px solid;
                transition: transform 0.2s;
            }}
            
            .stat-card:hover {{
                transform: translateY(-5px);
            }}
            
            .blue-card {{ border-left-color: #0d6efd; }}
            .teal-card {{ border-left-color: #20c997; }}
            .orange-card {{ border-left-color: #fd7e14; }}
            .brown-card {{ border-left-color: #6c757d; }}
            
            .chart-container {{
                height: 300px;
                position: relative;
            }}
            
            .progress-bar-custom {{
                background-color: #e9ecef;
                border-radius: 10px;
                overflow: hidden;
            }}
            
            .progress-fill {{
                transition: width 0.5s ease;
                height: 8px;
                border-radius: 10px;
            }}
            
            .bg-blue {{ background-color: #0d6efd; }}
            .bg-teal {{ background-color: #20c997; }}
            .bg-sky {{ background-color: #0dcaf0; }}
            .bg-orange {{ background-color: #fd7e14; }}
            .bg-brown {{ background-color: #6c757d; }}
            
            .expense-row, .budget-row {{
                transition: background-color 0.2s;
            }}
            
            .expense-row:hover, .budget-row:hover {{
                background-color: #f8f9fa;
            }}
            
            .btn-primary {{
                background-color: #0d6efd;
                border: none;
                padding: 8px 20px;
                border-radius: 4px;
                color: white;
                cursor: pointer;
            }}
            
            .btn-primary:hover {{
                background-color: #0b5ed7;
            }}
            
            .btn-outline-primary {{
                background-color: transparent;
                border: 1px solid #0d6efd;
                padding: 6px 12px;
                border-radius: 4px;
                color: #0d6efd;
                cursor: pointer;
            }}
            
            .btn-outline-primary:hover {{
                background-color: #0d6efd;
                color: white;
            }}
        </style>
    </head>
    <body>
        <div id="wrapper">
            <!-- Sidebar -->
            <nav id="sidebar" class="p-3 d-flex flex-column vh-100">
                <h4 class="text-white mb-4 text-center py-4">FinancePlan</h4>
                
                <ul class="nav nav-pills flex-column gap-2 flex-grow-1">
                    <li class="nav-item">
                        <a class="nav-link d-flex align-items-center active" href="/finance/dashboard">
                            <span class="material-symbols-outlined me-2">dashboard</span>
                            Dashboard
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link d-flex align-items-center active" href="/budget/">
                            <span class="material-symbols-outlined me-2">account_balance</span>
                            Budget
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link d-flex align-items-center" href="/expenses/">
                            <span class="material-symbols-outlined me-2">receipt</span>
                            Expenses
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link d-flex align-items-center active" href="/subscriptions/">
                            <span class="material-symbols-outlined me-2">subscriptions</span>
                            Subscriptions
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link d-flex align-items-center active" href="/reports/">
                            <span class="material-symbols-outlined me-2">bar_chart</span>
                            Reports
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link d-flex align-items-center" href="/savings/">
                            <span class="material-symbols-outlined me-2">savings</span>
                            Savings
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link d-flex align-items-center" href="/calendar/">
                            <span class="material-symbols-outlined me-2">calendar_month</span>
                            Calendar
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link d-flex align-items-center" href="/ai-assistant/">
                            <span class="material-symbols-outlined me-2">smart_toy</span>
                            AI Assistant
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link d-flex align-items-center" href="/app">
                            <span class="material-symbols-outlined me-2">people</span>
                            Users
                        </a>
                    </li>
                    <li class="nav-item mt-auto">
                        <a class="nav-link d-flex align-items-center text-danger" href="/logout">
                            <span class="material-symbols-outlined me-2">logout</span>
                            Logout
                        </a>
                    </li>
                </ul>
            </nav>
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
                        <h1>Financial Dashboard</h1>
                        <button class="btn-primary" id="setIncomeBtn">Set Income</button>
                    </div>
                    
                    <!-- Stats Cards -->
                    <div class="row mb-4">
                        <div class="col-md-3">
                            <div class="card stat-card blue-card">
                                <div class="card-body">
                                    <h6 class="card-subtitle mb-2 text-muted">Monthly Income</h6>
                                    <h2 class="card-title mb-0" id="monthlyIncome">${data['monthly_income']:.2f}</h2>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="card stat-card teal-card">
                                <div class="card-body">
                                    <h6 class="card-subtitle mb-2 text-muted">Total Expenses</h6>
                                    <h2 class="card-title mb-0" id="totalExpenses">${data['total_expenses']:.2f}</h2>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="card stat-card orange-card">
                                <div class="card-body">
                                    <h6 class="card-subtitle mb-2 text-muted">Burn Rate</h6>
                                    <h2 class="card-title mb-0" id="burnRate">${data['burn_rate']:.2f}</h2>
                                    <span class="badge bg-success mt-2">Surplus</span>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="card stat-card brown-card">
                                <div class="card-body">
                                    <h6 class="card-subtitle mb-2 text-muted">Savings Rate</h6>
                                    <h2 class="card-title mb-0" id="savingsRate">{data['savings_rate']:.1f}%</h2>
                                    <small class="text-muted">of income</small>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Chart -->
                    <div class="card mb-4">
                        <div class="card-header bg-white">
                            <h5 class="mb-0">Income vs Expenses Trend</h5>
                        </div>
                        <div class="card-body">
                            <div class="chart-container">
                                <canvas id="incomeExpensesChart"></canvas>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Two Columns -->
                    <div class="row mb-4">
                        <div class="col-lg-6">
                            <div class="card h-100">
                                <div class="card-header bg-white">
                                    <h5 class="mb-0">Spending by Category</h5>
                                </div>
                                <div class="card-body">
                                    <div class="chart-container">
                                        <canvas id="categoryChart"></canvas>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="col-lg-6">
                            <div class="card h-100">
                                <div class="card-header bg-white">
                                    <h5 class="mb-0">Budget Progress</h5>
                                </div>
                                <div class="card-body">
                                    <div id="budgetProgressList">
                                        {render_budgets(data['budgets'])}
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Recent Expenses -->
                    <div class="card">
                        <div class="card-header bg-white d-flex justify-content-between align-items-center">
                            <h5 class="mb-0">Recent Expenses</h5>
                            <button class="btn-outline-primary" id="refreshExpensesBtn">
                                <span class="material-symbols-outlined">refresh</span>
                            </button>
                        </div>
                        <div class="card-body p-0">
                            <div class="list-group list-group-flush" id="recentExpensesList">
                                {render_expenses(data['recent_expenses'])}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <script>
            // Chart data
            const monthlyIncome = {data['monthly_income']};
            const monthlyExpensesHistory = {data['monthly_expenses']};
            const categoryLabels = {data['category_labels']};
            const categoryValues = {data['category_values']};
            
            let incomeChart = null;
            let categoryChart = null;
            
            function initIncomeExpensesChart() {{
                const canvas = document.getElementById('incomeExpensesChart');
                if (!canvas) return;
                const ctx = canvas.getContext('2d');
                const months = ['Jan', 'Feb', 'Mar', 'Apr'];
                const incomeData = [monthlyIncome, monthlyIncome, monthlyIncome, monthlyIncome];
                
                if (incomeChart) incomeChart.destroy();
                incomeChart = new Chart(ctx, {{
                    type: 'line',
                    data: {{
                        labels: months,
                        datasets: [
                            {{ label: 'Income', data: incomeData, borderColor: '#0d6efd', backgroundColor: 'rgba(13, 110, 253, 0.1)', fill: true, tension: 0.4, borderWidth: 2 }},
                            {{ label: 'Expenses', data: monthlyExpensesHistory, borderColor: '#fd7e14', backgroundColor: 'rgba(253, 126, 20, 0.1)', fill: true, tension: 0.4, borderWidth: 2 }}
                        ]
                    }},
                    options: {{
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {{ legend: {{ position: 'bottom' }}, tooltip: {{ callbacks: {{ label: function(context) {{ return context.dataset.label + ': $' + context.raw.toFixed(2); }} }} }} }},
                        scales: {{ y: {{ beginAtZero: true, ticks: {{ callback: function(value) {{ return '$' + value; }} }} }} }}
                    }}
                }});
            }}
            
            function initCategoryChart() {{
                const canvas = document.getElementById('categoryChart');
                if (!canvas) return;
                const ctx = canvas.getContext('2d');
                const colors = ['#0d6efd', '#20c997', '#0dcaf0', '#fd7e14', '#6c757d', '#d63384'];
                
                if (categoryChart) categoryChart.destroy();
                categoryChart = new Chart(ctx, {{
                    type: 'doughnut',
                    data: {{ labels: categoryLabels, datasets: [{{ data: categoryValues, backgroundColor: colors.slice(0, categoryLabels.length), borderWidth: 2, borderColor: '#fff' }}] }},
                    options: {{ responsive: true, maintainAspectRatio: false, plugins: {{ legend: {{ position: 'bottom' }}, tooltip: {{ callbacks: {{ label: function(context) {{ return context.label + ': $' + context.raw.toFixed(2); }} }} }} }} }}
                }});
            }}
            
            async function updateIncome(newIncome) {{
                const response = await fetch('/finance/api/update-income', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ income: newIncome }})
                }});
                if (response.ok) window.location.reload();
            }}
            
            document.getElementById('setIncomeBtn')?.addEventListener('click', () => {{
                const newIncome = prompt('Enter your monthly income:', monthlyIncome);
                if (newIncome && !isNaN(newIncome)) updateIncome(parseFloat(newIncome));
            }});
            
            document.getElementById('menu-toggle')?.addEventListener('click', () => {{
                document.getElementById('sidebar').classList.toggle('collapsed');
            }});
            
            document.getElementById('refreshExpensesBtn')?.addEventListener('click', async () => {{
                const response = await fetch('/finance/api/expenses');
                if (response.ok) {{
                    const data = await response.json();
                    const expensesList = document.getElementById('recentExpensesList');
                    if (expensesList && data.expenses) {{
                        expensesList.innerHTML = '';
                        data.expenses.slice(0, 5).forEach(expense => {{
                            const expenseDiv = document.createElement('div');
                            expenseDiv.className = 'list-group-item expense-row d-flex justify-content-between align-items-center';
                            expenseDiv.innerHTML = `
                                <div>
                                    <h6 class="mb-0">${{expense.name}}</h6>
                                    <small class="text-muted">${{expense.category}} • ${{expense.date}}</small>
                                </div>
                                <span class="text-danger">-$${{expense.amount}}</span>
                            `;
                            expensesList.appendChild(expenseDiv);
                        }});
                    }}
                }}
            }});
            
            initIncomeExpensesChart();
            initCategoryChart();
        </script>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content)

# API Routes

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