"""
config.py

Centralized application configuration.

Why this file exists:
FastAPI apps need settings (database URL, secrets, model names, etc.) that
change between environments (local dev, Docker, production). Hard-coding
these values is a security risk and makes the app inflexible. Instead, we
read everything from environment variables using Pydantic's BaseSettings,
which gives us:
  - automatic type validation (e.g. TOP_K must be an int)
  - a single source of truth for configuration
  - sensible defaults for local development

Every other part of the backend imports `settings` from this file instead
of calling os.environ directly.
"""

from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

    # --- App metadata ---
    APP_NAME: str = "DataBound AI"
    APP_ENV: str = Field(default="development")
    API_V1_PREFIX: str = "/api"

    # --- Database ---
    DATABASE_URL: str = Field(
        default="postgresql://databound:databound@localhost:5432/databound",
        description="SQLAlchemy-compatible PostgreSQL connection string",
    )

    # --- Security / Auth (used starting Phase 2, defined now so .env is stable) ---
    JWT_SECRET: str = Field(default="change-this-secret-in-production")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    # --- AI / LLM provider abstraction (used starting Phase 5) ---
    LLM_API_KEY: str = Field(default="")
    LLM_MODEL: str = Field(default="claude-sonnet-4-6")
    EMBEDDING_MODEL: str = Field(default="text-embedding-3-small")

    # --- Embeddings (Phase 4) ---
    # "local": a dependency-free, deterministic hashing-based embedding —
    #   works immediately with no API key or cost, at the price of being
    #   lexical (word-overlap) rather than truly semantic. See
    #   app/services/embeddings.py for the full tradeoff explanation.
    # "openai": real semantic embeddings via OpenAI's API. Requires
    #   LLM_API_KEY to be set to an OpenAI key.
    EMBEDDING_PROVIDER: str = Field(default="local")
    # Fixed at table-creation time (see app/models/document_chunk.py) —
    # changing this after documents have already been indexed requires
    # re-indexing everything, since existing vectors would have the old
    # dimensionality. Tracked as a limitation for now (no migrations yet).
    EMBEDDING_DIMENSIONS: int = 384

    # --- Chunking (Phase 4) ---
    CHUNK_SIZE: int = 800  # target characters per chunk
    CHUNK_OVERLAP: int = 100  # characters of overlap between consecutive chunks

    # --- Retrieval tuning (used starting Phase 4/5) ---
    TOP_K: int = 5
    # Calibrated empirically against the LOCAL embedding provider (see
    # app/services/embeddings.py), where genuinely relevant matches
    # typically score ~0.4-0.75 and clearly unrelated text scores ~0.2.
    # A threshold here only screens out obviously-irrelevant chunks
    # (Anti-Hallucination Layer 1) — it can't distinguish "same topic" from
    # "actually answers the question" (e.g. a chunk about Rahul's CGPA
    # scores similarly whether asked about his CGPA or his father's name).
    # That's why Layer 2 (the strict grounded prompt) and Phase 6's Layer 3
    # (post-hoc answer validation) both matter — retrieval alone isn't
    # enough. If you switch to EMBEDDING_PROVIDER=openai, raise this back
    # toward 0.6-0.75; real semantic embeddings separate relevant from
    # irrelevant content more sharply than this lexical fallback does.
    SIMILARITY_THRESHOLD: float = 0.3

    # --- File handling ---
    MAX_FILE_SIZE: int = 20 * 1024 * 1024  # 20 MB
    # Stored as a plain comma-separated string (not List[str]): pydantic-
    # settings tries to JSON-decode List[...] fields read from env vars
    # before any custom validator gets a chance to run, which breaks on
    # a plain comma-separated value like Render's env var UI encourages.
    # Use the .allowed_file_extensions_list property below instead of this
    # field directly.
    ALLOWED_FILE_EXTENSIONS: str = ".txt,.pdf,.csv"

    # --- CORS ---
    # Same reasoning as above — plain comma-separated string, e.g.:
    #   http://localhost:5173,https://databound-frontend.onrender.com
    # Use .cors_origins_list below instead of this field directly.
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    @property
    def allowed_file_extensions_list(self) -> List[str]:
        return [ext.strip() for ext in self.ALLOWED_FILE_EXTENSIONS.split(",") if ext.strip()]


@lru_cache
def get_settings() -> Settings:
    """
    Returns a cached Settings instance.

    lru_cache ensures we parse environment variables only once per process,
    rather than re-reading and re-validating them on every request.
    """
    return Settings()


settings = get_settings()
