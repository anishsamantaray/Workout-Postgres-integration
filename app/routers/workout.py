from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.workout import (
    SessionListResponse,
    WebhookIngestResponse,
    WorkoutSessionIn,
)
from app.services.workout_service import create_workout_session, list_user_sessions

router = APIRouter(tags=["workouts"])


@router.post("/webhooks/workout-session", response_model=WebhookIngestResponse)
def ingest_workout_session(payload: WorkoutSessionIn, db: Session = Depends(get_db)) -> WebhookIngestResponse:
    session, created = create_workout_session(db, payload)
    message = "session created" if created else "duplicate webhook ignored"
    return WebhookIngestResponse(id=session.id, created=created, message=message)


@router.get("/sessions/{user_id}", response_model=SessionListResponse)
def get_sessions_for_user(
    user_id: str,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
) -> SessionListResponse:
    items, total_items, total_pages = list_user_sessions(db, user_id, page, page_size)
    return SessionListResponse(
        user_id=user_id,
        page=page,
        page_size=page_size,
        total_items=total_items,
        total_pages=total_pages,
        items=items,
    )
