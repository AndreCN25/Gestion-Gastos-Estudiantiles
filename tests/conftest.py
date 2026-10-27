import os
import tempfile
import pytest

_fd, _db_path = tempfile.mkstemp(suffix=".db")
os.close(_fd)
os.environ["DATABASE_URL"] = f"sqlite:///{_db_path}"
os.environ["SECRET_KEY"] = "test-secret-that-is-not-used-in-production"

from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine

@pytest.fixture(autouse=True)
def clean_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield

@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c

@pytest.fixture
def auth_headers(client):
    client.post("/api/auth/register", json={"email":"ana@example.com","password":"estudiante-segura-123"})
    response=client.post("/api/auth/login", json={"email":"ana@example.com","password":"estudiante-segura-123"})
    return {"Authorization":f"Bearer {response.json()['access_token']}"}
