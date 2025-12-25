import asyncpg # type: ignore
from fastapi import FastAPI
from loguru import logger

from app.core.settings.app import AppSettings


async def connect_to_db(app: FastAPI, settings: AppSettings) -> None:
    logger.info("Connecting to PostgreSQL...")
    dsn = str(settings.database_url)
    if "+asyncpg" in dsn:
        dsn = dsn.replace("+asyncpg", "")

    app.state.pool = await asyncpg.create_pool( # type: ignore
        dsn,
        min_size=settings.min_connection_count,
        max_size=settings.max_connection_count,
    )
    logger.info("Connection completed")


async def close_db_connection(app: FastAPI) -> None:
    logger.info("Closing connection to database")

    await app.state.pool.close()

    logger.info("Connection closed")