from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.database import engine, Base, get_db
from app.config import get_settings
from app.api.routes import health

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="DataBound AI",
    description="Data-grounded question-answering platform",
    version="0.1.0",
)

# Get settings
settings = get_settings()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url, "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(health.router)


@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    print("🚀 DataBound AI Backend Starting...")
    print(f"Environment: {settings.environment}")
    print(f"Database: {settings.database_url}")
    print(f"LLM Provider: {settings.llm_provider}")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    print("👋 DataBound AI Backend Shutting Down...")
