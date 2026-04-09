#!/bin/sh
set -e

./run.sh

exec uvicorn app.main:app --host 0.0.0.0 --port 8000
