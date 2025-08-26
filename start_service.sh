#!/bin/bash
set -e

echo "Running Alembic migrations..."
cd /app
uv run alembic -c app/alembic.ini upgrade head

echo "Starting FastAPI with Uvicorn..."
exec uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
