from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse
from typing import Dict, List
from pydantic import BaseModel
from datetime import datetime
from app.routers.sidebar import get_sidebar_html

router = APIRouter(prefix="/expenses", tags=["expenses"])

# Schemas
class ExpenseCreate(BaseModel):
    name: str
    category: str
    amount: float
    date: str

# Service layer
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
async def expenses_page(request: Request):
    """Render the expenses page with inline HTML"""
    
    username = "User"
    if hasattr(request, "session") and request.session:
        username = request.session.get("username", "User")
    
    categories = expenses_service.get_expenses_by_category()
    total_expenditure = expenses_service.get_total_expenditure()
    
    categories_html = ""
    for category, data in categories.items():
        categories_html += f'''
        <div class="category-section">
            <div class="category-header d-flex justify-content-between align-items-center" data-category="{category}">
                <div class="d-flex align-items-center gap-3">
                    <h4>{category}</h4>
                    <span class="category-badge">{data["count"]} entries</span>
                </div>
                <div class="category-total">${data["total"]:.2f}</div>
            </div>
            <div class="expense-list" id="category-{category.replace(' ', '')}" style="display: block;">
        '''
        
        for expense in data["entries"]:
            categories_html += f'''
                <div class="expense-item d-flex justify-content-between align-items-center">
                    <div>
                        <div class="expense-name">{expense["name"]}</div>
                        <div class="expense-date">{expense["date"]}</div>
                    </div>
                    <div class="d-flex align-items-center gap-3">
                        <span class="expense-amount">-${expense["amount"]:.2f}</span>
                    </div>
                </div>
            '''
        
        categories_html += '''
            </div>
        </div>
        '''
    sidebar_html = get_sidebar_html(active_page ="expenses")

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>FinancePlan - Expense Tracker</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20,100,1,200" rel="stylesheet">
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
            
            #sidebar .nav-link.active {{
                background-color: #0d6efd;
            }}
            
            #content {{
                width: 100%;
                padding: 1rem;
                transition: all 0.3s;
                display: flex;
                flex-direction: column;
                background-color: #f8f9fa;
            }}
            
            .total-card {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 15px 25px;
                border-radius: 12px;
                color: white;
                text-align: center;
                min-width: 200px;
            }}
            
            .total-card small {{
                font-size: 12px;
                opacity: 0.9;
            }}
            
            .total-card h3 {{
                margin: 5px 0 0;
                font-size: 28px;
                font-weight: bold;
            }}
            
            .category-section {{
                background: white;
                border-radius: 12px;
                margin-bottom: 24px;
                overflow: hidden;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            }}
            
            .category-header {{
                background: #f8f9fa;
                padding: 15px 20px;
                border-bottom: 2px solid #e9ecef;
                cursor: pointer;
                transition: background 0.2s;
            }}
            
            .category-header:hover {{
                background: #e9ecef;
            }}
            
            .category-header h4 {{
                margin: 0;
                font-size: 18px;
                font-weight: 600;
            }}
            
            .category-badge {{
                background: #0d6efd;
                color: white;
                padding: 4px 10px;
                border-radius: 20px;
                font-size: 12px;
            }}
            
            .category-total {{
                font-size: 18px;
                font-weight: bold;
                color: #198754;
            }}
            
            .expense-list {{
                padding: 0;
            }}
            
            .expense-item {{
                padding: 15px 20px;
                border-bottom: 1px solid #e9ecef;
                transition: background 0.2s;
            }}
            
            .expense-item:hover {{
                background: #f8f9fa;
            }}
            
            .expense-item:last-child {{
                border-bottom: none;
            }}
            
            .expense-name {{
                font-weight: 500;
                margin-bottom: 4px;
            }}
            
            .expense-date {{
                font-size: 12px;
                color: #6c757d;
            }}
            
            .expense-amount {{
                font-size: 16px;
                font-weight: 600;
                color: #dc3545;
            }}
            
            .btn-primary {{
                background-color: #0d6efd;
                border: none;
                padding: 10px 24px;
                border-radius: 8px;
                color: white;
                cursor: pointer;
                display: inline-flex;
                align-items: center;
                gap: 8px;
                transition: all 0.2s;
            }}
            
            .btn-primary:hover {{
                background-color: #0b5ed7;
                transform: translateY(-2px);
            }}
            
            .btn-secondary {{
                background-color: #6c757d;
                border: none;
                padding: 8px 20px;
                border-radius: 6px;
                color: white;
                cursor: pointer;
            }}
            
            .modal-content {{
                border-radius: 12px;
            }}
            
            @media (max-width: 768px) {{
                #sidebar {{
                    transform: translateX(-100%);
                    position: fixed;
                    z-index: 1000;
                }}
                
                #sidebar.collapsed {{
                    transform: translateX(0);
                }}
                
                #content {{
                    margin-left: 0;
                }}
                
                .total-card {{
                    min-width: 150px;
                    padding: 10px 15px;
                }}
                
                .total-card h3 {{
                    font-size: 20px;
                }}
            }}
            
            @keyframes fadeIn {{
                from {{
                    opacity: 0;
                    transform: translateY(10px);
                }}
                to {{
                    opacity: 1;
                    transform: translateY(0);
                }}
            }}
            
            .category-section {{
                animation: fadeIn 0.3s ease-out;
            }}
        </style>
    </head>
    <body>
        <div id="wrapper">
            {sidebar_html}
            
            <div id="content">
                <!-- Top Navbar -->
                <nav class="navbar navbar-expand-lg bg-white mb-4 px-3 rounded-3 shadow-sm">
                    <button class="btn btn-outline-secondary" id="menu-toggle">
                        <span class="material-symbols-outlined">menu</span>
                    </button>
                    <div class="ms-auto d-flex align-items-center gap-3">
                        <span class="fw-semibold">Welcome, {username}</span>
                    </div>
                </nav>
                
                <div class="container-fluid">
                    <!-- Header -->
                    <div class="d-flex justify-content-between align-items-center mb-4">
                        <div>
                            <h1>Expense Tracker</h1>
                            <p class="text-muted">Track and manage your spending</p>
                        </div>
                        <div class="text-end">
                            <div class="total-card">
                                <small>Total Expenditure</small>
                                <h3>${total_expenditure:.2f}</h3>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Add Expense Button -->
                    <div class="mb-4">
                        <button class="btn btn-primary" id="addExpenseBtn">
                            <span class="material-symbols-outlined">add</span>
                            New Entry
                        </button>
                    </div>
                    
                    <!-- Expense Categories -->
                    {categories_html}
                </div>
            </div>
        </div>
        
        <!-- Add Expense Modal -->
        <div class="modal fade" id="addExpenseModal" tabindex="-1">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Add New Expense</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <form id="addExpenseForm">
                            <div class="mb-3">
                                <label class="form-label">Expense Name</label>
                                <input type="text" class="form-control" id="expenseName" required>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Category</label>
                                <select class="form-select" id="expenseCategory">
                                    <option value="Food">Food</option>
                                    <option value="Transportation">Transportation</option>
                                    <option value="Entertainment">Entertainment</option>
                                    <option value="Health">Health</option>
                                    <option value="Software">Software</option>
                                    <option value="Utilities">Utilities</option>
                                </select>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Amount ($)</label>
                                <input type="number" step="0.01" class="form-control" id="expenseAmount" required>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Date</label>
                                <input type="date" class="form-control" id="expenseDate" required>
                            </div>
                        </form>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                        <button type="button" class="btn btn-primary" id="saveExpenseBtn">Save Expense</button>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Toast Notification -->
        <div class="position-fixed bottom-0 end-0 p-3" style="z-index: 11">
            <div id="liveToast" class="toast" role="alert" aria-live="assertive" aria-atomic="true" data-bs-autohide="true" data-bs-delay="3000">
                <div class="toast-header">
                    <strong class="me-auto">Notification</strong>
                    <button type="button" class="btn-close" data-bs-dismiss="toast"></button>
                </div>
                <div class="toast-body"></div>
            </div>
        </div>
        
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/js/bootstrap.bundle.min.js"></script>
        <script>
            // Toggle sidebar
            document.getElementById('menu-toggle')?.addEventListener('click', () => {{
                document.getElementById('sidebar').classList.toggle('collapsed');
            }});
            
            // Toggle category sections
            document.querySelectorAll('.category-header').forEach(header => {{
                header.addEventListener('click', () => {{
                    const category = header.getAttribute('data-category');
                    const list = document.getElementById(`category-${{category.replace(/ /g, '')}}`);
                    if (list) {{
                        const isVisible = list.style.display !== 'none';
                        list.style.display = isVisible ? 'none' : 'block';
                    }}
                }});
            }});
            
            // Show toast
            function showToast(message, type = 'success') {{
                const toastElement = document.getElementById('liveToast');
                const toastBody = toastElement.querySelector('.toast-body');
                const toastHeader = toastElement.querySelector('.toast-header');
                
                toastBody.textContent = message;
                
                if (type === 'success') {{
                    toastHeader.style.backgroundColor = '#198754';
                    toastHeader.style.color = 'white';
                }} else {{
                    toastHeader.style.backgroundColor = '#dc3545';
                    toastHeader.style.color = 'white';
                }}
                
                const toast = new bootstrap.Toast(toastElement);
                toast.show();
                
                setTimeout(() => {{
                    toastHeader.style.backgroundColor = '';
                    toastHeader.style.color = '';
                }}, 3000);
            }}
            
            // Add expense modal
            const addBtn = document.getElementById('addExpenseBtn');
            const saveBtn = document.getElementById('saveExpenseBtn');
            let modal = null;
            
            if (addBtn) {{
                addBtn.addEventListener('click', () => {{
                    document.getElementById('addExpenseForm').reset();
                    document.getElementById('expenseDate').value = new Date().toISOString().split('T')[0];
                    modal = new bootstrap.Modal(document.getElementById('addExpenseModal'));
                    modal.show();
                }});
            }}
            
            if (saveBtn) {{
                saveBtn.addEventListener('click', async () => {{
                    const name = document.getElementById('expenseName').value.trim();
                    const category = document.getElementById('expenseCategory').value;
                    const amount = parseFloat(document.getElementById('expenseAmount').value);
                    const date = document.getElementById('expenseDate').value;
                    
                    if (!name) {{
                        showToast('Please enter an expense name', 'error');
                        return;
                    }}
                    
                    if (isNaN(amount) || amount <= 0) {{
                        showToast('Please enter a valid amount', 'error');
                        return;
                    }}
                    
                    const response = await fetch('/expenses/api/expenses/add', {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify({{ name, category, amount, date }})
                    }});
                    
                    if (response.ok) {{
                        showToast('Expense added successfully!', 'success');
                        if (modal) modal.hide();
                        setTimeout(() => window.location.reload(), 1000);
                    }} else {{
                        showToast('Failed to add expense', 'error');
                    }}
                }});
            }}
        </script>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content)

# API Routes

@router.get("/api/expenses")
async def get_expenses():
    """Get all expenses"""
    return {"expenses": expenses_service.get_all_expenses()}

@router.get("/api/expenses/categories")
async def get_expenses_by_category():
    """Get expenses grouped by category"""
    return expenses_service.get_expenses_by_category()

@router.get("/api/expenses/total")
async def get_total_expenditure():
    """Get total expenditure"""
    return {"total": expenses_service.get_total_expenditure()}

@router.post("/api/expenses/add")
async def add_expense(expense: ExpenseCreate):
    """Add a new expense"""
    try:
        result = expenses_service.add_expense(expense)
        return {"success": True, "expense": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))