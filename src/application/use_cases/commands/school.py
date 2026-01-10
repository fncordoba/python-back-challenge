from uuid import UUID
from src.application.dtos import (
    CreateSchoolCommand, UpdateSchoolCommand, SchoolDTO
)
from src.domain.entities import School
from src.domain.exceptions import EntityNotFound

class SchoolCommandsMixin:
    async def create_school(self, cmd: CreateSchoolCommand) -> SchoolDTO:
        school = School.create(name=cmd.name)
        await self.school_repo.save(school)
        await self.uow.commit()
        return SchoolDTO(id=school.id, name=school.name, created_at=school.created_at)

    async def update_school(self, cmd: UpdateSchoolCommand) -> SchoolDTO:
        school = await self.school_repo.get_by_id(cmd.school_id)
        if not school:
             raise EntityNotFound(f"School {cmd.school_id} not found")
        
        school.name = cmd.name
        await self.school_repo.save(school)
        await self.uow.commit()
        return SchoolDTO(id=school.id, name=school.name, created_at=school.created_at)

    async def delete_school(self, school_id: UUID) -> None:
        school = await self.school_repo.get_by_id(school_id)
        if not school:
             raise EntityNotFound(f"School {school_id} not found")
        
        await self.school_repo.delete(school_id)
        await self.uow.commit()
        await self.cache.increment_version(f"school:{school_id}")
