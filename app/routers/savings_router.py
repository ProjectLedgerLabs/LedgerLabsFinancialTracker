from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.routers import templates
from app.dependencies.auth import AuthDep
from app.dependencies.session import SessionDep
from app.utilities.flash import get_flashed_messages
from app.repositories.savings import SavingsRepository

router = APIRouter(prefix="/savings", tags=["savings"])


class SavingsGoalCreate(BaseModel):
    name: str
    target_amount: float
    target_date: Optional[str] = None
    description: Optional[str] = None


class SavingsContribution(BaseModel):
    goal_id: int
    amount: float


# ------------------------------------------------------------------ #
#  Page route                                                          #
# ------------------------------------------------------------------ #

@router.get("/", response_class=HTMLResponse)
async def savings_page(request: Request, user: AuthDep, db: SessionDep):
    repo = SavingsRepository(db)
    goals = repo.get_all(user.user_id)
    total_saved = repo.get_total_saved(user.user_id)
    total_target = repo.get_total_target(user.user_id)
    overall_progress = repo.get_overall_progress(user.user_id)

    return templates.TemplateResponse(
        request=request, name="savings.html",
        context={
            "flash_messages": get_flashed_messages(request),
            "user": user, "active_page": "savings",
            "goals": goals, "total_saved": total_saved,
            "total_target": total_target, "overall_progress": overall_progress,
        },
    )


# ------------------------------------------------------------------ #
#  API routes                                                          #
# ------------------------------------------------------------------ #

@router.get("/api/goals")
async def get_goals(user: AuthDep, db: SessionDep):
    return {"goals": SavingsRepository(db).get_all(user.user_id)}


@router.get("/api/summary")
async def get_savings_summary(user: AuthDep, db: SessionDep):
    repo = SavingsRepository(db)
    return {
        "total_saved": repo.get_total_saved(user.user_id),
        "total_target": repo.get_total_target(user.user_id),
        "overall_progress": repo.get_overall_progress(user.user_id),
    }


@router.post("/api/goals/add")
async def add_goal(goal: SavingsGoalCreate, user: AuthDep, db: SessionDep):
    try:
        deadline = datetime.strptime(goal.target_date, "%Y-%m-%d") if goal.target_date else None
        result = SavingsRepository(db).create(
            user_id=user.user_id,
            name=goal.name,
            target_amount=goal.target_amount,
            deadline=deadline,
            description=goal.description,
        )
        return {"success": True, "goal": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/contribute")
async def contribute(contribution: SavingsContribution, user: AuthDep, db: SessionDep):
    result = SavingsRepository(db).contribute(contribution.goal_id, user.user_id, contribution.amount)
    if result is None:
        raise HTTPException(status_code=404, detail="Goal not found")
    return {"success": True, "goal": result}


@router.delete("/api/goals/{goal_id}")
async def delete_goal(goal_id: int, user: AuthDep, db: SessionDep):
    deleted = SavingsRepository(db).delete(goal_id, user.user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Goal not found")
    return {"success": True}
