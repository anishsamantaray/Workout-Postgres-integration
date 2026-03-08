from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, model_validator


class Exercise(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    sets: int = Field(..., ge=1)
    reps: int = Field(..., ge=1)
    weight_kg: float | None = Field(default=None, ge=0)


class WorkoutSessionIn(BaseModel):
    event_id: str = Field(..., min_length=1, max_length=100)
    user_id: str = Field(..., min_length=1, max_length=100)
    workout_type: str = Field(..., min_length=1, max_length=100)
    started_at: datetime
    ended_at: datetime
    calories_burned: int | None = Field(default=None, ge=0)
    exercises: list[Exercise] = Field(..., min_length=1)

    @model_validator(mode="after")
    def validate_times(self) -> "WorkoutSessionIn":
        if self.ended_at <= self.started_at:
            raise ValueError("ended_at must be greater than started_at")
        return self


class WorkoutSessionOut(BaseModel):
    id: int
    event_id: str
    user_id: str
    workout_type: str
    started_at: datetime
    ended_at: datetime
    calories_burned: int | None
    created_at: datetime

    model_config = {"from_attributes": True}


class WebhookIngestResponse(BaseModel):
    id: int
    created: bool
    message: str


class SessionListResponse(BaseModel):
    user_id: str
    page_size: int
    next_cursor: Optional[dict]
    items: list[WorkoutSessionOut]