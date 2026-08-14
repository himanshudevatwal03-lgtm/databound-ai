# --- DataBound AI backend image ---
FROM python:3.11-slim

# Prevents Python from writing .pyc files and buffers stdout, which makes
# `docker compose logs` show output immediately instead of batching it.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# System packages needed to build psycopg2 and (later) PDF libraries.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# Shell form (not exec-array form) so $PORT is actually expanded. Render
# (and most PaaS hosts) assign a dynamic port via the PORT env var; we
# default to 8000 for local `docker run` where PORT isn't set.
# No --reload here — that's a dev-only flag, overridden locally via
# docker-compose.yml's `command:` override instead.
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
