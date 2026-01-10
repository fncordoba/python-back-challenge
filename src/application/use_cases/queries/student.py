from typing import Optional
from uuid import UUID
import json
from src.application.dtos import (
    PaginationParams, PaginatedResponse, StudentDTO, AccountStatementDTO
)
from src.domain.exceptions import EntityNotFound

class StudentQueriesMixin:
    async def list_students(self, params: PaginationParams, school_id: Optional[UUID] = None) -> PaginatedResponse[StudentDTO]:
        items, total = await self.student_repo.list(limit=params.limit, offset=params.offset, school_id=school_id)
        dtos = [StudentDTO(id=i.id, school_id=i.school_id, name=i.name, created_at=i.created_at) for i in items]
        return PaginatedResponse(items=dtos, total=total, limit=params.limit, offset=params.offset)

    async def get_student_account_statement(self, student_id: UUID) -> AccountStatementDTO:
        version = await self.cache.get_version(f"student:{student_id}")
        cache_key = f"student:{student_id}:statement:v{version}"
        
        cached_data = await self.cache.get(cache_key)
        if cached_data:
            try:
                data_dict = json.loads(cached_data)
                return AccountStatementDTO(**data_dict)
            except Exception:
                pass

        statement = await self.statement_repo.get_student_statement(student_id)
        if not statement:
            raise EntityNotFound(f"Student {student_id} not found or no statement available")

        await self.cache.set(cache_key, statement.model_dump_json(), ttl_seconds=60)
        
        return statement
