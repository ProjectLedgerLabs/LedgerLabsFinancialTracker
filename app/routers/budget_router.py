from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse
from typing import Dict, List
from pydantic import BaseModel
from app.routers.sidebar import get_sidebar_html

router = APIRouter(prefix="/budget", tags=["budget"])


class BudgetUpdate(BaseModel):
    category: str
    limit: float

class BudgetCreate(BaseModel):
    category: str
    limit: float


class BudgetService:
    def __init__(self):
        self.budget_limits = {
            "Food": 600,
            "Transportation": 300,
            "Entertainment": 200,
            "Health": 150,
            "Software": 100,
            "Utilities": 250
        }
        
        self.spending = {
            "Food": 258.57,
            "Transportation": 65.00,
            "Entertainment": 34.00,
            "Health": 49.99,
            "Software": 30.98,
            "Utilities": 180.00
        }
    
    def get_all_budgets(self) -> List[Dict]:
        budgets = []
        for category, limit in self.budget_limits.items():
            spent = self.spending.get(category, 0)
            percentage = round((spent / limit) * 100, 1) if limit > 0 else 0
            remaining = limit - spent
            
            if percentage >= 90:
                status = "danger"
            elif percentage >= 75:
                status = "warning"
            else:
                status = "success"
            
            budgets.append({
                "category": category,
                "limit": round(limit, 2),
                "spent": round(spent, 2),
                "remaining": round(remaining, 2),
                "percentage": percentage,
                "status": status
            })
        return budgets
    
    def get_total_allocated(self) -> float:
        return sum(self.budget_limits.values())
    
    def get_total_spent(self) -> float:
        return sum(self.spending.values())
    
    def get_total_remaining(self) -> float:
        return self.get_total_allocated() - self.get_total_spent()
    
    def get_overall_progress(self) -> float:
        total_allocated = self.get_total_allocated()
        total_spent = self.get_total_spent()
        return round((total_spent / total_allocated) * 100, 1) if total_allocated > 0 else 0
    
    def update_budget_limit(self, category: str, new_limit: float) -> Dict:
        if category in self.budget_limits:
            self.budget_limits[category] = new_limit
            return {"success": True, "category": category, "new_limit": new_limit}
        return {"success": False, "error": "Category not found"}
    
    def add_budget_category(self, category: str, limit: float) -> Dict:
        if category in self.budget_limits:
            return {"success": False, "error": "Category already exists"}
        self.budget_limits[category] = limit
        self.spending[category] = 0
        return {"success": True, "category": category, "limit": limit}

budget_service = BudgetService()

