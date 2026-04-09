from fastapi import APIRouter, HTTPException, Request, status
from sqlalchemy import text

from app.db.database import engine


router = APIRouter(prefix="/health", tags=["Health"])


@router.get("/live", status_code=status.HTTP_200_OK, summary="Liveness probe")
async def liveness() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/ready", status_code=status.HTTP_200_OK, summary="Readiness probe")
async def readiness(request: Request) -> dict[str, object]:
    checks: dict[str, str] = {}

    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        checks["database"] = "ok"
    except Exception:
        checks["database"] = "error"

    redis = getattr(request.app.state, "redis", None)
    try:
        if redis is None:
            raise RuntimeError("Redis client is not initialized")
        await redis.ping()
        checks["redis"] = "ok"
    except Exception:
        checks["redis"] = "error"

    if any(value != "ok" for value in checks.values()):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "status": "error",
                "checks": checks,
            },
        )

    return {"status": "ok", "checks": checks}
