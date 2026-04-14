from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.routers import templates
from app.dependencies.auth import AuthDep
from app.dependencies.session import SessionDep
from app.utilities.flash import get_flashed_messages
from app.repositories.entry import EntryRepository
from app.repositories.category import CategoryRepository
from app.models.user import EntryType

router = APIRouter(prefix="/expenses", tags=["expenses"])


class ExpenseCreate(BaseModel):
    name: str
    category: str
    amount: float
    date: str


# ------------------------------------------------------------------ #
#  Shared helper                                                        #
# ------------------------------------------------------------------ #

def _group_by_category(items: list) -> dict:
    """Group expense/subscription rows by category for template rendering."""
    categories: dict = {}
    for item in items:
        cat = item["category"]
        if cat not in categories:
            categories[cat] = {"entries": [], "total": 0.0, "count": 0}
        categories[cat]["entries"].append(item)
        categories[cat]["total"] = round(categories[cat]["total"] + item["amount"], 2)
        categories[cat]["count"] += 1
    return categories


# ------------------------------------------------------------------ #
#  Page route                                                          #
# ------------------------------------------------------------------ #

@router.get("/", response_class=HTMLResponse)
async def expenses_page(request: Request, user: AuthDep, db: SessionDep):
    repo = EntryRepository(db)
    # get_all_spending returns both Entry expenses and active subscriptions
    all_spending = repo.get_all_spending(user.user_id)
    total_expenses = repo.get_total_expenses(user.user_id)
    categories = _group_by_category(all_spending)

    return templates.TemplateResponse(
        request=request, name="expenses.html",
        context={
            "flash_messages": get_flashed_messages(request),
            "user": user, "active_page": "expenses",
            "categories": categories,
            "total_expenses": total_expenses,
        },
    )


# ------------------------------------------------------------------ #
#  API routes                                                          #
# ------------------------------------------------------------------ #

@router.get("/api/expenses")
async def get_expenses(user: AuthDep, db: SessionDep):
    """Returns all spending: manual expenses + active subscriptions."""
    return {"expenses": EntryRepository(db).get_all_spending(user.user_id)}


@router.get("/api/expenses/raw")
async def get_raw_expenses(user: AuthDep, db: SessionDep):
    """Returns only manually logged Entry expenses (no subscriptions)."""
    return {"expenses": EntryRepository(db).get_expenses(user.user_id)}


@router.get("/api/expenses/categories")
async def get_expenses_by_category(user: AuthDep, db: SessionDep):
    all_spending = EntryRepository(db).get_all_spending(user.user_id)
    return _group_by_category(all_spending)


@router.get("/api/expenses/total")
async def get_total_expenditure(user: AuthDep, db: SessionDep):
    return {"total": EntryRepository(db).get_total_expenses(user.user_id)}


@router.post("/api/expenses/add")
async def add_expense(expense: ExpenseCreate, user: AuthDep, db: SessionDep):
    try:
        cat_repo = CategoryRepository(db)
        category = cat_repo.get_or_create(user.user_id, expense.category)
        entry_repo = EntryRepository(db)
        result = entry_repo.create_entry(
            user_id=user.user_id,
            description=expense.name,
            amount=expense.amount,
            entry_type=EntryType.EXPENSE,
            category_id=category.category_id,
            date=datetime.strptime(expense.date, "%Y-%m-%d"),
        )
        return {"success": True, "expense": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/api/expenses/{entry_id}")
async def delete_expense(entry_id: int, user: AuthDep, db: SessionDep):
    deleted = EntryRepository(db).delete_entry(entry_id, user.user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Expense not found")
    return {"success": True}
