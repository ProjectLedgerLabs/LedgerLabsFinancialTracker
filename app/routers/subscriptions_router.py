from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse
from typing import Dict, List
from pydantic import BaseModel
from datetime import datetime, timedelta
from app.routers.sidebar import get_sidebar_html

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])
class SubscriptionCreate(BaseModel):
    name: str
    amount: float
    category: str
    billing_cycle: str
    next_billing: str

class SubscriptionUpdate(BaseModel):
    name: str = None
    amount: float = None
    category: str = None
    billing_cycle: str = None
    next_billing: str = None

class SubscriptionsService:
    def __init__(self):
        self.subscriptions = [
            {
                "id": 1,
                "name": "Gym Membership",
                "amount": 49.99,
                "category": "Health",
                "billing_cycle": "monthly",
                "next_billing": "2026-05-10",
                "active": True
            },
            {
                "id": 2,
                "name": "Software Subscription",
                "amount": 20.00,
                "category": "Software",
                "billing_cycle": "monthly",
                "next_billing": "2026-05-12",
                "active": True
            },
            {
                "id": 3,
                "name": "Streaming Service A",
                "amount": 15.99,
                "category": "Entertainment",
                "billing_cycle": "monthly",
                "next_billing": "2026-05-15",
                "active": True
            },
            {
                "id": 4,
                "name": "Music Streaming",
                "amount": 9.99,
                "category": "Entertainment",
                "billing_cycle": "monthly",
                "next_billing": "2026-05-20",
                "active": True
            },
            {
                "id": 5,
                "name": "Cloud Storage",
                "amount": 5.00,
                "category": "Software",
                "billing_cycle": "monthly",
                "next_billing": "2026-05-01",
                "active": True
            }
        ]
        self.next_id = 6
    
    def get_all_subscriptions(self) -> List[Dict]:
        return self.subscriptions
    
    def get_active_subscriptions(self) -> List[Dict]:
        return [sub for sub in self.subscriptions if sub["active"]]
    
    def get_inactive_subscriptions(self) -> List[Dict]:
        return [sub for sub in self.subscriptions if not sub["active"]]
    
    def get_monthly_cost(self) -> float:
        return sum(sub["amount"] for sub in self.subscriptions if sub["active"])
    
    def get_yearly_projection(self) -> float:
        monthly = self.get_monthly_cost()
        yearly = monthly * 12
       
        for sub in self.subscriptions:
            if sub["active"] and sub["billing_cycle"] == "yearly":
                yearly += sub["amount"] - (sub["amount"] / 12)
        return yearly
    
    def get_active_count(self) -> int:
        return len(self.get_active_subscriptions())
    
    def get_inactive_count(self) -> int:
        return len(self.get_inactive_subscriptions())
    
    def add_subscription(self, subscription: SubscriptionCreate) -> Dict:
        new_sub = subscription.dict()
        new_sub["id"] = self.next_id
        new_sub["active"] = True
        self.next_id += 1
        self.subscriptions.append(new_sub)
        return new_sub
    
    def update_subscription(self, sub_id: int, updates: SubscriptionUpdate) -> Dict:
        for sub in self.subscriptions:
            if sub["id"] == sub_id:
                update_data = updates.dict(exclude_unset=True)
                sub.update(update_data)
                return sub
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    def toggle_subscription(self, sub_id: int) -> Dict:
        for sub in self.subscriptions:
            if sub["id"] == sub_id:
                sub["active"] = not sub["active"]
                return sub
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    def delete_subscription(self, sub_id: int) -> Dict:
        for i, sub in enumerate(self.subscriptions):
            if sub["id"] == sub_id:
                return self.subscriptions.pop(i)
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    def get_upcoming_billing(self, days: int = 30) -> List[Dict]:
        today = datetime.now().date()
        upcoming = []
        for sub in self.subscriptions:
            if sub["active"]:
                next_date = datetime.strptime(sub["next_billing"], "%Y-%m-%d").date()
                days_until = (next_date - today).days
                if 0 <= days_until <= days:
                    upcoming.append({
                        **sub,
                        "days_until": days_until
                    })
        return sorted(upcoming, key=lambda x: x["days_until"])

