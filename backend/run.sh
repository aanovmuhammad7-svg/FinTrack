#!/bin/sh
set -e

echo "Waiting for DB..."

while ! nc -z db 5432; do
  sleep 1
done

echo "DB is up"

alembic revision --autogenerate -m "add migrations"

alembic upgrade head