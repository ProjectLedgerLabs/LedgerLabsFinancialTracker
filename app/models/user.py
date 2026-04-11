from datetime import datetime

from sqlmodel import Field, Relationship, SQLModel
from typing import Optional
from pydantic import EmailStr
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
    # role:str = ""

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

    user_rel = Relationship(back_populates="entries")
    category_rel = Relationship(back_populates="entries")

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

    category_rel = Relationship(back_populates="subscriptions")
    user_rel = Relationship(back_populates="subscriptions")

class Category (SQLModel, table=True):
    category_id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    user_id: Optional[int] = Field(default=None, foreign_key="user.user_id")
    
    entries: list["Entry"] = Relationship(back_populates="category_rel")
    subscriptions: list["Subscription"] = Relationship(back_populates="category_rel")
    user_rel = Relationship(back_populates="categories")
    

class CalendarEvent (SQLModel, table=True):
    event_id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(default=None, foreign_key="user.user_id")
    type: CalendarEventType
    title: str
    description: Optional[str] = None
    date: Optional[datetime] = None
    user_rel = Relationship(back_populates="calendar_events")

class SavingsGoal (SQLModel, table=True):
    goal_id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(default=None, foreign_key="user.user_id")
    name: str
    target_amount: float
    current_amount: float = 0.0
    description: Optional[str] = None
    deadline: Optional[datetime] = None
    user_rel = Relationship(back_populates="savings_goals")