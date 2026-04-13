from ast import Dict, List
from datetime import datetime, timedelta

from sqlmodel import Field, Relationship, SQLModel
from typing import Optional
from pydantic import BaseModel, EmailStr
from enum import Enum

class EntryType(str, Enum):
    INCOME = "income"
    EXPENSE = "expense"

class CalendarEventType(str, Enum):
    GOAL_DEADLINE = "goal_deadline"
    INCOME = "income"
    EXPENSE = "expense"
    SUBSCRIPTION = "subscription"

class BillingCycle(str, Enum):
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"

class Status(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"

class UserBase(SQLModel,):
    username: str = Field(index=True, unique=True)
    email: EmailStr = Field(index=True, unique=True)
    password: str
    role: str = Field(default="regular_user")

class User(UserBase, table=True):
    user_id: Optional[int] = Field(default=None, primary_key=True)
    entries: list["Entry"] = Relationship(back_populates="user_rel")
    subscriptions: list["Subscription"] = Relationship(back_populates="user_rel")
    categories: list["Category"] = Relationship(back_populates="user_rel")
    calendar_events: list["CalendarEvent"] = Relationship(back_populates="user_rel")
    savings_goals: list["SavingsGoal"] = Relationship(back_populates="user_rel")

class Entry (SQLModel, table=True):
    entry_id: Optional[int] = Field(default=None, primary_key=True)
    amount: float
    description: Optional[str] = None
    date: Optional[datetime] = None
    type: EntryType
    category_id: Optional[int] = Field(default=None, foreign_key="category.category_id")
    user_id: Optional[int] = Field(default=None, foreign_key="user.user_id")

    user_rel: Optional["User"] = Relationship(back_populates="entries")
    category_rel: Optional["Category"] = Relationship(back_populates="entries")

class Subscription (SQLModel, table=True):
    subscription_id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(default=None, foreign_key="user.user_id")
    name: str
    amount: float
    description: Optional[str] = None
    billing_cycle: BillingCycle
    next_billing_date: Optional[datetime] = None
    status: Status = Status.ACTIVE
    category_id: Optional[int] = Field(default=None, foreign_key="category.category_id")

    category_rel: Optional["Category"] = Relationship(back_populates="subscriptions")
    user_rel: Optional["User"] = Relationship(back_populates="subscriptions")

class Category (SQLModel, table=True):
    category_id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    user_id: Optional[int] = Field(default=None, foreign_key="user.user_id")
    
    entries: list["Entry"] = Relationship(back_populates="category_rel")
    subscriptions: list["Subscription"] = Relationship(back_populates="category_rel")
    user_rel: Optional["User"] = Relationship(back_populates="categories")
    

class CalendarEvent (SQLModel, table=True):
    event_id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(default=None, foreign_key="user.user_id")
    type: CalendarEventType
    title: str
    description: Optional[str] = None
    date: Optional[datetime] = None
    user_rel: Optional["User"] = Relationship(back_populates="calendar_events")

class SavingsGoal (SQLModel, table=True):
    goal_id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(default=None, foreign_key="user.user_id")
    name: str
    target_amount: float
    current_amount: float = 0.0
    description: Optional[str] = None
    deadline: Optional[datetime] = None
    user_rel: Optional["User"] = Relationship(back_populates="savings_goals")

class ExpenseCreate(BaseModel):
    name: str
    category: str
    amount: float
    date: str

class ExpensesService:
    def __init__(self):
        self.expenses = [
            {"name": "Grocery shopping", "category": "Food", "amount": 156.32, "date": "2026-04-05"},
            {"name": "Gas station", "category": "Transportation", "amount": 65.00, "date": "2026-04-03"},
            {"name": "Restaurant dinner", "category": "Food", "amount": 89.50, "date": "2026-04-01"},
            {"name": "Coffee shop", "category": "Food", "amount": 12.75, "date": "2026-04-08"},
            {"name": "Movie tickets", "category": "Entertainment", "amount": 34.00, "date": "2026-04-06"},
            {"name": "Gym membership", "category": "Health", "amount": 49.99, "date": "2026-04-01"},
            {"name": "Netflix", "category": "Software", "amount": 15.99, "date": "2026-04-01"},
            {"name": "Spotify", "category": "Software", "amount": 9.99, "date": "2026-04-01"},
            {"name": "Internet bill", "category": "Utilities", "amount": 80.00, "date": "2026-04-01"},
            {"name": "Electric bill", "category": "Utilities", "amount": 100.00, "date": "2026-04-02"},
        ]
    
    def get_all_expenses(self) -> List[Dict]:
        return self.expenses
    
    def get_expenses_by_category(self) -> Dict[str, Dict]:
        categories = {}
        for expense in self.expenses:
            cat = expense["category"]
            if cat not in categories:
                categories[cat] = {
                    "entries": [],
                    "total": 0,
                    "count": 0
                }
            categories[cat]["entries"].append(expense)
            categories[cat]["total"] += expense["amount"]
            categories[cat]["count"] += 1
        return categories
    
    def get_total_expenditure(self) -> float:
        return sum(expense["amount"] for expense in self.expenses)
    
    def add_expense(self, expense: ExpenseCreate) -> Dict:
        new_expense = expense.dict()
        self.expenses.insert(0, new_expense)
        return new_expense
    
    
# finanace dashboard 

class IncomeUpdate(BaseModel):
    income: float

class FinanceService:
    def __init__(self):
        self.monthly_income = 5000.00
        self.expenses = [
            {"name": "Grocery shopping", "category": "Food", "amount": 156.32, "date": datetime(2026, 4, 5)},
            {"name": "Gas station", "category": "Transportation", "amount": 65.00, "date": datetime(2026, 4, 3)},
            {"name": "Restaurant dinner", "category": "Food", "amount": 89.50, "date": datetime(2026, 4, 1)},
            {"name": "Coffee shop", "category": "Food", "amount": 12.75, "date": datetime(2026, 4, 8)},
            {"name": "Movie tickets", "category": "Entertainment", "amount": 34.00, "date": datetime(2026, 4, 6)},
            {"name": "Gym membership", "category": "Health", "amount": 49.99, "date": datetime(2026, 4, 1)},
            {"name": "Netflix", "category": "Software", "amount": 15.99, "date": datetime(2026, 4, 1)},
            {"name": "Spotify", "category": "Software", "amount": 9.99, "date": datetime(2026, 4, 1)},
            {"name": "Internet bill", "category": "Utilities", "amount": 80.00, "date": datetime(2026, 4, 1)},
            {"name": "Electric bill", "category": "Utilities", "amount": 100.00, "date": datetime(2026, 4, 2)},
        ]
        
        self.budget_limits = {
            "Food": 600, "Transportation": 300, "Entertainment": 200,
            "Health": 150, "Software": 100, "Utilities": 200
        }
        
        self.monthly_expenses_history = [450, 520, 380, 465]
        self.monthly_labels = ["Jan", "Feb", "Mar", "Apr"]
    
    def get_total_expenses(self) -> float:
        return sum(expense["amount"] for expense in self.expenses)
    
    def get_category_spending(self) -> Dict[str, float]:
        categories = {}
        for expense in self.expenses:
            cat = expense["category"]
            amount = expense["amount"]
            categories[cat] = categories.get(cat, 0) + amount
        return categories
    
    def get_burn_rate(self) -> float:
        return self.monthly_income - self.get_total_expenses()
    
    def get_savings_rate(self) -> float:
        burn_rate = self.get_burn_rate()
        return round((burn_rate / self.monthly_income) * 100, 1) if self.monthly_income > 0 else 0
    
    def get_budgets(self) -> List[Dict]:
        spending = self.get_category_spending()
        budgets = []
        color_map = {
            "Food": "#006699", "Transportation": "#669900", "Entertainment": "#ff6600",
            "Health": "#cc3399", "Software": "#99cc33", "Utilities": "#ffcc00"
        }
        
        for category, limit in self.budget_limits.items():
            spent = spending.get(category, 0)
            percentage = round((spent / limit) * 100, 1)
            budgets.append({
                "category": category,
                "limit": limit,
                "spent": round(spent, 2),
                "percentage": min(percentage, 100),
                "color": color_map.get(category, "#006699")
            })
        return budgets
    
    def get_recent_expenses(self, limit: int = 5) -> List[Dict]:
        sorted_expenses = sorted(self.expenses, key=lambda x: x["date"], reverse=True)
        recent = sorted_expenses[:limit]
        return [
            {
                "name": exp["name"],
                "category": exp["category"],
                "amount": round(exp["amount"], 2),
                "date": exp["date"].strftime("%Y-%m-%d")
            }
            for exp in recent
        ]
    
    def get_all_expenses(self) -> List[Dict]:
        return [
            {
                "name": exp["name"],
                "category": exp["category"],
                "amount": round(exp["amount"], 2),
                "date": exp["date"].strftime("%Y-%m-%d")
            }
            for exp in self.expenses
        ]
    
    def update_income(self, new_income: float) -> Dict:
        self.monthly_income = new_income
        return {
            "income": self.monthly_income,
            "burn_rate": round(self.get_burn_rate(), 2),
            "savings_rate": self.get_savings_rate()
        }
    
    def get_dashboard_data(self) -> Dict:
        category_spending = self.get_category_spending()
        return {
            "monthly_income": self.monthly_income,
            "total_expenses": self.get_total_expenses(),
            "burn_rate": self.get_burn_rate(),
            "savings_rate": self.get_savings_rate(),
            "recent_expenses": self.get_recent_expenses(),
            "budgets": self.get_budgets(),
            "category_labels": list(category_spending.keys()),
            "category_values": list(category_spending.values()),
            "monthly_expenses_data": self.monthly_expenses_history,
            "monthly_labels": self.monthly_labels
        }


#calendar_router
class CalendarEvent(BaseModel):
    title: str
    date: str
    amount: float
    type: str

class CalendarService:
    def __init__(self):
        self.events = [
            {"title": "Grocery shopping", "date": "2026-04-05", "amount": 156.32, "type": "expense"},
            {"title": "Gas station", "date": "2026-04-03", "amount": 65.00, "type": "expense"},
            {"title": "Restaurant dinner", "date": "2026-04-01", "amount": 89.50, "type": "expense"},
            {"title": "Gym membership", "date": "2026-04-10", "amount": 49.99, "type": "subscription"},
            {"title": "Netflix", "date": "2026-04-15", "amount": 15.99, "type": "subscription"},
            {"title": "Internet bill", "date": "2026-04-01", "amount": 80.00, "type": "bill"},
            {"title": "Salary", "date": "2026-04-15", "amount": 5000.00, "type": "income"},
        ]
    
    def get_events_by_month(self, year: int, month: int) -> Dict[str, List]:
        events_by_date = {}
        for event in self.events:
            event_date = datetime.strptime(event["date"], "%Y-%m-%d")
            if event_date.year == year and event_date.month == month:
                day = str(event_date.day)
                if day not in events_by_date:
                    events_by_date[day] = []
                events_by_date[day].append(event)
        return events_by_date
    
    def get_monthly_totals(self, year: int, month: int) -> Dict:
        total_expenses = 0
        total_income = 0
        for event in self.events:
            event_date = datetime.strptime(event["date"], "%Y-%m-%d")
            if event_date.year == year and event_date.month == month:
                if event["type"] in ["expense", "subscription", "bill"]:
                    total_expenses += event["amount"]
                elif event["type"] == "income":
                    total_income += event["amount"]
        return {"expenses": total_expenses, "income": total_income}
    
    def get_upcoming_events(self, days: int = 14) -> List[Dict]:
        today = datetime.now().date()
        upcoming = []
        for event in self.events:
            event_date = datetime.strptime(event["date"], "%Y-%m-%d").date()
            if today <= event_date <= today + timedelta(days=days):
                upcoming.append(event)
        return sorted(upcoming, key=lambda x: x["date"])
