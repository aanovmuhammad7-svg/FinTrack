from fastapi import FastAPI
from loguru import logger
from app.db.redis import redis_client

async def connect_to_redis(app: FastAPI):
    logger.info("Connecting to Redis...")
    try:
        await redis_client.ping()# type: ignore
        app.state.redis = redis_client
        logger.info("Redis connected✅")
    except Exception as e:
        logger.exception(f"Error connecting to Redis: {e}")
        raise

async def close_redis_connection(app: FastAPI):
    logger.info("Closing Redis connection...")
    redis = app.state.redis
    try:
        await redis.aclose()
        logger.info("Redis connection closed✅")
    except Exception as e:
        logger.exception(f"Error closing Redis connection: {e}")
