import math
from sqlalchemy import select, and_, or_
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional
from app.models import WorkoutSession
from app.schemas.workout import WorkoutSessionIn


def create_workout_session(db: Session, payload: WorkoutSessionIn) -> tuple[WorkoutSession, bool]:
    existing = db.execute(
        select(WorkoutSession).where(WorkoutSession.event_id == payload.event_id)
    ).scalar_one_or_none()
    if existing:
        return existing, False

    session = WorkoutSession(
        event_id=payload.event_id,
        user_id=payload.user_id,
        workout_type=payload.workout_type,
        started_at=payload.started_at,
        ended_at=payload.ended_at,
        calories_burned=payload.calories_burned,
        payload=payload.model_dump(mode="json"),
    )
    db.add(session)

    try:
        db.commit()
        db.refresh(session)
        return session, True
    except IntegrityError:
        db.rollback()
        existing = db.execute(
            select(WorkoutSession).where(WorkoutSession.event_id == payload.event_id)
        ).scalar_one()
        return existing, False


def list_user_sessions(
    db: Session,
    user_id: str,
    cursor_started_at: Optional[datetime],
    cursor_id: Optional[int],
    page_size: int,
):

    query = (
        select(WorkoutSession)
        .where(WorkoutSession.user_id == user_id)
        .order_by(
            WorkoutSession.started_at.desc(),
            WorkoutSession.id.desc(),
        )
        .limit(page_size)
    )

    if cursor_started_at and cursor_id:
        query = query.where(
            or_(
                WorkoutSession.started_at < cursor_started_at,
                and_(
                    WorkoutSession.started_at == cursor_started_at,
                    WorkoutSession.id < cursor_id,
                ),
            )
        )

    items = db.execute(query).scalars().all()

    next_cursor = None
    if items:
        last = items[-1]
        next_cursor = {
            "cursor_started_at": last.started_at,
            "cursor_id": last.id,
        }

    return items, next_cursor