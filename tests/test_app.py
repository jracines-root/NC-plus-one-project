from datetime import datetime

import pytest

from src.connection import get_db_connection


def test_get_events_responds_with_200(client):
    response = client.get("/api/events")

    assert response.status_code == 200


def test_get_events_returns_object_with_events_key(client):
    body = client.get("/api/events").json()

    assert isinstance(body, dict)
    assert list(body.keys()) == ["events"]


def test_get_events_returns_all_seeded_events(client):
    events = client.get("/api/events").json()["events"]

    assert len(events) == 10


def test_get_events_returns_expected_fields(client):
    events = client.get("/api/events").json()["events"]

    for event in events:
        assert set(event.keys()) == {"id", "title", "starts_at", "ends_at", "location"}


def test_get_events_are_ordered_by_soonest_start(client):
    events = client.get("/api/events").json()["events"]

    starts = [datetime.fromisoformat(event["starts_at"]) for event in events]
    assert starts == sorted(starts)


def test_get_events_location_combines_venue_name_and_address(client):
    events = client.get("/api/events").json()["events"]

    first_event = next(event for event in events if event["id"] == 1)
    assert first_event["title"] == "Leeds Tech Meetup – June Edition"
    assert first_event["location"] == "Nexus, University of Leeds, Discovery Way, Leeds, LS2 3AA"


def test_get_events_location_is_venue_name_when_address_is_missing(client):
    events = client.get("/api/events").json()["events"]

    online_event = next(event for event in events if event["id"] == 2)
    assert online_event["location"] == "Online – Zoom"


def test_get_events_includes_event_without_a_venue(client):
    conn = get_db_connection()
    try:
        with conn, conn.cursor() as cur:
            cur.execute(
                """INSERT INTO events (title, starts_at, ends_at)
                VALUES ('No Venue Yet', '2027-01-01T18:00:00+00:00', '2027-01-01T20:00:00+00:00');"""
            )
    finally:
        conn.close()

    events = client.get("/api/events").json()["events"]

    assert len(events) == 11
    assert events[-1]["title"] == "No Venue Yet"
    assert events[-1]["location"] is None


def test_get_event_by_id_responds_with_200(client):
    response = client.get("/api/events/2")

    assert response.status_code == 200


def test_get_event_by_id_returns_object_with_event_key(client):
    body = client.get("/api/events/2").json()

    assert list(body.keys()) == ["event"]


def test_get_event_by_id_returns_the_correct_event(client):
    event = client.get("/api/events/2").json()["event"]

    assert event["id"] == 2
    assert event["title"] == "Intro to Machine Learning Workshop"
    assert event["description"] == (
        "Hands-on workshop covering perceptrons, neural networks, and classifiers using NumPy and PyTorch."
    )
    assert datetime.fromisoformat(event["starts_at"]) == datetime.fromisoformat("2026-06-25T10:00:00+01:00")
    assert datetime.fromisoformat(event["ends_at"]) == datetime.fromisoformat("2026-06-25T13:00:00+01:00")
    assert datetime.fromisoformat(event["created_at"])


def test_get_event_by_id_returns_expected_fields(client):
    event = client.get("/api/events/2").json()["event"]

    assert set(event.keys()) == {
        "id",
        "title",
        "description",
        "starts_at",
        "ends_at",
        "location",
        "address",
        "capacity",
        "created_at",
    }


def test_get_event_by_id_includes_venue_details(client):
    event = client.get("/api/events/1").json()["event"]

    assert event["location"] == "Nexus, University of Leeds"
    assert event["address"] == "Discovery Way, Leeds, LS2 3AA"
    assert event["capacity"] == 200


def test_get_event_by_id_address_is_null_for_online_venue(client):
    event = client.get("/api/events/2").json()["event"]

    assert event["location"] == "Online – Zoom"
    assert event["address"] is None
    assert event["capacity"] == 500


def test_get_event_by_id_includes_event_without_a_venue(client):
    conn = get_db_connection()
    try:
        with conn, conn.cursor() as cur:
            cur.execute(
                """INSERT INTO events (title, starts_at, ends_at)
                VALUES ('No Venue Yet', '2027-01-01T18:00:00+00:00', '2027-01-01T20:00:00+00:00')
                RETURNING id;"""
            )
            event_id = cur.fetchone()[0]
    finally:
        conn.close()

    response = client.get(f"/api/events/{event_id}")

    assert response.status_code == 200
    assert response.json()["event"]["location"] is None


@pytest.mark.parametrize("event_id", ["9999", "0", "-1", "99999999999999999999"])
def test_get_event_by_id_responds_with_404_when_event_does_not_exist(client, event_id):
    response = client.get(f"/api/events/{event_id}")

    assert response.status_code == 404
    assert response.json() == {"detail": "Event not found"}


@pytest.mark.parametrize("event_id", ["abc", "1.5", "1.0", "1_000", "2abc", "1" * 5000])
def test_get_event_by_id_responds_with_400_when_id_is_invalid(client, event_id):
    response = client.get(f"/api/events/{event_id}")

    assert response.status_code == 400
    assert response.json() == {"detail": "Event id must be an integer"}