from abc import ABC, abstractmethod
from typing import Optional

class CacheService(ABC):
    @abstractmethod
    async def get(self, key: str) -> Optional[str]:
        """Retrieve a value by key."""
        ...

    @abstractmethod
    async def set(self, key: str, value: str, ttl_seconds: int) -> None:
        """Set a value with TTL."""
        ...

    @abstractmethod
    async def increment_version(self, key_prefix: str) -> None:
        """Increment version counter for invalidation implementation."""
        ...
        
    @abstractmethod
    async def get_version(self, key_prefix: str) -> int:
        """Get current version for key prefix."""
        ...
