#!/bin/bash
set -e

echo "Running Alembic migrations..."
cd /app
uv run alembic upgrade head

echo "Starting FastAPI with Uvicorn..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
