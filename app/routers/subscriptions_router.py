from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.routers import templates
from app.dependencies.auth import AuthDep
from app.dependencies.session import SessionDep
from app.utilities.flash import get_flashed_messages
from app.repositories.subscription import SubscriptionRepository
from app.repositories.category import CategoryRepository
from app.models.user import BillingCycle, Status

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])


class SubscriptionCreate(BaseModel):
    name: str
    amount: float
    category: str
    billing_cycle: str
    next_billing: str
    description: Optional[str] = None


class SubscriptionUpdate(BaseModel):
    name: Optional[str] = None
    amount: Optional[float] = None
    category: Optional[str] = None
    billing_cycle: Optional[str] = None
    next_billing: Optional[str] = None
    description: Optional[str] = None


# ------------------------------------------------------------------ #
#  Page route                                                          #
# ------------------------------------------------------------------ #

@router.get("/", response_class=HTMLResponse)
async def subscriptions_page(request: Request, user: AuthDep, db: SessionDep):
    repo = SubscriptionRepository(db)
    active_subs = repo.get_active(user.user_id)
    monthly_cost = repo.get_monthly_cost(user.user_id)
    upcoming = repo.get_upcoming_billing(user.user_id, days=30)

    return templates.TemplateResponse(
        request=request, name="subscriptions.html",
        context={
            "flash_messages": get_flashed_messages(request),
            "user": user, "active_page": "subscriptions",
            "active_subscriptions": active_subs,
            "subscription_summary": {
                "monthly_cost": monthly_cost,
                "yearly_projection": round(monthly_cost * 12, 2),
                "active_services": len(active_subs),
            },
            "upcoming": upcoming,
        },
    )


# ------------------------------------------------------------------ #
#  API routes                                                          #
# ------------------------------------------------------------------ #

@router.get("/api/subscriptions/active")
async def get_active_subscriptions(user: AuthDep, db: SessionDep):
    return {"subscriptions": SubscriptionRepository(db).get_active(user.user_id)}


@router.get("/api/subscriptions/stats")
async def get_subscription_stats(user: AuthDep, db: SessionDep):
    repo = SubscriptionRepository(db)
    active = repo.get_active(user.user_id)
    monthly_cost = repo.get_monthly_cost(user.user_id)
    return {
        "monthly_cost": monthly_cost,
        "yearly_projection": round(monthly_cost * 12, 2),
        "active_count": len(active),
        "upcoming": repo.get_upcoming_billing(user.user_id, days=30),
    }


@router.post("/api/subscriptions/add")
async def add_subscription(subscription: SubscriptionCreate, user: AuthDep, db: SessionDep):
    try:
        cat_repo = CategoryRepository(db)
        category = cat_repo.get_or_create(user.user_id, subscription.category)
        repo = SubscriptionRepository(db)
        result = repo.create(
            user_id=user.user_id,
            name=subscription.name,
            amount=subscription.amount,
            billing_cycle=BillingCycle(subscription.billing_cycle),
            next_billing_date=datetime.strptime(subscription.next_billing, "%Y-%m-%d"),
            category_id=category.category_id,
            description=subscription.description,
        )
        return {"success": True, "subscription": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/api/subscriptions/{sub_id}")
async def update_subscription(sub_id: int, updates: SubscriptionUpdate, user: AuthDep, db: SessionDep):
    repo = SubscriptionRepository(db)
    update_dict = updates.dict(exclude_unset=True)

    # Resolve category name -> id if provided
    if "category" in update_dict:
        cat_repo = CategoryRepository(db)
        category = cat_repo.get_or_create(user.user_id, update_dict.pop("category"))
        update_dict["category_id"] = category.category_id

    if "next_billing" in update_dict:
        update_dict["next_billing_date"] = datetime.strptime(update_dict.pop("next_billing"), "%Y-%m-%d")

    if "billing_cycle" in update_dict:
        update_dict["billing_cycle"] = BillingCycle(update_dict["billing_cycle"])

    result = repo.update(sub_id, user.user_id, update_dict)
    if result is None:
        raise HTTPException(status_code=404, detail="Subscription not found")
    return {"success": True, "subscription": result}


@router.delete("/api/subscriptions/{sub_id}")
async def delete_subscription(sub_id: int, user: AuthDep, db: SessionDep):
    deleted = SubscriptionRepository(db).delete(sub_id, user.user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Subscription not found")
    return {"success": True}