subscriptions_service = SubscriptionsService()

# Page Route

@router.get("/", response_class=HTMLResponse)
async def subscriptions_page(request: Request):
    """Render the subscriptions page with inline HTML"""
   
    username = "User"
    if hasattr(request, "session") and request.session:
        username = request.session.get("username", "User")
    
  
    active_subs = subscriptions_service.get_active_subscriptions()
    monthly_cost = subscriptions_service.get_monthly_cost()
    yearly_projection = subscriptions_service.get_yearly_projection()
    active_count = subscriptions_service.get_active_count()
    upcoming = subscriptions_service.get_upcoming_billing(30)
    
   
    active_html = ""
    for sub in active_subs:
        
        category_colors = {
            "Health": "danger",
            "Software": "primary",
            "Entertainment": "success",
            "Food": "warning",
            "Utilities": "info"
        }
        color = category_colors.get(sub["category"], "secondary")
        
        active_html += f'''
        <div class="subscription-card" data-id="{sub['id']}">
            <div class="card-header">
                <div>
                    <h5>{sub["name"]}</h5>
                    <span class="badge bg-{color}">{sub["category"]}</span>
                </div>
                <div class="subscription-actions">
                    <span class="badge bg-secondary">{sub["billing_cycle"]}</span>
                    <button class="btn-icon edit-sub" data-id="{sub['id']}">
                        <span class="material-symbols-outlined">edit</span>
                    </button>
                    <button class="btn-icon delete-sub" data-id="{sub['id']}">
                        <span class="material-symbols-outlined">delete</span>
                    </button>
                </div>
            </div>
            <div class="card-body">
                <div class="amount">${sub["amount"]:.2f}</div>
                <div class="next-billing">
                    <span class="material-symbols-outlined">event</span>
                    Next: {sub["next_billing"]}
                </div>
            </div>
        </div>
        '''
    
   
    upcoming_html = ""
    if upcoming:
        for sub in upcoming:
            upcoming_html += f'''
            <div class="upcoming-item">
                <div>
                    <strong>{sub["name"]}</strong>
                    <div class="text-muted small">{sub["category"]}</div>
                </div>
                <div class="text-end">
                    <div>${sub["amount"]:.2f}</div>
                    <small class="text-muted">{sub["days_until"]} days</small>
                </div>
            </div>
            '''
    else:
        upcoming_html = '<p class="text-muted text-center">No upcoming bills in the next 30 days</p>'
    
    sidebar_html = get_sidebar_html(active_page="subscriptions")

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>FinancePlan - Subscription Manager</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20,100,1,200" rel="stylesheet">
        <link rel="stylesheet" href="/static/css/subscriptions.css">
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
                            <h1>Subscription Manager</h1>
                            <p class="text-muted">Track and manage recurring payments</p>
                        </div>
                        <button class="btn btn-primary" id="addSubBtn">
                            <span class="material-symbols-outlined">add</span>
                            New Subscription
                        </button>
                    </div>
                    
                    <!-- Stats Cards -->
                    <div class="row mb-4">
                        <div class="col-md-3">
                            <div class="stat-card">
                                <div class="stat-icon">💰</div>
                                <div>
                                    <div class="stat-label">Monthly Cost</div>
                                    <div class="stat-value">${monthly_cost:.2f}</div>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="stat-card">
                                <div class="stat-icon">📅</div>
                                <div>
                                    <div class="stat-label">Yearly Projection</div>
                                    <div class="stat-value">${yearly_projection:.2f}</div>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="stat-card">
                                <div class="stat-icon">✅</div>
                                <div>
                                    <div class="stat-label">Active Services</div>
                                    <div class="stat-value">{active_count}</div>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="stat-card">
                                <div class="stat-icon">⏰</div>
                                <div>
                                    <div class="stat-label">Upcoming Bills</div>
                                    <div class="stat-value">{len(upcoming)}</div>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Main Content Row -->
                    <div class="row">
                        <div class="col-lg-8">
                            <div class="card">
                                <div class="card-header bg-white">
                                    <h5 class="mb-0">Active Subscriptions</h5>
                                </div>
                                <div class="card-body subscriptions-grid" id="subscriptionsList">
                                    {active_html}
                                </div>
                            </div>
                        </div>
                        
                        <div class="col-lg-4">
                            <div class="card">
                                <div class="card-header bg-white">
                                    <h5 class="mb-0">Upcoming Billing</h5>
                                </div>
                                <div class="card-body upcoming-list" id="upcomingList">
                                    {upcoming_html}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Add/Edit Subscription Modal -->
        <div class="modal fade" id="subscriptionModal" tabindex="-1">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title" id="modalTitle">Add Subscription</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <form id="subscriptionForm">
                            <input type="hidden" id="subId" value="">
                            <div class="mb-3">
                                <label class="form-label">Service Name</label>
                                <input type="text" class="form-control" id="subName" required>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Amount ($)</label>
                                <input type="number" step="0.01" class="form-control" id="subAmount" required>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Category</label>
                                <select class="form-select" id="subCategory">
                                    <option value="Health">Health</option>
                                    <option value="Software">Software</option>
                                    <option value="Entertainment">Entertainment</option>
                                    <option value="Food">Food</option>
                                    <option value="Utilities">Utilities</option>
                                </select>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Billing Cycle</label>
                                <select class="form-select" id="subBillingCycle">
                                    <option value="monthly">Monthly</option>
                                    <option value="yearly">Yearly</option>
                                </select>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Next Billing Date</label>
                                <input type="date" class="form-control" id="subNextBilling" required>
                            </div>
                        </form>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                        <button type="button" class="btn btn-primary" id="saveSubBtn">Save Subscription</button>
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
        <script src="/static/js/subscriptions.js"></script>
        <script>
            // Pass initial data to JavaScript
            window.subscriptionsData = {{
                subscriptions: {subscriptions_service.get_active_subscriptions()}
            }};
        </script>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content)

