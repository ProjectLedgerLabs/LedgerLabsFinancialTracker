from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse
from typing import Dict, List
from pydantic import BaseModel
from datetime import datetime
from app.models.user import SubscriptionsService
from app.routers import templates
from app.dependencies.auth import AuthDep
from app.utilities.flash import get_flashed_messages

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])

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
    })