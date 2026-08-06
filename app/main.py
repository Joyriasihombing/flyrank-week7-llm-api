from fastapi import FastAPI

from app.routers import widgets
from app.database import Base, engine
from app.models.user import User
from app.models.widget import Widget
from app.models.submission import Submission
from app.routers import auth
# Buat tabel database
Base.metadata.create_all(bind=engine)

# Buat aplikasi FastAPI
app = FastAPI(title="FlyRank Widget Platform")

# Daftarkan router
app.include_router(
    auth.router,
    prefix="/auth",
    tags=["Authentication"]
)

app.include_router(
    widgets.router,
    prefix="/widgets",
    tags=["Widgets"]
)

# Root endpoint
@app.get("/")
def root():
    return {"message": "FlyRank Widget Platform API"}
#root public
from app.routers import public
app.include_router(
    public.router,
    prefix="/public",
    tags=["Public"]
)