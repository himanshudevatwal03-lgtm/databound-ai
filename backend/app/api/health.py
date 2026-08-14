"""
health.py

A tiny router that exposes /api/health.

Why we need this:
When you deploy with Docker Compose, or when the frontend starts up, you
need a fast, reliable way to check "is the backend alive, and can it reach
the database?" without hitting any real business logic. Health checks like
this are standard practice in production systems (load balancers and
container orchestrators poll them to decide if a service is ready).
"""

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database.session import get_db

router = APIRouter(tags=["health"])


@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    """
    Returns overall API status plus a database connectivity check.

    We run `SELECT 1` — the simplest possible query — purely to confirm the
    connection pool can actually reach PostgreSQL. If this fails, FastAPI's
    exception handling will surface a 500 error, which is exactly what we
    want a health check to do when the DB is down.
    """
    db.execute(text("SELECT 1"))
    return {
        "status": "ok",
        "service": "databound-ai-backend",
        "database": "connected",
    }
