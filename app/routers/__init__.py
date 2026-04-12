from fastapi import APIRouter
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from app.config import get_settings
from jinja2 import FileSystemLoader, Environment


_env = Environment(
    loader=FileSystemLoader("app/templates"),
    auto_reload=True,
    cache_size=0,
)

def min_filter(value, arg):
    try:
        return min(value, arg)
    except (TypeError, ValueError):
        return value

_env.filters['min'] = min_filter
_env.globals['get_flashed_messages'] = lambda: []


templates = Jinja2Templates(directory="app/templates")
templates.env = _env

static_files = StaticFiles(directory="app/static")

router = APIRouter(
    tags=["Jinja Based Endpoints"],
    include_in_schema=get_settings().env.lower() in ["dev", "development"]
)
api_router = APIRouter(tags=["API Endpoints"], prefix="/api")

from . import (index, login, register, admin_home, user_home, users, logout,
               finance_router, expenses_router, subscriptions_router, budget_router,
               reports_router, savings_router, calendar_router)