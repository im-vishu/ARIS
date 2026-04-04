#!/usr/bin/env sh
set -eu

echo "[entrypoint] waiting for postgres..."
until nc -z postgres 5432; do
  sleep 1
done
echo "[entrypoint] postgres is up"

echo "[entrypoint] waiting for redis..."
until nc -z aris-redis 6379; do
  sleep 1
done
echo "[entrypoint] redis is up"

echo "[entrypoint] running migrations..."
alembic upgrade head

echo "[entrypoint] starting api..."
exec uvicorn app.api:app --host 0.0.0.0 --port 8000