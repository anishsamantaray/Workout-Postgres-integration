import math

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

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
    db: Session, user_id: str, page: int, page_size: int
) -> tuple[list[WorkoutSession], int, int]:
    total_items = db.execute(
        select(func.count(WorkoutSession.id)).where(WorkoutSession.user_id == user_id)
    ).scalar_one()
    total_pages = math.ceil(total_items / page_size) if total_items else 0

    offset = (page - 1) * page_size
    items = (
        db.execute(
            select(WorkoutSession)
            .where(WorkoutSession.user_id == user_id)
            .order_by(WorkoutSession.started_at.desc())
            .offset(offset)
            .limit(page_size)
        )
        .scalars()
        .all()
    )
    return items, total_items, total_pages
