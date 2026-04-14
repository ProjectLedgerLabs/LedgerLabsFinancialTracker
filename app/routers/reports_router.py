from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from app.routers import templates
from app.dependencies.auth import AuthDep
from app.dependencies.session import SessionDep
from app.utilities.flash import get_flashed_messages
from app.repositories.entry import EntryRepository
from app.repositories.subscription import SubscriptionRepository
from app.repositories.savings import SavingsRepository

router = APIRouter(prefix="/reports", tags=["reports"])

CATEGORY_COLORS = [
    "#35898b", "#4da0a8", "#e8a87c", "#e57373", "#388026", "#f1b74b",
]


def _build_report_data(user_id: int, db) -> dict:
    entry_repo = EntryRepository(db)
    sub_repo = SubscriptionRepository(db)
    savings_repo = SavingsRepository(db)

    # ── 6-month history ──────────────────────────────────────────────
    expense_history = entry_repo.get_monthly_expense_totals(user_id, num_months=6)
    income_history = entry_repo.get_monthly_income_totals(user_id, num_months=6)
    monthly_labels = expense_history["labels"]
    monthly_spending = expense_history["totals"]
    monthly_income_data = income_history["totals"]

    # ── Spending insights ────────────────────────────────────────────
    current_month = monthly_spending[-1] if monthly_spending else 0.0
    previous_month = monthly_spending[-2] if len(monthly_spending) >= 2 else 0.0
    non_zero = [m for m in monthly_spending if m > 0]
    average_monthly = round(sum(non_zero) / len(non_zero), 2) if non_zero else 0.0
    mom_change = (
        round(((current_month - previous_month) / previous_month) * 100, 1)
        if previous_month > 0 else 0.0
    )
    spending_insights = {
        "current_month": current_month,
        "previous_month": previous_month,
        "average_monthly": average_monthly,
        "month_over_month": mom_change,
        "is_decreasing": mom_change < 0,
    }

    # ── Category breakdown (current month only) ──────────────────────
    category_data = entry_repo.get_category_spending(user_id)

    # ── Top expense categories ───────────────────────────────────────
    sorted_cats = sorted(category_data.items(), key=lambda x: x[1], reverse=True)
    top_categories = [{"name": cat, "amount": amt} for cat, amt in sorted_cats[:3]]

    # ── Subscription summary ─────────────────────────────────────────
    active_subs = sub_repo.get_active(user_id)
    monthly_sub_cost = sub_repo.get_monthly_cost(user_id)
    subscription_summary = {
        "monthly_cost": monthly_sub_cost,
        "yearly_projection": round(monthly_sub_cost * 12, 2),
        "active_services": len(active_subs),
        "subscriptions": [
            {
                "name": s["name"],
                "amount": s["amount"],
                "nextBilling": s["next_billing"],
            }
            for s in active_subs
        ],
    }

    # ── Savings summary ──────────────────────────────────────────────
    savings_summary = {
        "total_saved": savings_repo.get_total_saved(user_id),
        "total_target": savings_repo.get_total_target(user_id),
        "progress": savings_repo.get_overall_progress(user_id),
    }

    return {
        "monthly_labels": monthly_labels,
        "monthly_spending": monthly_spending,
        "monthly_income": monthly_income_data,
        "category_labels": list(category_data.keys()),
        "category_values": list(category_data.values()),
        "category_colors": CATEGORY_COLORS,
        "spending_insights": spending_insights,
        "subscription_summary": subscription_summary,
        "savings_summary": savings_summary,
        "top_categories": top_categories,
    }


# ------------------------------------------------------------------ #
#  Page route                                                          #
# ------------------------------------------------------------------ #

@router.get("/", response_class=HTMLResponse)
async def reports_page(request: Request, user: AuthDep, db: SessionDep):
    data = _build_report_data(user.user_id, db)
    return templates.TemplateResponse(
        request=request,
        name="reports.html",
        context={
            "flash_messages": get_flashed_messages(request),
            "user": user,
            "active_page": "reports",
            **data,
        },
    )


# ------------------------------------------------------------------ #
#  API routes                                                          #
# ------------------------------------------------------------------ #

@router.get("/api/reports/summary")
async def get_reports_summary(user: AuthDep, db: SessionDep):
    return _build_report_data(user.user_id, db)


@router.get("/api/reports/spending-insights")
async def get_spending_insights(user: AuthDep, db: SessionDep):
    data = _build_report_data(user.user_id, db)
    return data["spending_insights"]


@router.get("/api/reports/category-breakdown")
async def get_category_breakdown(user: AuthDep, db: SessionDep):
    category_data = EntryRepository(db).get_category_spending(user.user_id)
    sorted_cats = sorted(category_data.items(), key=lambda x: x[1], reverse=True)
    return {
        "labels": [c[0] for c in sorted_cats],
        "values": [c[1] for c in sorted_cats],
        "colors": CATEGORY_COLORS[: len(sorted_cats)],
    }


@router.get("/api/reports/monthly-trend")
async def get_monthly_trend(user: AuthDep, db: SessionDep, months: int = 6):
    entry_repo = EntryRepository(db)
    expense_history = entry_repo.get_monthly_expense_totals(user.user_id, num_months=months)
    income_history = entry_repo.get_monthly_income_totals(user.user_id, num_months=months)
    return {
        "labels": expense_history["labels"],
        "spending": expense_history["totals"],
        "income": income_history["totals"],
    }
