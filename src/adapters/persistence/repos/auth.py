from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.application.ports.auth_repository import AuthRepository
from src.domain.auth import User, UserRole
from src.adapters.persistence.models_auth import UserModel

class SQLAlchemyAuthRepository(AuthRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_email(self, email: str) -> Optional[User]:
        query = select(UserModel).where(UserModel.email == email)
        result = await self.session.execute(query)
        model = result.scalar_one_or_none()
        
        if not model:
            return None
            
        return User(
            id=model.id,
            email=model.email,
            password_hash=model.password_hash,
            role=model.role,
            school_id=model.school_id,
            student_id=model.student_id,
            created_at=model.created_at
        )

    async def save(self, user: User) -> None:
        model = UserModel(
            id=user.id,
            email=user.email,
            password_hash=user.password_hash,
            role=user.role,
            school_id=user.school_id,
            student_id=user.student_id,
            created_at=user.created_at
        )
        self.session.add(model)
