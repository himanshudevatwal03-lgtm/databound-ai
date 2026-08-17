"""
main.py

The FastAPI application entrypoint.

This is the file `uvicorn` points to when the backend container starts
(see the Dockerfile CMD). Its job in Phase 1 is deliberately small:
  1. create the FastAPI app
  2. configure CORS so the React frontend (a different origin) can call it
  3. register the health-check router

As later phases add auth, documents, questions, notes, etc., each feature
gets its own router module under app/api/, and we simply include it here.
This keeps main.py from turning into a 2000-line file.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.api import auth, collections, documents, health
from app.database.session import Base, engine
from app import models  # noqa: F401 — registers models with Base.metadata


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Runs once at startup: creates any tables that don't exist yet, based
    on every model imported via app.models. This is a Phase 2 shortcut —
    fine for early development, but a real migration tool (Alembic) is
    the right call once the schema needs to evolve without dropping data.
    Tracked for a later phase.
    """
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title=settings.APP_NAME,
    description=(
        "DataBound AI — a data-grounded question-answering platform. "
        "Answers are generated only from user-provided documents, with "
        "verifiable source citations."
    ),
    version="0.3.0",
    lifespan=lifespan,
)

# CORS (Cross-Origin Resource Sharing): the React dev server runs on
# http://localhost:5173 while the API runs on a different port. Browsers
# block cross-origin requests by default, so we explicitly allow the
# frontend's origin(s) here.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



# Every route in health.py/auth.py is mounted under /api
# (e.g. /api/health, /api/auth/login).
app.include_router(health.router, prefix=settings.API_V1_PREFIX)
app.include_router(auth.router, prefix=settings.API_V1_PREFIX)
app.include_router(collections.router, prefix=settings.API_V1_PREFIX)
app.include_router(documents.router, prefix=settings.API_V1_PREFIX)


@app.get("/")
def root():
    """Simple root endpoint so visiting the API base URL isn't a 404."""
    return {
        "message": f"{settings.APP_NAME} API is running",
        "docs": "/docs",
        "health": f"{settings.API_V1_PREFIX}/health",
    }
