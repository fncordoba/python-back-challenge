from typing import Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete as sqlalchemy_delete

from src.application.ports.repositories import StudentRepository
from src.domain.entities import Student
from src.adapters.persistence.models import StudentModel

class SQLAlchemyStudentRepository(StudentRepository):
    def __init__(self, session: AsyncSession):
        self.session = session
        
    async def save(self, student: Student) -> None:
        existing = await self.session.get(StudentModel, student.id)
        if existing:
            existing.name = student.name
            existing.school_id = student.school_id
        else:
            model = StudentModel(
                id=student.id,
                school_id=student.school_id,
                name=student.name,
                created_at=student.created_at
            )
            self.session.add(model)
        
    async def get_by_id(self, student_id: UUID) -> Optional[Student]:
        result = await self.session.execute(select(StudentModel).where(StudentModel.id == student_id))
        model = result.scalar_one_or_none()
        if not model:
            return None
        return Student(id=model.id, school_id=model.school_id, name=model.name, created_at=model.created_at)

    async def get_by_school(self, school_id: UUID) -> List[Student]:
        # Existing method
        result = await self.session.execute(select(StudentModel).where(StudentModel.school_id == school_id))
        models = result.scalars().all()
        return [Student(id=m.id, school_id=m.school_id, name=m.name, created_at=m.created_at) for m in models]

    async def delete(self, student_id: UUID) -> None:
        await self.session.execute(
             sqlalchemy_delete(StudentModel).where(StudentModel.id == student_id)
        )

    async def list(self, limit: int, offset: int, school_id: Optional[UUID] = None) -> tuple[List[Student], int]:
        query = select(StudentModel)
        count_query = select(func.count()).select_from(StudentModel)
        
        if school_id:
            query = query.where(StudentModel.school_id == school_id)
            count_query = count_query.where(StudentModel.school_id == school_id)
            
        count_res = await self.session.execute(count_query)
        total = count_res.scalar_one()
        
        query = query.limit(limit).offset(offset).order_by(StudentModel.created_at.desc())
        result = await self.session.execute(query)
        models = result.scalars().all()
        
        items = [Student(id=m.id, school_id=m.school_id, name=m.name, created_at=m.created_at) for m in models]
        return items, total
