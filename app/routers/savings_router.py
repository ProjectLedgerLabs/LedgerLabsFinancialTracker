from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse
from typing import Dict, List
from pydantic import BaseModel
from datetime import datetime, timedelta

router = APIRouter(prefix="/savings", tags=["savings"])

# ========== SCHEMAS ==========
class SavingsGoalCreate(BaseModel):
    name: str
    target: float
    current: float
    target_date: str

class SavingsContribution(BaseModel):
    goal_name: str
    amount: float

# ========== SERVICE LAYER ==========
class SavingsService:
    def __init__(self):
        self.savings_goals = [
            {
                "name": "Emergency Fund",
                "current": 6500.00,
                "target": 10000.00,
                "target_date": "2026-12-31",
                "days_left": 266
            },
            {
                "name": "Vacation",
                "current": 1200.00,
                "target": 3000.00,
                "target_date": "2026-08-15",
                "days_left": 128
            },
            {
                "name": "New Laptop",
                "current": 1850.00,
                "target": 2500.00,
                "target_date": "2026-06-30",
                "days_left": 82
            }
        ]
    
    def get_all_goals(self) -> List[Dict]:
        today = datetime.now().date()
        for goal in self.savings_goals:
            target_date = datetime.strptime(goal["target_date"], "%Y-%m-%d").date()
            days_left = (target_date - today).days
            goal["days_left"] = max(0, days_left)
        return self.savings_goals
    
    def get_total_saved(self) -> float:
        return sum(goal["current"] for goal in self.savings_goals)
    
    def get_total_target(self) -> float:
        return sum(goal["target"] for goal in self.savings_goals)
    
    def get_overall_progress(self) -> float:
        total_saved = self.get_total_saved()
        total_target = self.get_total_target()
        return round((total_saved / total_target) * 100, 1) if total_target > 0 else 0
    
    def contribute_to_goal(self, goal_name: str, amount: float) -> Dict:
        for goal in self.savings_goals:
            if goal["name"] == goal_name:
                goal["current"] += amount
                return {"success": True, "goal": goal}
        return {"success": False, "error": "Goal not found"}
    
    def add_goal(self, goal: SavingsGoalCreate) -> Dict:
        target_date = datetime.strptime(goal.target_date, "%Y-%m-%d").date()
        days_left = (target_date - datetime.now().date()).days
        
        new_goal = {
            "name": goal.name,
            "current": goal.current,
            "target": goal.target,
            "target_date": goal.target_date,
            "days_left": max(0, days_left)
        }
        self.savings_goals.append(new_goal)
        return new_goal

savings_service = SavingsService()

# ========== PAGE ROUTE ==========