# Page Route
@router.get("/", response_class=HTMLResponse)
async def budget_page(request: Request):
    """Render the budget page with inline HTML"""
    
    username = "User"
    if hasattr(request, "session") and request.session:
        username = request.session.get("username", "User")
    
    budgets = budget_service.get_all_budgets()
    total_allocated = budget_service.get_total_allocated()
    total_spent = budget_service.get_total_spent()
    total_remaining = budget_service.get_total_remaining()
    overall_progress = budget_service.get_overall_progress()
    
    # Build budgets HTML
    budgets_html = ""
    for budget in budgets:
        budgets_html += f'''
        <div class="budget-card" data-category="{budget["category"]}">
            <div class="budget-card-header">
                <div>
                    <h4>{budget["category"]}</h4>
                    <span class="budget-status status-{budget["status"]}">{budget["percentage"]}% used</span>
                </div>
                <button class="edit-budget-btn" data-category="{budget["category"]}" data-limit="{budget["limit"]}">
                    <span class="material-symbols-outlined">edit</span>
                </button>
            </div>
            <div class="budget-amounts">
                <div class="spent">Spent: <strong>${budget["spent"]:.2f}</strong></div>
                <div class="limit">Limit: ${budget["limit"]:.2f}</div>
                <div class="remaining remaining-{budget["status"]}">Remaining: ${budget["remaining"]:.2f}</div>
            </div>
            <div class="progress-bar-container">
                <div class="progress-bar-fill progress-{budget["status"]}" style="width: {budget["percentage"]}%"></div>
            </div>
        </div>
        '''
    
    sidebar_html = get_sidebar_html(active_page="budget")

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>FinancePlan - Budget Management</title>
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
                transition: all 0.2s;
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
            
            .summary-cards {{
                display: grid;
                grid-template-columns: repeat(4, 1fr);
                gap: 20px;
                margin-bottom: 30px;
            }}
            
            .summary-card {{
                background: white;
                border-radius: 12px;
                padding: 20px;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                transition: transform 0.2s;
            }}
            
            .summary-card:hover {{
                transform: translateY(-5px);
            }}
            
            .summary-card.allocated {{ border-left: 4px solid #0d6efd; }}
            .summary-card.spent {{ border-left: 4px solid #dc3545; }}
            .summary-card.remaining {{ border-left: 4px solid #198754; }}
            .summary-card.progress {{ border-left: 4px solid #fd7e14; }}
            
            .summary-card h6 {{
                color: #6c757d;
                font-size: 14px;
                margin-bottom: 10px;
            }}
            
            .summary-card h3 {{
                font-size: 28px;
                font-weight: bold;
                margin: 0;
            }}
            
            .summary-card .progress-text {{
                font-size: 24px;
                font-weight: bold;
                color: #fd7e14;
            }}
            
            .budget-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
                gap: 20px;
                margin-top: 20px;
            }}
            
            .budget-card {{
                background: white;
                border-radius: 12px;
                padding: 20px;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                transition: all 0.2s;
            }}
            
            .budget-card:hover {{
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            }}
            
            .budget-card-header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 15px;
                padding-bottom: 10px;
                border-bottom: 1px solid #e9ecef;
            }}
            
            .budget-card-header h4 {{
                margin: 0;
                font-size: 18px;
                font-weight: 600;
            }}
            
            .budget-status {{
                font-size: 12px;
                padding: 3px 8px;
                border-radius: 20px;
                margin-left: 10px;
            }}
            
            .status-success {{
                background: #d1e7dd;
                color: #0f5132;
            }}
            
            .status-warning {{
                background: #fff3cd;
                color: #856404;
            }}
            
            .status-danger {{
                background: #f8d7da;
                color: #721c24;
            }}
            
            .edit-budget-btn {{
                background: none;
                border: none;
                cursor: pointer;
                padding: 5px;
                border-radius: 4px;
                transition: all 0.2s;
            }}
            
            .edit-budget-btn:hover {{
                background: #e9ecef;
            }}
            
            .budget-amounts {{
                display: flex;
                justify-content: space-between;
                margin-bottom: 15px;
                font-size: 14px;
            }}
            
            .remaining-success {{
                color: #198754;
                font-weight: bold;
            }}
            
            .remaining-warning {{
                color: #fd7e14;
                font-weight: bold;
            }}
            
            .remaining-danger {{
                color: #dc3545;
                font-weight: bold;
            }}
            
            .progress-bar-container {{
                background-color: #e9ecef;
                border-radius: 10px;
                height: 10px;
                overflow: hidden;
            }}
            
            .progress-bar-fill {{
                height: 100%;
                border-radius: 10px;
                transition: width 0.5s ease;
            }}
            
            .progress-success {{
                background-color: #198754;
            }}
            
            .progress-warning {{
                background-color: #fd7e14;
            }}
            
            .progress-danger {{
                background-color: #dc3545;
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
                
                .summary-cards {{
                    grid-template-columns: repeat(2, 1fr);
                }}
                
                .budget-grid {{
                    grid-template-columns: 1fr;
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
            
            .budget-card {{
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
                            <h1>Budget Management</h1>
                            <p class="text-muted">Track spending against your budget</p>
                        </div>
                        <button class="btn btn-primary" id="addCategoryBtn">
                            <span class="material-symbols-outlined">add</span>
                            Add Category
                        </button>
                    </div>
                    
                    <!-- Summary Cards -->
                    <div class="summary-cards">
                        <div class="summary-card allocated">
                            <h6>Total Allocated</h6>
                            <h3>${total_allocated:.2f}</h3>
                        </div>
                        <div class="summary-card spent">
                            <h6>Total Spent</h6>
                            <h3>${total_spent:.2f}</h3>
                        </div>
                        <div class="summary-card remaining">
                            <h6>Total Remaining</h6>
                            <h3>${total_remaining:.2f}</h3>
                        </div>
                        <div class="summary-card progress">
                            <h6>Overall Progress</h6>
                            <div class="progress-text">{overall_progress}%</div>
                            <div class="progress-bar-container mt-2">
                                <div class="progress-bar-fill progress-success" style="width: {overall_progress}%"></div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Budget Grid -->
                    <div class="budget-grid" id="budgetGrid">
                        {budgets_html}
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Edit Budget Modal -->
        <div class="modal fade" id="editBudgetModal" tabindex="-1">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Edit Budget</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <form id="editBudgetForm">
                            <div class="mb-3">
                                <label class="form-label">Category</label>
                                <input type="text" class="form-control" id="editCategory" readonly>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Budget Limit ($)</label>
                                <input type="number" step="0.01" class="form-control" id="editLimit" required>
                            </div>
                        </form>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                        <button type="button" class="btn btn-primary" id="saveBudgetBtn">Save Changes</button>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Add Category Modal -->
        <div class="modal fade" id="addCategoryModal" tabindex="-1">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Add Budget Category</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <form id="addCategoryForm">
                            <div class="mb-3">
                                <label class="form-label">Category Name</label>
                                <input type="text" class="form-control" id="newCategory" required>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Budget Limit ($)</label>
                                <input type="number" step="0.01" class="form-control" id="newLimit" required>
                            </div>
                        </form>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                        <button type="button" class="btn btn-primary" id="createBudgetBtn">Create Budget</button>
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
            
            // Show toast notification
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
            
            // Edit budget modal
            let editModal = null;
            let currentCategory = '';
            
            document.querySelectorAll('.edit-budget-btn').forEach(btn => {{
                btn.addEventListener('click', () => {{
                    const category = btn.getAttribute('data-category');
                    const limit = parseFloat(btn.getAttribute('data-limit'));
                    
                    document.getElementById('editCategory').value = category;
                    document.getElementById('editLimit').value = limit;
                    currentCategory = category;
                    
                    editModal = new bootstrap.Modal(document.getElementById('editBudgetModal'));
                    editModal.show();
                }});
            }});
            
            // Save budget changes
            document.getElementById('saveBudgetBtn')?.addEventListener('click', async () => {{
                const newLimit = parseFloat(document.getElementById('editLimit').value);
                
                if (isNaN(newLimit) || newLimit <= 0) {{
                    showToast('Please enter a valid budget limit', 'error');
                    return;
                }}
                
                const response = await fetch('/budget/api/update', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{
                        category: currentCategory,
                        limit: newLimit
                    }})
                }});
                
                if (response.ok) {{
                    showToast('Budget updated successfully!', 'success');
                    if (editModal) editModal.hide();
                    setTimeout(() => window.location.reload(), 1000);
                }} else {{
                    showToast('Failed to update budget', 'error');
                }}
            }});
            
            // Add category modal
            let addModal = null;
            document.getElementById('addCategoryBtn')?.addEventListener('click', () => {{
                document.getElementById('addCategoryForm').reset();
                addModal = new bootstrap.Modal(document.getElementById('addCategoryModal'));
                addModal.show();
            }});
            
            // Create new budget category
            document.getElementById('createBudgetBtn')?.addEventListener('click', async () => {{
                const category = document.getElementById('newCategory').value.trim();
                const limit = parseFloat(document.getElementById('newLimit').value);
                
                if (!category) {{
                    showToast('Please enter a category name', 'error');
                    return;
                }}
                
                if (isNaN(limit) || limit <= 0) {{
                    showToast('Please enter a valid budget limit', 'error');
                    return;
                }}
                
                const response = await fetch('/budget/api/add', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{
                        category: category,
                        limit: limit
                    }})
                }});
                
                const result = await response.json();
                
                if (result.success) {{
                    showToast('Budget category added successfully!', 'success');
                    if (addModal) addModal.hide();
                    setTimeout(() => window.location.reload(), 1000);
                }} else {{
                    showToast(result.error || 'Failed to add category', 'error');
                }}
            }});
        </script>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content)

# API Routes

@router.get("/api/budgets")
async def get_budgets():
    """Get all budgets"""
    return {"budgets": budget_service.get_all_budgets()}

@router.get("/api/summary")
async def get_budget_summary():
    """Get budget summary"""
    return {
        "total_allocated": budget_service.get_total_allocated(),
        "total_spent": budget_service.get_total_spent(),
        "total_remaining": budget_service.get_total_remaining(),
        "overall_progress": budget_service.get_overall_progress()
    }

@router.post("/api/update")
async def update_budget(budget_update: BudgetUpdate):
    """Update a budget limit"""
    try:
        result = budget_service.update_budget_limit(budget_update.category, budget_update.limit)
        if result["success"]:
            return result
        raise HTTPException(status_code=404, detail=result["error"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/add")
async def add_budget_category(budget_create: BudgetCreate):
    """Add a new budget category"""
    try:
        result = budget_service.add_budget_category(budget_create.category, budget_create.limit)
        if result["success"]:
            return result
        raise HTTPException(status_code=400, detail=result["error"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))