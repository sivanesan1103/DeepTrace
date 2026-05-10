import os
import json
import redis.asyncio as redis
import structlog

logger = structlog.get_logger()

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379")

redis_client = redis.from_url(REDIS_URL, decode_responses=True)


async def cache_embedding(key: str, embedding: list[float], ttl: int = 3600):
    await redis_client.setex(f"embedding:{key}", ttl, json.dumps(embedding))


async def get_cached_embedding(key: str) -> list[float] | None:
    data = await redis_client.get(f"embedding:{key}")
    return json.loads(data) if data else None


async def cache_investigation_data(investigation_id: str, data: dict, ttl: int = 86400):
    await redis_client.setex(f"investigation:{investigation_id}", ttl, json.dumps(data))


async def get_cached_investigation(investigation_id: str) -> dict | None:
    data = await redis_client.get(f"investigation:{investigation_id}")
    return json.loads(data) if data else None