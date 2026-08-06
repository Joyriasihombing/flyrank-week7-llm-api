from fastapi import FastAPI

from app.database import Base, engine
from app.models import user, widget, submission
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

# Root endpoint
@app.get("/")
def root():
    return {"message": "FlyRank Widget Platform API"}