from typing import Optional
from uuid import UUID
import json
from src.application.dtos import (
    PaginationParams, PaginatedResponse, SchoolDTO, AccountStatementDTO
)
from src.domain.exceptions import EntityNotFound

class SchoolQueriesMixin:
    async def list_schools(self, params: PaginationParams) -> PaginatedResponse[SchoolDTO]:
        items, total = await self.school_repo.list(limit=params.limit, offset=params.offset)
        dtos = [SchoolDTO(id=i.id, name=i.name, created_at=i.created_at) for i in items]
        return PaginatedResponse(items=dtos, total=total, limit=params.limit, offset=params.offset)

    async def get_school_account_statement(self, school_id: UUID) -> AccountStatementDTO:
        version = await self.cache.get_version(f"school:{school_id}")
        cache_key = f"school:{school_id}:statement:v{version}"
        
        cached_data = await self.cache.get(cache_key)
        if cached_data:
            try:
                data_dict = json.loads(cached_data)
                return AccountStatementDTO(**data_dict)
            except Exception:
                pass

        statement = await self.statement_repo.get_school_statement(school_id)
        if not statement:
             raise EntityNotFound(f"School {school_id} not found or no statement available")

        await self.cache.set(cache_key, statement.model_dump_json(), ttl_seconds=60)
        return statement
