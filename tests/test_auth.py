import os
import jwt
import pytest

INVALID_CREDENTIALS = {"detail": "Invalid email or password"}
MISSING_FIELDS = {"detail": "Email and password are required"}


def decode(token):
    return jwt.decode(token, os.environ["JWT_SECRET"], algorithms=["HS256"])


def test_login_responds_with_200_for_valid_credentials(client):
    response = client.post("/api/auth/login", json={"email": "alice@example.com", "password": "password123"})

    assert response.status_code == 200


def test_login_returns_object_with_only_a_token_key(client):
    body = client.post("/api/auth/login", json={"email": "alice@example.com", "password": "password123"}).json()

    assert list(body.keys()) == ["token"]
    assert isinstance(body["token"], str)


def test_login_token_is_signed_and_identifies_the_user(client):
    token = client.post("/api/auth/login", json={"email": "bob@example.com", "password": "password123"}).json()["token"]

    payload = decode(token)

    # Bob is the second seeded user
    assert payload["sub"] == "2"
    assert "exp" in payload


def test_login_token_is_rejected_if_signed_with_a_different_secret(client):
    token = client.post("/api/auth/login", json={"email": "alice@example.com", "password": "password123"}).json()["token"]

    with pytest.raises(jwt.InvalidSignatureError):
        jwt.decode(token, "not-the-real-secret", algorithms=["HS256"])


def test_login_responds_with_401_when_password_is_wrong(client):
    response = client.post("/api/auth/login", json={"email": "alice@example.com", "password": "wrongpassword"})

    assert response.status_code == 401
    assert response.json() == INVALID_CREDENTIALS


def test_login_responds_with_401_when_email_does_not_exist(client):
    response = client.post("/api/auth/login", json={"email": "nobody@example.com", "password": "password123"})

    assert response.status_code == 401
    assert response.json() == INVALID_CREDENTIALS


def test_login_gives_the_same_response_for_wrong_email_and_wrong_password(client):
    wrong_email = client.post("/api/auth/login", json={"email": "nobody@example.com", "password": "password123"})
    wrong_password = client.post("/api/auth/login", json={"email": "alice@example.com", "password": "wrongpassword"})

    assert wrong_email.status_code == wrong_password.status_code == 401
    assert wrong_email.json() == wrong_password.json()


@pytest.mark.parametrize(
    "body",
    [
        {"password": "password123"},
        {"email": "alice@example.com"},
        {},
        {"email": "", "password": "password123"},
        {"email": "alice@example.com", "password": ""},
        {"email": 123, "password": "password123"},
        {"email": "alice@example.com", "password": None},
    ],
)
def test_login_responds_with_400_when_a_field_is_missing_or_invalid(client, body):
    response = client.post("/api/auth/login", json=body)

    assert response.status_code == 400
    assert response.json() == MISSING_FIELDS


@pytest.mark.parametrize("raw_body", ["", "not json", "[]", '"alice@example.com"'])
def test_login_responds_with_400_when_body_is_not_a_json_object(client, raw_body):
    response = client.post("/api/auth/login", content=raw_body, headers={"Content-Type": "application/json"})

    assert response.status_code == 400
    assert response.json() == MISSING_FIELDS