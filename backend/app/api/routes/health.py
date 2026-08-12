from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.config import get_settings

router = APIRouter(prefix="/api", tags=["health"])


@router.get("/health")
async def health_check():
    """Basic health check endpoint"""
    return {"status": "ok", "service": "databound-ai-backend"}


@router.get("/health/db")
async def health_check_db(db: Session = Depends(get_db)):
    """Health check with database connection"""
    try:
        # Simple query to verify database connection
        db.execute("SELECT 1")
        return {
            "status": "ok",
            "service": "databound-ai-backend",
            "database": "connected",
        }
    except Exception as e:
        return {
            "status": "error",
            "service": "databound-ai-backend",
            "database": "disconnected",
            "error": str(e),
        }


@router.get("/config")
async def get_config():
    """Get public configuration"""
    settings = get_settings()
    return {
        "llm_provider": settings.llm_provider,
        "llm_model": settings.llm_model,
        "embedding_model": settings.embedding_model,
        "environment": settings.environment,
    }
