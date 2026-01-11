from typing import Optional
from uuid import UUID
from decimal import Decimal
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from src.application.ports.repositories import StatementRepository
from src.application.dtos import AccountStatementDTO, InvoiceDTO
from src.adapters.persistence.models_business import InvoiceModel, PaymentModel, StudentModel, SchoolModel

class SQLAlchemyStatementRepository(StatementRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_student_statement(self, student_id: UUID) -> Optional[AccountStatementDTO]:
        # Check student exists
        student_res = await self.session.execute(select(StudentModel).where(StudentModel.id == student_id))
        if not student_res.scalar_one_or_none():
            return None
            
        # Select explicit columns
        stmt = (
            select(
                InvoiceModel.id,
                InvoiceModel.amount_total,
                InvoiceModel.currency,
                InvoiceModel.status,
                InvoiceModel.issued_at,
                InvoiceModel.due_date,
                func.coalesce(func.sum(PaymentModel.amount), 0).label("paid_amount")
            )
            .outerjoin(PaymentModel, InvoiceModel.id == PaymentModel.invoice_id)
            .where(InvoiceModel.student_id == student_id)
            .group_by(
                InvoiceModel.id, 
                InvoiceModel.amount_total, 
                InvoiceModel.currency, 
                InvoiceModel.status, 
                InvoiceModel.issued_at, 
                InvoiceModel.due_date
            )
        )
        
        result = await self.session.execute(stmt)
        rows = result.all()
        
        invoices_dto = []
        total_due = Decimal(0)
        
        stmt_currency = "MIXED"
        if rows:
            stmt_currency = rows[0].currency.value

        for row in rows:
            amount_total = row.amount_total
            paid = row.paid_amount
            due = amount_total - paid
            
            total_due += due
            
            invoices_dto.append(InvoiceDTO(
                id=row.id,
                amount_total=amount_total,
                amount_paid=paid,
                amount_due=due,
                currency=row.currency,
                status=row.status,
                issued_at=row.issued_at,
                due_date=row.due_date
            ))
            
        return AccountStatementDTO(
            entity_id=student_id,
            generated_at=datetime.utcnow(),
            invoices=invoices_dto,
            total_due=total_due,
            currency=stmt_currency
        )

    async def get_school_statement(self, school_id: UUID) -> Optional[AccountStatementDTO]:
        school_res = await self.session.execute(select(SchoolModel).where(SchoolModel.id == school_id))
        if not school_res.scalar_one_or_none():
             return None

        stmt = (
            select(
                InvoiceModel.id,
                InvoiceModel.amount_total,
                InvoiceModel.currency,
                InvoiceModel.status,
                InvoiceModel.issued_at,
                InvoiceModel.due_date,
                func.coalesce(func.sum(PaymentModel.amount), 0).label("paid_amount")
            )
            .outerjoin(PaymentModel, InvoiceModel.id == PaymentModel.invoice_id)
            .where(InvoiceModel.school_id == school_id)
            .group_by(
                InvoiceModel.id, 
                InvoiceModel.amount_total, 
                InvoiceModel.currency, 
                InvoiceModel.status, 
                InvoiceModel.issued_at, 
                InvoiceModel.due_date
            )
        )
        
        result = await self.session.execute(stmt)
        rows = result.all()
        
        invoices_dto = []
        total_due = Decimal(0)
        
        stmt_currency = "MIXED"
        if rows:
            stmt_currency = rows[0].currency.value

        for row in rows:
            amount_total = row.amount_total
            paid = row.paid_amount
            due = amount_total - paid
            
            total_due += due
            
            invoices_dto.append(InvoiceDTO(
                id=row.id,
                amount_total=amount_total,
                amount_paid=paid,
                amount_due=due,
                currency=row.currency,
                status=row.status,
                issued_at=row.issued_at,
                due_date=row.due_date
            ))
            
        return AccountStatementDTO(
             entity_id=school_id,
             generated_at=datetime.utcnow(),
             invoices=invoices_dto,
             total_due=total_due,
             currency=stmt_currency
        )
