from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
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
    cursor_started_at: Optional[datetime] = Query(default=None),
    cursor_id: Optional[int] = Query(default=None),
    page_size: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
) -> SessionListResponse:

    items, next_cursor = list_user_sessions(
        db,
        user_id,
        cursor_started_at,
        cursor_id,
        page_size,
    )

    return SessionListResponse(
        user_id=user_id,
        page_size=page_size,
        next_cursor=next_cursor,
        items=items,
    )