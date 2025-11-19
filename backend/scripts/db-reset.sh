#!/usr/bin/env bash
set -e

# -------------------------------------------------------------
# Database Reset Script for ArcoirisPOS
# -------------------------------------------------------------
# This script:
#  1. Stops the postgres container
#  2. Removes the container
#  3. Deletes the postgres volume (full wipe)
#  4. Restarts postgres
#  5. Waits for healthcheck to pass
#  6. Runs Alembic migrations from scratch
# -------------------------------------------------------------

CONTAINER_NAME="arcoirispos_postgres"
VOLUME_NAME="arcoirispos_postgres_data"
SERVICE_NAME="postgres"

echo "---------------------------------------------------------"
echo "🧨  WARNING: FULL DATABASE RESET (DESTRUCTIVE OPERATION)"
echo "---------------------------------------------------------"
echo "This will ERASE the entire database and volume:"
echo "  - Container: $CONTAINER_NAME"
echo "  - Volume:    $VOLUME_NAME"
echo
read -p "Type YES to continue: " confirm
if [[ "$confirm" != "YES" ]]; then
    echo "❌ Cancelled."
    exit 1
fi

echo
echo "🛑 Stopping docker container..."
docker stop "$CONTAINER_NAME" >/dev/null 2>&1 || true

echo "🗑️ Removing docker container..."
docker rm "$CONTAINER_NAME" >/dev/null 2>&1 || true

echo "💥 Removing docker volume..."
docker volume rm "$VOLUME_NAME" || true

echo "🚀 Starting fresh postgres instance..."
docker-compose up -d "$SERVICE_NAME"

echo "⏳ Waiting for postgres healthcheck..."
# Poll until container is healthy
while true; do
    STATUS=$(docker inspect --format='{{json .State.Health.Status}}' "$CONTAINER_NAME" 2>/dev/null || echo "null")
    if [[ "$STATUS" == "\"healthy\"" ]]; then
        echo "✅ Postgres is healthy!"
        break
    fi
    echo "   ... still waiting ..."
    sleep 2
done

echo
echo "📦 Running Alembic migrations..."
cd backend
alembic upgrade head

echo
echo "---------------------------------------------------------"
echo "🎉 Database successfully reset and fully migrated!"
echo "---------------------------------------------------------"
