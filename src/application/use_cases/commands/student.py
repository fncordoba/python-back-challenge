from uuid import UUID
from src.application.dtos import (
    CreateStudentCommand, UpdateStudentCommand, StudentDTO
)
from src.domain.entities import Student
from src.domain.exceptions import EntityNotFound

class StudentCommandsMixin:
    async def create_student(self, cmd: CreateStudentCommand) -> StudentDTO:
        school = await self.school_repo.get_by_id(cmd.school_id)
        if not school:
            raise EntityNotFound(f"School {cmd.school_id} not found")
            
        student = Student.create(name=cmd.name, school_id=cmd.school_id)
        await self.student_repo.save(student)
        await self.uow.commit()
        
        # Invalidate School cache
        await self.cache.increment_version(f"school:{cmd.school_id}")
        
        return StudentDTO(
            id=student.id, school_id=student.school_id, name=student.name, 
            created_at=student.created_at
        )

    async def update_student(self, cmd: UpdateStudentCommand) -> StudentDTO:
        student = await self.student_repo.get_by_id(cmd.student_id)
        if not student:
             raise EntityNotFound(f"Student {cmd.student_id} not found")
        
        student.name = cmd.name
        await self.student_repo.save(student)
        await self.uow.commit()
        return StudentDTO(
            id=student.id, school_id=student.school_id, 
            name=student.name, created_at=student.created_at
        )

    async def delete_student(self, student_id: UUID) -> None:
        student = await self.student_repo.get_by_id(student_id)
        if not student:
            raise EntityNotFound(f"Student {student_id} not found")
        
        await self.student_repo.delete(student_id)
        await self.uow.commit()
        # Invalidate
        await self.cache.increment_version(f"student:{student_id}")
        await self.cache.increment_version(f"school:{student.school_id}")
