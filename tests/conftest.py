import os

# Must be set before the imports below, as src/connection.py picks its .env file on import
os.environ["ENV"] = "test"


# A low bcrypt cost keeps the seed fast
os.environ["BCRYPT_ROUNDS"] = "4"

os.environ["JWT_SECRET"] = "test-secret"

import pytest
from fastapi.testclient import TestClient

from app.main import app
from db.seed import seed


@pytest.fixture(autouse=True)
def reset_db():
    seed()


@pytest.fixture()
def client():
    return TestClient(app)