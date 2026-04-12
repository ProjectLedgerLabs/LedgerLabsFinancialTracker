from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse
from typing import Dict, List
from pydantic import BaseModel
from datetime import datetime
from app.routers import templates
from app.dependencies.auth import AuthDep
from app.utilities.flash import get_flashed_messages

router = APIRouter(prefix="/savings", tags=["savings"])

class SavingsGoalCreate(BaseModel):
    name: str
    target: float
    current: float
    target_date: str

class SavingsContribution(BaseModel):
    goal_name: str
    amount: float

class SavingsService:
    def __init__(self):
        self.savings_goals = [
            {"name": "Emergency Fund", "current": 6500.00, "target": 10000.00, "target_date": "2026-12-31"},
            {"name": "Vacation", "current": 1200.00, "target": 3000.00, "target_date": "2026-08-15"},
            {"name": "New Laptop", "current": 1850.00, "target": 2500.00, "target_date": "2026-06-30"}
        ]
    
    def get_all_goals(self) -> List[Dict]:
        today = datetime.now().date()
        for goal in self.savings_goals:
            target_date = datetime.strptime(goal["target_date"], "%Y-%m-%d").date()
            goal["days_left"] = max(0, (target_date - today).days)
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