# API Routes

@router.get("/api/subscriptions")
async def get_subscriptions():
    """Get all subscriptions"""
    return {"subscriptions": subscriptions_service.get_all_subscriptions()}

@router.get("/api/subscriptions/active")
async def get_active_subscriptions():
    """Get active subscriptions"""
    return {"subscriptions": subscriptions_service.get_active_subscriptions()}

@router.get("/api/subscriptions/stats")
async def get_subscription_stats():
    """Get subscription statistics"""
    return {
        "monthly_cost": subscriptions_service.get_monthly_cost(),
        "yearly_projection": subscriptions_service.get_yearly_projection(),
        "active_count": subscriptions_service.get_active_count(),
        "inactive_count": subscriptions_service.get_inactive_count(),
        "upcoming": subscriptions_service.get_upcoming_billing(30)
    }

@router.post("/api/subscriptions/add")
async def add_subscription(subscription: SubscriptionCreate):
    """Add a new subscription"""
    try:
        result = subscriptions_service.add_subscription(subscription)
        return {"success": True, "subscription": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/api/subscriptions/{sub_id}")
async def update_subscription(sub_id: int, updates: SubscriptionUpdate):
    """Update a subscription"""
    try:
        result = subscriptions_service.update_subscription(sub_id, updates)
        return {"success": True, "subscription": result}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/api/subscriptions/{sub_id}/toggle")
async def toggle_subscription(sub_id: int):
    """Toggle subscription active status"""
    try:
        result = subscriptions_service.toggle_subscription(sub_id)
        return {"success": True, "subscription": result}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/api/subscriptions/{sub_id}")
async def delete_subscription(sub_id: int):
    """Delete a subscription"""
    try:
        result = subscriptions_service.delete_subscription(sub_id)
        return {"success": True, "subscription": result}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/subscriptions/upcoming")
async def get_upcoming_billing(days: int = 30):
    """Get upcoming billing in next X days"""
    return {"upcoming": subscriptions_service.get_upcoming_billing(days)}