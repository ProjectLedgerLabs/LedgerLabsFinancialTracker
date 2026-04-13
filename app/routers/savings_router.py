from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse
from typing import Dict, List
from pydantic import BaseModel
from datetime import datetime
from app.models.user import SavingsContribution, SavingsService
from app.routers import templates
from app.dependencies.auth import AuthDep
from app.utilities.flash import get_flashed_messages

router = APIRouter(prefix="/savings", tags=["savings"])

savings_service = SavingsService()

# Page Route
@router.get("/", response_class=HTMLResponse)
async def savings_page(request: Request, user: AuthDep):
    goals = savings_service.get_all_goals()
    total_saved = savings_service.get_total_saved()
    total_target = savings_service.get_total_target()
    overall_progress = savings_service.get_overall_progress()
    
    return templates.TemplateResponse(
        request=request,
        name="savings.html",
        context={
            "flash_messages": get_flashed_messages(request),
            "user": user,
            "active_page": "savings",
            "goals": goals,
            "total_saved": total_saved,
            "total_target": total_target,
            "overall_progress": overall_progress,
        }
    )

# API Routes
@router.post("/api/contribute")
async def contribute(contribution: SavingsContribution):
    result = savings_service.contribute_to_goal(contribution.goal_name, contribution.amount)
    if result["success"]:
        return result
    raise HTTPException(status_code=404, detail="Goal not found")