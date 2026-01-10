from typing import Optional
import redis.asyncio as redis
from redis.exceptions import RedisError

from src.application.ports.cache import CacheService
from src.adapters.resilience.circuit_breaker import CircuitBreaker, CircuitBreakerOpenException

class RedisCacheAdapter(CacheService):
    def __init__(self, redis_url: str):
        self.redis = redis.from_url(redis_url, encoding="utf-8", decode_responses=True)
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=3,
            recovery_timeout=30,
            expected_exceptions=(RedisError, ConnectionError, TimeoutError)
        )

    async def get(self, key: str) -> Optional[str]:
        try:
            return await self.circuit_breaker.call(self.redis.get, key)
        except (CircuitBreakerOpenException, RedisError):
            # Fallback (handled by domain: return None -> treat as miss)
            return None

    async def set(self, key: str, value: str, ttl_seconds: int) -> None:
        try:
            await self.circuit_breaker.call(self.redis.set, key, value, ex=ttl_seconds)
        except (CircuitBreakerOpenException, RedisError):
            # Fire and forget failure
            pass

    async def increment_version(self, key_prefix: str) -> None:
        try:
            version_key = f"{key_prefix}:version"
            await self.circuit_breaker.call(self.redis.incr, version_key)
        except (CircuitBreakerOpenException, RedisError):
            pass

    async def get_version(self, key_prefix: str) -> int:
        try:
            version_key = f"{key_prefix}:version"
            val = await self.circuit_breaker.call(self.redis.get, version_key)
            return int(val) if val else 0
        except (CircuitBreakerOpenException, RedisError, ValueError):
            return 0
