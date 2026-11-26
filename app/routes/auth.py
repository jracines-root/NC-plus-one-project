import os
from datetime import datetime, timedelta, timezone
from json import JSONDecodeError

import jwt
from fastapi import APIRouter, HTTPException, Request

from app.models.users import EmailAlreadyRegistered, fetch_user_by_email, insert_user
from src.utils import hash_password, verify_password

router = APIRouter()

TOKEN_LIFETIME = timedelta(hours=1)

# Checked against when the email doesn't exist, so a wrong email takes as long as a
# wrong password. Otherwise the response time would reveal which emails are registered.
DUMMY_HASH = hash_password("not-a-real-password")


def create_token(user_id):
    """Sign a JWT that identifies the user on later requests."""
    try:
        secret = os.environ["JWT_SECRET"]
    except KeyError as e:
        raise RuntimeError("Missing environment variable 'JWT_SECRET'. Add it to your .env file.") from e

    payload = {
        "sub": str(user_id),
        "exp": datetime.now(timezone.utc) + TOKEN_LIFETIME,
    }

    return jwt.encode(payload, secret, algorithm="HS256")


async def read_required_fields(request, fields, error_message):
    """Return the named fields from the JSON body, or answer with a 400 if any is missing or not text."""
    # The body is read by hand, because FastAPI would answer a missing field with a 422,
    # and the tickets need a 400.
    try:
        body = await request.json()
    except (JSONDecodeError, UnicodeDecodeError):
        body = None

    if not isinstance(body, dict):
        raise HTTPException(status_code=400, detail=error_message)

    values = [body.get(field) for field in fields]

    if not all(isinstance(value, str) and value for value in values):
        raise HTTPException(status_code=400, detail=error_message)

    return values


@router.post("/api/auth/register", status_code=201)
async def register(request: Request):
    name, email, password = await read_required_fields(
        request, ["name", "email", "password"], "Name, email and password are required"
    )

    try:
        user = insert_user(name, email, hash_password(password))
    except EmailAlreadyRegistered:
        raise HTTPException(status_code=409, detail="Email is already registered")

    return {"user": user}


@router.post("/api/auth/login")
async def login(request: Request):
    email, password = await read_required_fields(
        request, ["email", "password"], "Email and password are required"
    )

    user = fetch_user_by_email(email)

    # The same 401 for a wrong email and a wrong password, so the response never
    # reveals which one was wrong.
    password_matches = verify_password(password, user["password"] if user else DUMMY_HASH)

    if user is None or not password_matches:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    return {"token": create_token(user["id"])}