@router.get("/", response_class=HTMLResponse)
async def savings_page(request: Request):
    username = "User"
    if hasattr(request, "session") and request.session:
        username = request.session.get("username", "User")
    
    goals = savings_service.get_all_goals()
    total_saved = savings_service.get_total_saved()
    total_target = savings_service.get_total_target()
    overall_progress = savings_service.get_overall_progress()
    
    goals_html = ""
    for goal in goals:
        progress = (goal["current"] / goal["target"]) * 100
        remaining = goal["target"] - goal["current"]
        
        if progress >= 75:
            color_class = "bg-success"
        elif progress >= 50:
            color_class = "bg-info"
        elif progress >= 25:
            color_class = "bg-warning"
        else:
            color_class = "bg-danger"
        
        goals_html += f'''
        <div class="goal-card" data-goal-name="{goal['name']}">
            <div class="goal-header">
                <div>
                    <h3 class="goal-title">{goal['name']}</h3>
                    <span class="goal-days">{goal['days_left']} days left</span>
                </div>
                <div class="goal-stats">
                    <span class="goal-progress-text">{progress:.1f}%</span>
                    <div class="progress-bar-custom">
                        <div class="progress-fill {color_class}" style="width: {progress}%;"></div>
                    </div>
                    <div class="goal-amounts">
                        <span>${goal['current']:,.2f}</span>
                        <span class="text-muted">of ${goal['target']:,.2f}</span>
                    </div>
                    <div class="goal-remaining">
                        Remaining: <strong>${remaining:,.2f}</strong>
                    </div>
                </div>
            </div>
            <div class="goal-actions">
                <button class="btn-contribute" data-goal="{goal['name']}" data-remaining="{remaining}">
                    <span class="material-symbols-outlined">add_circle</span>
                    Contribute
                </button>
            </div>
        </div>
        '''
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>FinancePlan - Savings Goals</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20,100,1,200" rel="stylesheet">
        <link rel="stylesheet" href="/static/css/savings.css">
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
                background: linear-gradient(135deg, #1b4332 0%, #2d6a4f 100%);
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
            
            .goals-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
                gap: 24px;
            }}
            
            .goal-card {{
                background: white;
                border-radius: 12px;
                padding: 20px;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                transition: transform 0.2s, box-shadow 0.2s;
            }}
            
            .goal-card:hover {{
                transform: translateY(-4px);
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            }}
            
            .goal-title {{
                font-size: 20px;
                font-weight: 600;
                margin: 0 0 5px 0;
                color: #1b263b;
            }}
            
            .goal-days {{
                font-size: 12px;
                color: #6c757d;
            }}
            
            .goal-stats {{
                margin: 15px 0;
            }}
            
            .goal-progress-text {{
                font-size: 14px;
                font-weight: 500;
                margin-bottom: 5px;
                display: inline-block;
            }}
            
            .progress-bar-custom {{
                background-color: #e9ecef;
                border-radius: 10px;
                overflow: hidden;
                height: 10px;
                margin: 8px 0;
            }}
            
            .progress-fill {{
                height: 100%;
                border-radius: 10px;
                transition: width 0.5s ease;
            }}
            
            .goal-amounts {{
                display: flex;
                justify-content: space-between;
                font-size: 14px;
                margin-top: 8px;
            }}
            
            .goal-remaining {{
                font-size: 13px;
                color: #6c757d;
                margin-top: 8px;
                padding-top: 8px;
                border-top: 1px solid #e9ecef;
            }}
            
            .goal-actions {{
                margin-top: 15px;
                text-align: right;
            }}
            
            .btn-contribute {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border: none;
                padding: 8px 20px;
                border-radius: 8px;
                color: white;
                cursor: pointer;
                display: inline-flex;
                align-items: center;
                gap: 8px;
                transition: all 0.2s;
            }}
            
            .btn-contribute:hover {{
                transform: translateY(-2px);
                box-shadow: 0 2px 8px rgba(102, 126, 234, 0.4);
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
                
                .goals-grid {{
                    grid-template-columns: 1fr;
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
            
            .goal-card {{
                animation: fadeIn 0.3s ease-out;
            }}
        </style>
    </head>
    <body>
        <div id="wrapper">
            <nav id="sidebar" class="p-3 d-flex flex-column vh-100">
                <h4 class="text-white mb-4 text-center py-4">FinancePlan</h4>
                <ul class="nav nav-pills flex-column gap-2 flex-grow-1">
                    <li class="nav-item"><a class="nav-link d-flex align-items-center" href="/finance/dashboard"><span class="material-symbols-outlined me-2">dashboard</span>Dashboard</a></li>
                    <li class="nav-item"><a class="nav-link d-flex align-items-center" href="/budget/"><span class="material-symbols-outlined me-2">account_balance</span>Budget</a></li>
                    <li class="nav-item"><a class="nav-link d-flex align-items-center" href="/expenses/"><span class="material-symbols-outlined me-2">receipt</span>Expenses</a></li>
                    <li class="nav-item"><a class="nav-link d-flex align-items-center" href="/subscriptions/"><span class="material-symbols-outlined me-2">subscriptions</span>Subscriptions</a></li>
                    <li class="nav-item"><a class="nav-link d-flex align-items-center" href="/reports/"><span class="material-symbols-outlined me-2">bar_chart</span>Reports</a></li>
                    <li class="nav-item"><a class="nav-link d-flex align-items-center active" href="/savings/"><span class="material-symbols-outlined me-2">savings</span>Savings</a></li>
                    <li class="nav-item"><a class="nav-link d-flex align-items-center" href="/calendar/"><span class="material-symbols-outlined me-2">calendar_month</span>Calendar</a></li>
                    <li class="nav-item"><a class="nav-link d-flex align-items-center" href="/ai-assistant/"><span class="material-symbols-outlined me-2">smart_toy</span>AI Assistant</a></li>
                    <li class="nav-item"><a class="nav-link d-flex align-items-center" href="/app"><span class="material-symbols-outlined me-2">people</span>Users</a></li>
                    <li class="nav-item mt-auto"><a class="nav-link d-flex align-items-center text-danger" href="/logout"><span class="material-symbols-outlined me-2">logout</span>Logout</a></li>
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
                    <div class="d-flex justify-content-between align-items-center mb-4 flex-wrap gap-3">
                        <div>
                            <h1>Savings Goals</h1>
                            <p class="text-muted">Track progress towards your financial goals</p>
                        </div>
                        <div class="d-flex gap-3">
                            <div class="total-card">
                                <small>Total Saved</small>
                                <h3>${total_saved:,.2f}</h3>
                            </div>
                            <div class="total-card">
                                <small>Total Target</small>
                                <h3>${total_target:,.2f}</h3>
                            </div>
                            <div class="total-card">
                                <small>Overall Progress</small>
                                <h3>{overall_progress:.1f}%</h3>
                            </div>
                        </div>
                    </div>
                    
                    <div class="mb-4">
                        <button class="btn-primary" id="addGoalBtn">
                            <span class="material-symbols-outlined">add</span>
                            New Savings Goal
                        </button>
                    </div>
                    
                    <div class="goals-grid" id="goalsGrid">
                        {goals_html}
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Contribute Modal -->
        <div class="modal fade" id="contributeModal" tabindex="-1">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Contribute to Savings Goal</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <form id="contributeForm">
                            <div class="mb-3">
                                <label class="form-label">Goal</label>
                                <input type="text" class="form-control" id="contributeGoalName" readonly>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Amount to Contribute ($)</label>
                                <input type="number" step="0.01" class="form-control" id="contributeAmount" required>
                                <small class="text-muted" id="remainingHint"></small>
                            </div>
                        </form>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                        <button type="button" class="btn btn-primary" id="confirmContributeBtn">Contribute</button>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Add Goal Modal -->
        <div class="modal fade" id="addGoalModal" tabindex="-1">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Add New Savings Goal</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <form id="addGoalForm">
                            <div class="mb-3">
                                <label class="form-label">Goal Name</label>
                                <input type="text" class="form-control" id="goalName" required>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Target Amount ($)</label>
                                <input type="number" step="0.01" class="form-control" id="goalTarget" required>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Current Savings ($)</label>
                                <input type="number" step="0.01" class="form-control" id="goalCurrent" value="0">
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Target Date</label>
                                <input type="date" class="form-control" id="goalTargetDate" required>
                            </div>
                        </form>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                        <button type="button" class="btn btn-primary" id="confirmAddGoalBtn">Create Goal</button>
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
        <script src="/static/js/savings.js"></script>
        <script>
            document.getElementById('menu-toggle')?.addEventListener('click', () => {{
                document.getElementById('sidebar').classList.toggle('collapsed');
            }});
            
            function showToast(message, type) {{
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
            
            let currentGoal = null;
            let currentRemaining = 0;
            let contributeModal = null;
            
            document.querySelectorAll('.btn-contribute').forEach(btn => {{
                btn.addEventListener('click', () => {{
                    currentGoal = btn.getAttribute('data-goal');
                    currentRemaining = parseFloat(btn.getAttribute('data-remaining'));
                    document.getElementById('contributeGoalName').value = currentGoal;
                    document.getElementById('remainingHint').textContent = 'Remaining to reach goal: $' + currentRemaining.toFixed(2);
                    document.getElementById('contributeAmount').value = '';
                    contributeModal = new bootstrap.Modal(document.getElementById('contributeModal'));
                    contributeModal.show();
                }});
            }});
            
            document.getElementById('confirmContributeBtn')?.addEventListener('click', async () => {{
                const amount = parseFloat(document.getElementById('contributeAmount').value);
                
                if (isNaN(amount) || amount <= 0) {{
                    showToast('Please enter a valid amount', 'error');
                    return;
                }}
                
                if (amount > currentRemaining) {{
                    showToast('Amount exceeds remaining goal ($' + currentRemaining.toFixed(2) + ')', 'error');
                    return;
                }}
                
                const response = await fetch('/savings/api/contribute', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ goal_name: currentGoal, amount: amount }})
                }});
                
                if (response.ok) {{
                    showToast('Successfully contributed $' + amount.toFixed(2) + ' to ' + currentGoal + '!', 'success');
                    if (contributeModal) contributeModal.hide();
                    setTimeout(() => window.location.reload(), 1000);
                }} else {{
                    showToast('Failed to contribute', 'error');
                }}
            }});
            
            let addGoalModal = null;
            document.getElementById('addGoalBtn')?.addEventListener('click', () => {{
                document.getElementById('addGoalForm').reset();
                document.getElementById('goalTargetDate').value = new Date().toISOString().split('T')[0];
                addGoalModal = new bootstrap.Modal(document.getElementById('addGoalModal'));
                addGoalModal.show();
            }});
            
            document.getElementById('confirmAddGoalBtn')?.addEventListener('click', async () => {{
                const name = document.getElementById('goalName').value.trim();
                const target = parseFloat(document.getElementById('goalTarget').value);
                const current = parseFloat(document.getElementById('goalCurrent').value);
                const target_date = document.getElementById('goalTargetDate').value;
                
                if (!name) {{
                    showToast('Please enter a goal name', 'error');
                    return;
                }}
                
                if (isNaN(target) || target <= 0) {{
                    showToast('Please enter a valid target amount', 'error');
                    return;
                }}
                
                if (isNaN(current) || current < 0) {{
                    showToast('Please enter a valid current amount', 'error');
                    return;
                }}
                
                if (current > target) {{
                    showToast('Current savings cannot exceed target', 'error');
                    return;
                }}
                
                const response = await fetch('/savings/api/add-goal', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ name, target, current, target_date }})
                }});
                
                if (response.ok) {{
                    showToast('Savings goal created successfully!', 'success');
                    if (addGoalModal) addGoalModal.hide();
                    setTimeout(() => window.location.reload(), 1000);
                }} else {{
                    showToast('Failed to create goal', 'error');
                }}
            }});
        </script>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content)

# API Routes

@router.get("/api/goals")
async def get_goals():
    return {"goals": savings_service.get_all_goals()}

@router.get("/api/summary")
async def get_summary():
    return {
        "total_saved": savings_service.get_total_saved(),
        "total_target": savings_service.get_total_target(),
        "overall_progress": savings_service.get_overall_progress()
    }

@router.post("/api/contribute")
async def contribute(contribution: SavingsContribution):
    try:
        result = savings_service.contribute_to_goal(contribution.goal_name, contribution.amount)
        if result["success"]:
            return result
        raise HTTPException(status_code=404, detail="Goal not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/add-goal")
async def add_goal(goal: SavingsGoalCreate):
    try:
        result = savings_service.add_goal(goal)
        return {"success": True, "goal": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))