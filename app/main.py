from fastapi import FastAPI
from mangum import Mangum
from app.core.config import settings
from app.core.database import Base, engine
from app.routers.workout import router as workout_router


import app.models  # noqa: F401

app = FastAPI(title="Workout Webhook Service", version="1.0.0")


def init_db() -> None:
    if settings.AUTO_CREATE_TABLES:
        Base.metadata.create_all(bind=engine)

app.include_router(workout_router, prefix="/api/v1")

# AWS Lambda entry point.
handler = Mangum(app)
