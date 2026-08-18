from fastapi import FastAPI

from app.database import Base, engine
from app.models.user import User
from app.models.widget import Widget
from app.models.submission import Submission

from app.routers import auth
from app.routers import widgets
from app.routers import public
from app.routers import triage


# Create database tables
Base.metadata.create_all(bind=engine)

# Create FastAPI application
app = FastAPI(title="FlyRank Widget Platform")


# Authentication
app.include_router(
    auth.router,
    prefix="/auth",
    tags=["Authentication"]
)


# Widget management
app.include_router(
    widgets.router,
    prefix="/widgets",
    tags=["Widgets"]
)


# Public widgets
app.include_router(
    public.router,
    prefix="/public",
    tags=["Public"]
)


# LLM Triage
app.include_router(
    triage.router,
    prefix="/api",
    tags=["Triage"]
)


@app.get("/")
def root():
    return {
        "message": "FlyRank Widget Platform API"
    }