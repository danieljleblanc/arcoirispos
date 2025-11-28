FROM python:3.12-slim AS base

# Install system dependencies needed for bcrypt, psycopg, etc.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    gcc \
    libffi-dev \
    python3-dev \
    cargo \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy dependency file
COPY requirements.txt .

# Install Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire backend source code
COPY src ./src

# 🔥 ADD THIS LINE — VERY IMPORTANT
COPY .env .env

EXPOSE 8000

# Final CMD (only ONE allowed)
# Note: docker-compose.yml overrides this, but keeping correct path for reference
CMD ["bash", "-c", "uvicorn src.app.main:app --host 0.0.0.0 --port 8000 --reload"]
