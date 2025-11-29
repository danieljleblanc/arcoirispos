FROM python:3.12-slim AS base

# Install system dependencies for bcrypt, psycopg, SQLAlchemy async
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    gcc \
    libffi-dev \
    python3-dev \
    cargo \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy Python dependencies
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source code
COPY src ./src

# Copy Alembic configuration + migrations
COPY alembic.ini /app/alembic.ini
COPY src/app/infrastructure/migrations /app/src/app/infrastructure/migrations

# Expose FastAPI port
EXPOSE 8000

# Default command (docker-compose may override in dev)
CMD ["uvicorn", "src.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
