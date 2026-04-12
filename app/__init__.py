from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from contextlib import asynccontextmanager
from app.config import get_settings
from app.utilities.flash import get_flashed_messages

templates = Jinja2Templates(directory="app/templates")

def min_filter(value, arg):
    return min(value, arg)

templates.env.filters['min'] = min_filter

templates.env.globals['get_flashed_messages'] = get_flashed_messages

static_files = StaticFiles(directory="app/static")

@asynccontextmanager
async def lifespan(app: FastAPI):
    from app.database import create_db_and_tables
    create_db_and_tables()
    yield

def create_app():
    """Application factory pattern"""
    settings = get_settings()
    
    app = FastAPI(
        middleware=[
            Middleware(SessionMiddleware, secret_key=settings.secret_key)
        ],
        lifespan=lifespan
    )
    
  
    from app.routers import (
        router, api_router, finance_router, expenses_router, 
        subscriptions_router, budget_router, reports_router, 
        savings_router, calendar_router
    )
    
    app.include_router(router)
    app.include_router(api_router)
    app.include_router(finance_router.router)
    app.include_router(expenses_router.router)
    app.include_router(subscriptions_router.router)
    app.include_router(budget_router.router)
    app.include_router(reports_router.router)
    app.include_router(savings_router.router)
    app.include_router(calendar_router.router)
    app.mount("/static", static_files, name="static")
    
  
    @app.exception_handler(401)
    async def unauthorized_redirect_handler(request, exc):
        return templates.TemplateResponse(
            request=request, 
            name="401.html",
        )
    
    return app