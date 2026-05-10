import hashlib
import json
from typing import Any

from .redis_client import cache_embedding, get_cached_embedding


def generate_embedding_key(data: Any) -> str:
    return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()[:16]


async def get_or_cache_embedding(data: dict | list) -> list[float]:
    key = generate_embedding_key(data)
    cached = await get_cached_embedding(key)
    if cached:
        return cached

    embedding = [0.0] * 768
    await cache_embedding(key, embedding)
    return embedding