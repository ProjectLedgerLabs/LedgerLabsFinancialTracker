from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from app.routers import templates
from app.dependencies.auth import AuthDep
from app.dependencies.session import SessionDep
from app.utilities.flash import get_flashed_messages
from app.repositories.entry import EntryRepository
from app.repositories.budget import BudgetRepository

router = APIRouter(prefix="/budget", tags=["budget"])


class BudgetSet(BaseModel):
    category: str
    limit: float


class BudgetDelete(BaseModel):
    budget_id: int


# ------------------------------------------------------------------ #
#  Shared helper                                                        #
# ------------------------------------------------------------------ #

def _build_budget_data(user_id: int, db) -> dict:
    spending = EntryRepository(db).get_category_spending(user_id)
    budgets = BudgetRepository(db).get_all(user_id, spending)

    total_allocated = round(sum(b["limit"] for b in budgets), 2)
    total_spent = round(sum(b["spent"] for b in budgets), 2)
    total_remaining = round(total_allocated - total_spent, 2)
    overall_progress = round((total_spent / total_allocated) * 100, 1) if total_allocated else 0.0

    return {
        "budgets": budgets,
        "total_allocated": f"{total_allocated:.2f}",
        "total_spent": f"{total_spent:.2f}",
        "total_remaining": f"{total_remaining:.2f}",
        "overall_progress": overall_progress,
    }


# ------------------------------------------------------------------ #
#  Page route                                                          #
# ------------------------------------------------------------------ #

@router.get("/", response_class=HTMLResponse)
async def budget_page(request: Request, user: AuthDep, db: SessionDep):
    data = _build_budget_data(user.user_id, db)
    return templates.TemplateResponse(
        request=request, name="budget.html",
        context={
            "flash_messages": get_flashed_messages(request),
            "user": user,
            "active_page": "budget",
            **data,
        },
    )


# ------------------------------------------------------------------ #
#  API routes                                                          #
# ------------------------------------------------------------------ #

@router.get("/api/budgets")
async def get_budgets(user: AuthDep, db: SessionDep):
    return _build_budget_data(user.user_id, db)


@router.post("/api/update")
async def update_budget(payload: BudgetSet, user: AuthDep, db: SessionDep):
    """Create or update the budget limit for a category."""
    if payload.limit <= 0:
        raise HTTPException(status_code=400, detail="Limit must be greater than zero")
    try:
        result = BudgetRepository(db).set_limit(user.user_id, payload.category, payload.limit)
        return {"success": True, "budget": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/add")
async def add_budget(payload: BudgetSet, user: AuthDep, db: SessionDep):
    """Alias for update — creates a new limit or overwrites an existing one."""
    if payload.limit <= 0:
        raise HTTPException(status_code=400, detail="Limit must be greater than zero")
    try:
        result = BudgetRepository(db).set_limit(user.user_id, payload.category, payload.limit)
        return {"success": True, "budget": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/api/budgets/{budget_id}")
async def delete_budget(budget_id: int, user: AuthDep, db: SessionDep):
    deleted = BudgetRepository(db).delete(budget_id, user.user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Budget not found")
    return {"success": True}
