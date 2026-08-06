from fastapi import FastAPI

from app.database import Base, engine

from app.models import user, widget, submission

Base.metadata.create_all(bind=engine)

app = FastAPI(title="FlyRank Widget Platform")


@app.get("/")
def root():
    return {
        "message": "FlyRank Widget Platform API"
    }