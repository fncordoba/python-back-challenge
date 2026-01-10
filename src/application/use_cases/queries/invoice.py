from typing import Optional
from uuid import UUID
from src.application.dtos import (
    PaginationParams, PaginatedResponse, InvoiceDTO
)

class InvoiceQueriesMixin:
    async def list_invoices(self, params: PaginationParams, student_id: Optional[UUID] = None) -> PaginatedResponse[InvoiceDTO]:
        items, total = await self.invoice_repo.list(limit=params.limit, offset=params.offset, student_id=student_id)
        dtos = [
            InvoiceDTO(
                id=i.id,
                amount_total=i.amount.amount,
                amount_paid=i.amount_paid.amount,
                amount_due=i.amount_due.amount,
                currency=i.amount.currency,
                status=i.status,
                issued_at=i.issued_at,
                due_date=i.due_date
            ) for i in items
        ]
        return PaginatedResponse(items=dtos, total=total, limit=params.limit, offset=params.offset)
