from abc import ABC, abstractmethod
from typing import Optional
from src.domain.auth import User

class AuthRepository(ABC):
    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]: ...
    
    @abstractmethod
    async def save(self, user: User) -> None: ...
