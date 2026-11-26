from datetime import datetime

import pytest

from src.connection import get_db_connection
from src.utils import verify_password

NEW_USER = {"name": "Grace Hopper", "email": "grace@example.com", "password": "securepassword123"}
EMAIL_TAKEN = {"detail": "Email is already registered"}
MISSING_FIELDS = {"detail": "Name, email and password are required"}


def count_users():
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM users;")
            return cur.fetchone()[0]
    finally:
        conn.close()


def fetch_stored_password(email):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT password FROM users WHERE email = %s;", (email,))
            return cur.fetchone()[0]
    finally:
        conn.close()


def test_register_responds_with_201(client):
    response = client.post("/api/auth/register", json=NEW_USER)

    assert response.status_code == 201


def test_register_returns_object_with_a_user_key(client):
    body = client.post("/api/auth/register", json=NEW_USER).json()

    assert list(body.keys()) == ["user"]


def test_register_returns_the_created_user(client):
    user = client.post("/api/auth/register", json=NEW_USER).json()["user"]

    # 6 users are seeded, so the new one is the 7th
    assert user["id"] == 7
    assert user["name"] == "Grace Hopper"
    assert user["email"] == "grace@example.com"
    assert datetime.fromisoformat(user["created_at"])


def test_register_never_returns_the_password(client):
    user = client.post("/api/auth/register", json=NEW_USER).json()["user"]

    assert set(user.keys()) == {"id", "name", "email", "created_at"}
    assert "securepassword123" not in str(user)


def test_register_stores_the_user_in_the_database(client):
    client.post("/api/auth/register", json=NEW_USER)

    assert count_users() == 7


def test_register_stores_a_hash_not_the_plaintext_password(client):
    client.post("/api/auth/register", json=NEW_USER)

    stored = fetch_stored_password("grace@example.com")

    assert stored != "securepassword123"
    assert stored.startswith("$2b$")
    assert verify_password("securepassword123", stored)


def test_registered_user_can_log_in(client):
    client.post("/api/auth/register", json=NEW_USER)

    response = client.post(
        "/api/auth/login", json={"email": "grace@example.com", "password": "securepassword123"}
    )

    assert response.status_code == 200
    assert "token" in response.json()


def test_register_responds_with_409_when_email_is_already_seeded(client):
    response = client.post(
        "/api/auth/register",
        json={"name": "Another Alice", "email": "alice@example.com", "password": "securepassword123"},
    )

    assert response.status_code == 409
    assert response.json() == EMAIL_TAKEN
    assert count_users() == 6


def test_register_responds_with_409_when_registering_the_same_email_twice(client):
    client.post("/api/auth/register", json=NEW_USER)
    response = client.post("/api/auth/register", json=NEW_USER)

    assert response.status_code == 409
    assert response.json() == EMAIL_TAKEN
    assert count_users() == 7


@pytest.mark.parametrize(
    "body",
    [
        {"email": "grace@example.com", "password": "securepassword123"},
        {"name": "Grace Hopper", "password": "securepassword123"},
        {"name": "Grace Hopper", "email": "grace@example.com"},
        {},
        {"name": "", "email": "grace@example.com", "password": "securepassword123"},
        {"name": "Grace Hopper", "email": "", "password": "securepassword123"},
        {"name": "Grace Hopper", "email": "grace@example.com", "password": ""},
        {"name": 42, "email": "grace@example.com", "password": "securepassword123"},
        {"name": "Grace Hopper", "email": None, "password": "securepassword123"},
    ],
)
def test_register_responds_with_400_when_a_field_is_missing_or_invalid(client, body):
    response = client.post("/api/auth/register", json=body)

    assert response.status_code == 400
    assert response.json() == MISSING_FIELDS
    assert count_users() == 6


@pytest.mark.parametrize("raw_body", ["", "not json", "[]", '"grace@example.com"'])
def test_register_responds_with_400_when_body_is_not_a_json_object(client, raw_body):
    response = client.post("/api/auth/register", content=raw_body, headers={"Content-Type": "application/json"})

    assert response.status_code == 400
    assert response.json() == MISSING_FIELDS