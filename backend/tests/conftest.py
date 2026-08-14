"""
conftest.py

Shared pytest fixtures.

`client` gives every test a FastAPI TestClient with tables already
created (mirroring what main.py's startup event does in production).
`db_session` gives tests direct DB access for setup/teardown — mainly so
each test can delete the users it created afterward, keeping tests
independent of each other and safe to re-run.
"""

import pytest
from fastapi.testclient import TestClient

from app.database.session import Base, SessionLocal, engine
from app.main import app
from app import models  # noqa: F401 — ensures User is registered on Base


@pytest.fixture(scope="session", autouse=True)
def create_test_tables():
    Base.metadata.create_all(bind=engine)
    yield


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def db_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def cleanup_users(db_session):
    """
    Call this fixture in any test that registers users, to guarantee they
    don't leak into other test runs (which would cause spurious "email
    already exists" failures on repeated `pytest` runs).
    """
    from app.models.user import User

    created_emails = []
    yield created_emails
    if created_emails:
        db_session.query(User).filter(User.email.in_(created_emails)).delete(
            synchronize_session=False
        )
        db_session.commit()
