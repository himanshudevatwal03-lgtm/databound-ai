"""
session.py

Sets up the SQLAlchemy engine and session machinery used to talk to
PostgreSQL.

Why we need this:
FastAPI route functions shouldn't open raw database connections themselves.
Instead, we create one Engine (a connection pool) for the whole app, and a
SessionLocal factory that produces short-lived Session objects — one per
request. The `get_db` dependency function is what FastAPI calls to hand a
fresh session to each endpoint, and it guarantees the session is closed
afterwards even if an error occurs.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.config import settings

# The engine manages a pool of physical connections to PostgreSQL.
# pool_pre_ping checks that a pulled connection is still alive before use,
# which avoids errors after the DB restarts or an idle connection drops.
engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)

# SessionLocal is a factory: calling SessionLocal() gives a new DB session.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base is the class every ORM model (User, Document, etc.) will inherit
# from. SQLAlchemy uses it to know which Python classes map to which tables.
Base = declarative_base()


def get_db():
    """
    FastAPI dependency that yields a database session and ensures it is
    closed after the request finishes, whether it succeeded or raised.

    Usage in an endpoint:
        def my_route(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
