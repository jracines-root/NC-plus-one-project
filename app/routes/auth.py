import os
from datetime import datetime, timedelta, timezone
from json import JSONDecodeError

import jwt
from fastapi import APIRouter, HTTPException, Request
from app.models.users import fetch_user_by_email
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


@router.post("/api/auth/login")
async def login(request: Request):

    try:
        body = await request.json()
    except (JSONDecodeError, UnicodeDecodeError):
        body = None

    email = body.get("email") if isinstance(body, dict) else None
    password = body.get("password") if isinstance(body, dict) else None

    if not isinstance(email, str) or not isinstance(password, str) or not email or not password:
        raise HTTPException(status_code=400, detail="Email and password are required")

    user = fetch_user_by_email(email)

    # The same 401 for a wrong email and a wrong password
    password_matches = verify_password(password, user["password"] if user else DUMMY_HASH)

    if user is None or not password_matches:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    return {"token": create_token(user["id"])}