from typing import Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete as sqlalchemy_delete

from src.application.ports.repositories import SchoolRepository
from src.domain.entities import School
from src.adapters.persistence.models import SchoolModel

class SQLAlchemySchoolRepository(SchoolRepository):
    def __init__(self, session: AsyncSession):
        self.session = session
        
    async def save(self, school: School) -> None:
        # Check if exists (upsert simplified)
        existing = await self.session.get(SchoolModel, school.id)
        if existing:
            existing.name = school.name
        else:
            model = SchoolModel(
                id=school.id,
                name=school.name,
                created_at=school.created_at
            )
            self.session.add(model)
        
    async def get_by_id(self, school_id: UUID) -> Optional[School]:
        result = await self.session.execute(select(SchoolModel).where(SchoolModel.id == school_id))
        model = result.scalar_one_or_none()
        if not model:
            return None
        return School(id=model.id, name=model.name, created_at=model.created_at)

    async def delete(self, school_id: UUID) -> None:
        await self.session.execute(
            sqlalchemy_delete(SchoolModel).where(SchoolModel.id == school_id)
        )

    async def list(self, limit: int, offset: int) -> tuple[List[School], int]:
        # Count
        count_res = await self.session.execute(select(func.count()).select_from(SchoolModel))
        total = count_res.scalar_one()
        
        # Select
        query = select(SchoolModel).limit(limit).offset(offset).order_by(SchoolModel.created_at.desc())
        result = await self.session.execute(query)
        models = result.scalars().all()
        
        items = [School(id=m.id, name=m.name, created_at=m.created_at) for m in models]
        return items, total
