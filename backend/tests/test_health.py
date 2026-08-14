"""
test_health.py

Phase 1's only test: confirm the API boots and the /api/health endpoint
responds with a 200 and the expected shape. Later phases add many more
tests (auth, uploads, retrieval, hallucination checks, etc.) under this
same tests/ directory.

Run with:
    pytest
from inside the backend/ directory (with DATABASE_URL pointing at a
reachable Postgres instance — e.g. via `docker compose up postgres`).
"""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    body = response.json()
    assert "message" in body


def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["database"] == "connected"
