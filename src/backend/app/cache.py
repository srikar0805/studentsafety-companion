from __future__ import annotations

import json
import time
from dataclasses import dataclass
from typing import Any

from .config import settings


class Cache:
    def get(self, key: str) -> Any | None:
        raise NotImplementedError

    def set(self, key: str, value: Any, ttl_seconds: int) -> None:
        raise NotImplementedError


@dataclass
class _MemoryEntry:
    value: Any
    expires_at: float


class MemoryCache(Cache):
    def __init__(self) -> None:
        self._store: dict[str, _MemoryEntry] = {}

    def get(self, key: str) -> Any | None:
        entry = self._store.get(key)
        if entry is None:
            return None
        if entry.expires_at <= time.time():
            self._store.pop(key, None)
            return None
        return entry.value

    def set(self, key: str, value: Any, ttl_seconds: int) -> None:
        self._store[key] = _MemoryEntry(
            value=value,
            expires_at=time.time() + ttl_seconds,
        )


class RedisCache(Cache):
    def __init__(self, redis_client) -> None:
        self._redis = redis_client

    def get(self, key: str) -> Any | None:
        raw = self._redis.get(key)
        if raw is None:
            return None
        return json.loads(raw)

    def set(self, key: str, value: Any, ttl_seconds: int) -> None:
        self._redis.setex(key, ttl_seconds, json.dumps(value))


def get_cache() -> Cache:
    if not settings.redis_url:
        return MemoryCache()

    try:
        import redis

        client = redis.from_url(settings.redis_url, decode_responses=True)
        client.ping()
        return RedisCache(client)
    except Exception:
        return MemoryCache()
