from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse
from typing import Dict, List
from pydantic import BaseModel
from datetime import datetime
from app.routers import templates
from app.dependencies.auth import AuthDep
from app.utilities.flash import get_flashed_messages

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
            {"id": 1, "name": "Gym Membership", "amount": 49.99, "category": "Health", 
             "billing_cycle": "monthly", "next_billing": "2026-05-10", "active": True},
            {"id": 2, "name": "Software Subscription", "amount": 20.00, "category": "Software", 
             "billing_cycle": "monthly", "next_billing": "2026-05-12", "active": True},
            {"id": 3, "name": "Streaming Service A", "amount": 15.99, "category": "Entertainment", 
             "billing_cycle": "monthly", "next_billing": "2026-05-15", "active": True},
            {"id": 4, "name": "Music Streaming", "amount": 9.99, "category": "Entertainment", 
             "billing_cycle": "monthly", "next_billing": "2026-05-20", "active": True},
            {"id": 5, "name": "Cloud Storage", "amount": 5.00, "category": "Software", 
             "billing_cycle": "monthly", "next_billing": "2026-05-01", "active": True}
        ]
        self.next_id = 6
    
    def get_active_subscriptions(self) -> List[Dict]:
        return [sub for sub in self.subscriptions if sub["active"]]
    
    def get_monthly_cost(self) -> float:
        return sum(sub["amount"] for sub in self.subscriptions if sub["active"])
    
    def get_yearly_projection(self) -> float:
        return self.get_monthly_cost() * 12
    
    def get_upcoming_billing(self, days: int = 30) -> List[Dict]:
        today = datetime.now().date()
        upcoming = []
        for sub in self.subscriptions:
            if sub["active"]:
                next_date = datetime.strptime(sub["next_billing"], "%Y-%m-%d").date()
                days_until = (next_date - today).days
                if 0 <= days_until <= days:
                    upcoming.append({**sub, "days_until": days_until})
        return sorted(upcoming, key=lambda x: x["days_until"])
    
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
    
    def delete_subscription(self, sub_id: int) -> Dict:
        for i, sub in enumerate(self.subscriptions):
            if sub["id"] == sub_id:
                return self.subscriptions.pop(i)
        raise HTTPException(status_code=404, detail="Subscription not found")

subscriptions_service = SubscriptionsService()

# Page Route
@router.get("/", response_class=HTMLResponse)
async def subscriptions_page(request: Request, user: AuthDep):
    active_subs = subscriptions_service.get_active_subscriptions()
    monthly_cost = subscriptions_service.get_monthly_cost()
    yearly_projection = subscriptions_service.get_yearly_projection()
    upcoming = subscriptions_service.get_upcoming_billing(30)
    
    return templates.TemplateResponse(
        request=request,
        name="subscriptions.html",
        context={
            "flash_messages": get_flashed_messages(request),
            "user": user,
            "active_page": "subscriptions",
            "active_subscriptions": active_subs,
            "subscription_summary": {
                "monthly_cost": monthly_cost,
                "yearly_projection": yearly_projection,
                "active_services": len(active_subs)
            },
            "upcoming": upcoming,
        }
    )

# API Routes
@router.get("/api/subscriptions/active")
async def get_active_subscriptions():
    return {"subscriptions": subscriptions_service.get_active_subscriptions()}

@router.get("/api/subscriptions/stats")
async def get_subscription_stats():
    return {
        "monthly_cost": subscriptions_service.get_monthly_cost(),
        "yearly_projection": subscriptions_service.get_yearly_projection(),
        "active_count": len(subscriptions_service.get_active_subscriptions()),
        "upcoming": subscriptions_service.get_upcoming_billing(30)
    }

@router.post("/api/subscriptions/add")
async def add_subscription(subscription: SubscriptionCreate):
    try:
        result = subscriptions_service.add_subscription(subscription)
        return {"success": True, "subscription": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/api/subscriptions/{sub_id}")
async def update_subscription(sub_id: int, updates: SubscriptionUpdate):
    try:
        result = subscriptions_service.update_subscription(sub_id, updates)
        return {"success": True, "subscription": result}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/api/subscriptions/{sub_id}")
async def delete_subscription(sub_id: int):
    try:
        result = subscriptions_service.delete_subscription(sub_id)
        return {"success": True, "subscription": result}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))