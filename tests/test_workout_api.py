from typing import Dict


def build_payload(event_id: str, user_id: str = "user-123") -> Dict:
    return {
        "event_id": event_id,
        "user_id": user_id,
        "workout_type": "strength",
        "started_at": "2026-03-07T09:00:00Z",
        "ended_at": "2026-03-07T10:00:00Z",
        "calories_burned": 450,
        "exercises": [
            {"name": "Squat", "sets": 4, "reps": 8, "weight_kg": 100},
            {"name": "Bench Press", "sets": 4, "reps": 6, "weight_kg": 80},
        ],
    }


def test_ingest_webhook_creates_session(client):
    response = client.post(
        "/api/v1/webhooks/workout-session",
        json=build_payload("evt-1"),
    )

    assert response.status_code == 200

    data = response.json()
    assert data["created"] is True
    assert data["message"] == "session created"
    assert isinstance(data["id"], int)


def test_webhook_idempotency_prevents_duplicate_records(client):
    payload = build_payload("evt-2")

    first = client.post("/api/v1/webhooks/workout-session", json=payload)
    second = client.post("/api/v1/webhooks/workout-session", json=payload)

    assert first.status_code == 200
    assert second.status_code == 200

    first_data = first.json()
    second_data = second.json()

    assert first_data["created"] is True
    assert second_data["created"] is False
    assert second_data["message"] == "duplicate webhook ignored"

    # Same record returned
    assert first_data["id"] == second_data["id"]


def test_get_sessions_for_user_with_cursor_pagination(client):
    # Create sessions
    client.post("/api/v1/webhooks/workout-session", json=build_payload("evt-3", "user-a"))
    client.post("/api/v1/webhooks/workout-session", json=build_payload("evt-4", "user-a"))
    client.post("/api/v1/webhooks/workout-session", json=build_payload("evt-5", "user-a"))
    client.post("/api/v1/webhooks/workout-session", json=build_payload("evt-6", "user-b"))

    # First page
    page_one = client.get("/api/v1/sessions/user-a?page_size=2")

    assert page_one.status_code == 200

    page_one_data = page_one.json()

    assert len(page_one_data["items"]) == 2
    assert page_one_data["next_cursor"] is not None
    assert all(item["user_id"] == "user-a" for item in page_one_data["items"])

    cursor = page_one_data["next_cursor"]

    # Second page
    page_two = client.get(
        f"/api/v1/sessions/user-a?page_size=2"
        f"&cursor_started_at={cursor['cursor_started_at']}"
        f"&cursor_id={cursor['cursor_id']}"
    )

    assert page_two.status_code == 200

    page_two_data = page_two.json()

    assert len(page_two_data["items"]) == 1
    assert all(item["user_id"] == "user-a" for item in page_two_data["items"])


def test_sessions_are_sorted_descending(client):
    client.post("/api/v1/webhooks/workout-session", json=build_payload("evt-10"))
    client.post("/api/v1/webhooks/workout-session", json=build_payload("evt-11"))

    response = client.get("/api/v1/sessions/user-123?page_size=10")

    assert response.status_code == 200

    data = response.json()

    timestamps = [item["started_at"] for item in data["items"]]

    assert timestamps == sorted(timestamps, reverse=True)


def test_validation_fails_for_invalid_time_range(client):
    payload = build_payload("evt-7")
    payload["ended_at"] = "2026-03-07T08:00:00Z"

    response = client.post(
        "/api/v1/webhooks/workout-session",
        json=payload,
    )

    assert response.status_code == 422