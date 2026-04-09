# FinTrack Backend

## Local development

1. Create `backend/.env` from `backend/.env.example`.
2. Start infrastructure and API:

```bash
docker compose up --build
```

3. Open:
- API docs: `http://localhost:8000/docs`
- MailHog: `http://localhost:8025`

## Health endpoints

- `GET /health/live`
- `GET /health/ready`

## Test suite

```bash
poetry install
poetry run pytest tests -q
```

## Live smoke test against docker-compose

```bash
$env:FINTRACK_LIVE_BASE_URL="http://127.0.0.1:8000"
poetry run pytest tests/test_live_smoke.py -q
```

Optional MailHog override:

```bash
$env:FINTRACK_MAILHOG_API_URL="http://127.0.0.1:8025/api/v2/messages"
```

## Notes

- Container startup runs `alembic upgrade head` before launching the API.
- New migrations must be created manually. The container no longer auto-generates migrations on startup.
