import os
from datetime import datetime, timedelta, timezone
from json import JSONDecodeError

import jwt
from fastapi import APIRouter, HTTPException, Request
from app.models.users import fetch_user_by_email
from src.utils import hash_password, verify_password