from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Database
    database_url: str = "postgresql://databound:databound@localhost:5432/databound_db"

    # LLM Configuration
    llm_api_key: str = ""
    llm_provider: str = "openai"
    llm_model: str = "gpt-4"

    # Embedding Configuration
    embedding_model: str = "text-embedding-3-small"
    embedding_provider: str = "openai"

    # RAG Configuration
    top_k: int = 5
    similarity_threshold: float = 0.5

    # File Upload
    max_file_size: int = 52428800  # 50MB

    # JWT
    jwt_secret: str = "your-secret-key-change-this-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24

    # API URLs
    backend_url: str = "http://localhost:8000"
    backend_port: int = 8000
    frontend_url: str = "http://localhost:5173"
    frontend_port: int = 5173

    # Environment
    environment: str = "development"

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
