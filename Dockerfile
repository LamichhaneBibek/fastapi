FROM python:3.13-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install uv
RUN pip install --no-cache-dir uv==0.4.30

WORKDIR /app

# Copy dependency files first (better layer caching)
COPY pyproject.toml uv.lock ./
RUN uv sync --no-dev --frozen

# Copy the rest of the code
COPY . .

# Ensure script is executable
RUN chmod +x start_service.sh

EXPOSE 8000

ENTRYPOINT ["./start_service.sh"]
