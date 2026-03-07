from fastapi import FastAPI

from app.core.database import Base, engine
from app.routers.workout import router as workout_router

# Ensure SQLAlchemy models are imported before table creation.
from app import models  # noqa: F401

app = FastAPI(title="Workout Webhook Service", version="1.0.0")


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(workout_router, prefix="/api/v1")
