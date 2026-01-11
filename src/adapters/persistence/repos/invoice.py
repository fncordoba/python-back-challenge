from typing import Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete as sqlalchemy_delete
from sqlalchemy.orm import selectinload

from src.application.ports.repositories import InvoiceRepository
from src.domain.entities import Invoice, Payment
from src.domain.value_objects import Money
from src.adapters.persistence.models_business import InvoiceModel, PaymentModel

class SQLAlchemyInvoiceRepository(InvoiceRepository):
    def __init__(self, session: AsyncSession):
        self.session = session
        
    async def save(self, invoice: Invoice) -> None:
        existing = await self.session.get(InvoiceModel, invoice.id)
        if existing:
             existing.status = invoice.status
             
             current_payment_ids = {p.id for p in existing.payments}
             for p in invoice.payments:
                 if p.id not in current_payment_ids:
                     pm = PaymentModel(
                         id=p.id, invoice_id=invoice.id, amount=p.amount.amount, 
                         currency=p.amount.currency, paid_at=p.paid_at
                     )
                     self.session.add(pm)
        else:
            model = InvoiceModel(
                id=invoice.id,
                student_id=invoice.student_id,
                school_id=invoice.school_id,
                amount_total=invoice.amount.amount,
                currency=invoice.amount.currency,
                due_date=invoice.due_date,
                issued_at=invoice.issued_at,
                status=invoice.status
            )
            self.session.add(model)
            for p in invoice.payments:
                 pm = PaymentModel(
                     id=p.id, invoice_id=invoice.id, amount=p.amount.amount, 
                     currency=p.amount.currency, paid_at=p.paid_at
                 )
                 self.session.add(pm)

    async def get_by_id(self, invoice_id: UUID) -> Optional[Invoice]:
        query = select(InvoiceModel).where(InvoiceModel.id == invoice_id).execution_options(populate_existing=True)
        query = query.options(selectinload(InvoiceModel.payments))
        
        result = await self.session.execute(query)
        model = result.scalar_one_or_none()
        
        if not model:
            return None
            
        payments = [
            Payment(
                id=p.id, invoice_id=p.invoice_id, 
                amount=Money(p.amount, p.currency), paid_at=p.paid_at
            ) for p in model.payments
        ]
        
        return Invoice(
            id=model.id,
            student_id=model.student_id,
            school_id=model.school_id,
            amount=Money(model.amount_total, model.currency),
            due_date=model.due_date,
            status=model.status,
            issued_at=model.issued_at,
            payments=payments
        )

    async def delete(self, invoice_id: UUID) -> None:
        await self.session.execute(
            sqlalchemy_delete(InvoiceModel).where(InvoiceModel.id == invoice_id)
        )

    async def list(self, limit: int, offset: int, student_id: Optional[UUID] = None) -> tuple[List[Invoice], int]:
        query = select(InvoiceModel)
        count_query = select(func.count()).select_from(InvoiceModel)
        
        if student_id:
            query = query.where(InvoiceModel.student_id == student_id)
            count_query = count_query.where(InvoiceModel.student_id == student_id)
            
        count_res = await self.session.execute(count_query)
        total = count_res.scalar_one()
        
        query = query.options(selectinload(InvoiceModel.payments)).limit(limit).offset(offset).order_by(InvoiceModel.issued_at.desc())
        
        result = await self.session.execute(query)
        models = result.scalars().all()
        
        items = []
        for model in models:
             payments = [
                Payment(
                    id=p.id, invoice_id=p.invoice_id, 
                    amount=Money(p.amount, p.currency), paid_at=p.paid_at
                ) for p in model.payments
            ]
             items.append(Invoice(
                id=model.id,
                student_id=model.student_id,
                school_id=model.school_id,
                amount=Money(model.amount_total, model.currency),
                due_date=model.due_date,
                status=model.status,
                issued_at=model.issued_at,
                payments=payments
            ))
            
        return items, total
