from fastapi import FastAPI
from loguru import logger
from sqlalchemy import text

from app.core.settings.app import AppSettings
from app.db.database import engine


async def connect_to_database(app: FastAPI, settings: AppSettings) -> None:
    logger.info("Connecting to PostgreSQL...")
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        logger.info("Connection completed✅")
    except Exception as e:
        logger.exception(f"Error connecting to database: {e}")


async def close_database_connection(app: FastAPI) -> None:
    logger.info("Closing connection to database")
    try:
        await engine.dispose()
        logger.info("Database connection closed✅")
    except Exception as e:
        logger.exception(f"Error closing database connection: {e}")