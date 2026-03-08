# Workout Webhook Service

FastAPI service to ingest workout webhook events and store sessions in PostgreSQL with idempotency by `event_id`.

## Features
- `POST /api/v1/webhooks/workout-session` to ingest workout sessions.
- Payload validation with Pydantic.
- SQLAlchemy persistence in PostgreSQL.
- Idempotency using unique `event_id`.
- `GET /api/v1/sessions/{user_id}` with cursor pagination (`cursor_started_at`, `cursor_id`, `page_size`).
- AWS Lambda handler via Mangum (`app.main.handler`).

## Project Structure
- `app/main.py`: FastAPI app, startup DB init, Lambda handler.
- `app/routers/workout.py`: API routes.
- `app/schemas/workout.py`: request/response models and validation.
- `app/services/workout_service.py`: session creation + cursor-based listing logic.
- `app/models.py`: SQLAlchemy models.
- `docker-compose.yml`: local PostgreSQL + API services.

## Environment Variables
- `DATABASE_URL` (default: `postgresql+psycopg2://postgres:postgres@localhost:5432/workout_db`)
- `AUTO_CREATE_TABLES` (default: `true`)

## Run With Docker Compose
1. Build and start services:
   ```bash
   docker compose up --build
   ```
2. API will be available at `http://localhost:8000`.
3. PostgreSQL will be available at `localhost:5432` with:
   - user: `postgres`
   - password: `postgres`
   - database: `workout_db`

To stop:
```bash
docker compose down
```

## API Endpoints
### Ingest workout session
`POST /api/v1/webhooks/workout-session`

Sample request:
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

Sample response:
```json
{
  "id": 1,
  "created": true,
  "message": "session created"
}
```

If the same `event_id` is sent again:
```json
{
  "id": 1,
  "created": false,
  "message": "duplicate webhook ignored"
}
```

### List sessions for a user (cursor pagination)
`GET /api/v1/sessions/{user_id}?page_size=10&cursor_started_at=<ISO_DATETIME>&cursor_id=<INT>`

- `page_size`: 1 to 100 (default 10)
- `cursor_started_at` and `cursor_id`: optional cursor from previous response `next_cursor`

Sample response shape:
```json
{
  "user_id": "user_42",
  "page_size": 10,
  "next_cursor": {
    "cursor_started_at": "2026-03-07T09:00:00+00:00",
    "cursor_id": 1
  },
  "items": [
    {
      "id": 1,
      "event_id": "evt_20260307_001",
      "user_id": "user_42",
      "workout_type": "strength",
      "started_at": "2026-03-07T09:00:00+00:00",
      "ended_at": "2026-03-07T10:00:00+00:00",
      "calories_burned": 450,
      "created_at": "2026-03-08T12:00:00+00:00"
    }
  ]
}
```

## Run Without Docker
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Set environment variables (PowerShell example):
   ```powershell
   $env:DATABASE_URL = "postgresql+psycopg2://postgres:postgres@localhost:5432/workout_db"
   $env:AUTO_CREATE_TABLES = "true"
   ```
3. Start the app:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

## Tests
```bash
pytest -q
```

## AWS Lambda (Mangum)
- Handler: `app.main.handler`
- Configure `DATABASE_URL` in Lambda environment variables.
- Deploy behind API Gateway HTTP API.
