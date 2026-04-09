from fastapi import FastAPI
from fastapi import Request
from starlette.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from time import perf_counter
import uvicorn
from loguru import logger
from slowapi.errors import RateLimitExceeded

from app.api.dependencies.limiter import limiter, rate_limit_exceeded_handler
from app.core.config import settings
from app.core.events import create_start_app_handler, create_stop_app_handler
from app.api.routers.routers import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_start_app_handler(app, settings)()
    try:
        yield
    finally:
        await create_stop_app_handler(app)()

def get_application() -> FastAPI:
    settings.configure_logging()

    application = FastAPI(
        lifespan=lifespan,
        **settings.fastapi_kwargs
    )
    application.state.limiter = limiter
    application.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_hosts,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    application.include_router(api_router)

    @application.middleware("http")
    async def request_logging_middleware(request: Request, call_next):
        start = perf_counter()
        method = request.method
        path = request.url.path
        client = request.client.host if request.client else "-"

        logger.info(f"HTTP request started method={method} path={path} client={client}")
        try:
            response = await call_next(request)
        except Exception:
            duration_ms = (perf_counter() - start) * 1000
            logger.exception(
                f"HTTP request failed method={method} path={path} duration_ms={duration_ms:.2f} client={client}"
            )
            raise

        duration_ms = (perf_counter() - start) * 1000
        logger.info(
            f"HTTP request completed method={method} path={path} status={response.status_code} duration_ms={duration_ms:.2f} client={client}"
        )
        return response

    return application


app = get_application()


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
