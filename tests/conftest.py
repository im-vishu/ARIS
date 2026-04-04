import os

import pytest
from fastapi.testclient import TestClient

# test-safe env defaults
os.environ.setdefault("APP_ENV", "test")
os.environ.setdefault("JWT_SECRET", "test-secret")
os.environ.setdefault("JWT_ALG", "HS256")
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MIN", "30")
os.environ.setdefault("REFRESH_TOKEN_EXPIRE_MIN", "10080")
os.environ.setdefault("RATE_LIMIT_ENABLED", "false")
os.environ.setdefault("RATE_LIMIT_PER_MINUTE", "5")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")
os.environ.setdefault("OPENAI_API_KEY", "sk-test-key")

from app.api import app  # noqa: E402


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c