# Workout Webhook Service

## Features
- `POST /api/v1/webhooks/workout-session` to ingest workout sessions.
- Pydantic payload validation.
- SQLAlchemy persistence in PostgreSQL.
- Idempotency using unique `event_id`.
- `GET /api/v1/sessions/{user_id}` with pagination (`page`, `page_size`).
- Mangum integration for AWS Lambda/API Gateway.

## Sample Webhook JSON
```json
{
  "event_id": "evt_20260307_001",
  "user_id": "user_42",
  "workout_type": "strength",
  "started_at": "2026-03-07T09:00:00Z",
  "ended_at": "2026-03-07T10:00:00Z",
  "calories_burned": 450,
  "exercises": [
    {
      "name": "Squat",
      "sets": 4,
      "reps": 8,
      "weight_kg": 100
    },
    {
      "name": "Bench Press",
      "sets": 4,
      "reps": 6,
      "weight_kg": 80
    }
  ]
}
```

## Run locally
1. Install dependencies:
   `pip install -r requirements.txt`
2. Set database URL:
   `set DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/workouts`
3. Optional startup schema creation toggle:
   `set AUTO_CREATE_TABLES=true`
4. Start API:
   `uvicorn main:app --reload`

## Run tests
`pytest -q`

## Docker
Build image:
`docker build -t workout-webhook-service .`

Run container:
`docker run -p 8000:8000 -e DATABASE_URL=postgresql+psycopg2://postgres:postgres@host.docker.internal:5432/workouts -e AUTO_CREATE_TABLES=true workout-webhook-service`

## AWS Lambda (Mangum)
- Lambda handler: `app.main.handler`
- Alternate wrapper handler: `lambda_handler.handler`
- Deploy behind API Gateway HTTP API and pass `DATABASE_URL` in Lambda environment variables.
