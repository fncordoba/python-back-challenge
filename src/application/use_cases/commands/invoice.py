from uuid import UUID
from src.application.dtos import (
    CreateInvoiceCommand, ProcessPaymentCommand, InvoiceDTO
)
from src.domain.entities import Invoice
from src.domain.value_objects import Money
from src.domain.exceptions import EntityNotFound

class InvoiceCommandsMixin:
    async def create_invoice(self, cmd: CreateInvoiceCommand) -> InvoiceDTO:
        student = await self.student_repo.get_by_id(cmd.student_id)
        if not student:
            raise EntityNotFound(f"Student {cmd.student_id} not found")
            
        money = Money(amount=cmd.amount, currency=cmd.currency)
        invoice = Invoice.create(
            student_id=cmd.student_id,
            school_id=student.school_id,
            amount=money,
            due_date=cmd.due_date
        )
        
        await self.invoice_repo.save(invoice)
        await self.uow.commit()
        
        # Invalidate Student and School cache
        await self.cache.increment_version(f"student:{student.id}")
        await self.cache.increment_version(f"school:{student.school_id}")
        
        return InvoiceDTO(
            id=invoice.id,
            amount_total=invoice.amount.amount,
            amount_paid=invoice.amount_paid.amount,
            amount_due=invoice.amount_due.amount,
            currency=invoice.amount.currency,
            status=invoice.status,
            issued_at=invoice.issued_at,
            due_date=invoice.due_date
        )

    async def process_payment(self, cmd: ProcessPaymentCommand) -> UUID:
        invoice = await self.invoice_repo.get_by_id(cmd.invoice_id)
        if not invoice:
            raise EntityNotFound(f"Invoice {cmd.invoice_id} not found")
        
        # Currency check typically happens here or inside domain if we pass Money object
        money = Money(amount=cmd.amount, currency=invoice.amount.currency)
        payment = invoice.register_payment(money)
        
        # Invoice Repo save usually implies saving aggregate including payments
        await self.invoice_repo.save(invoice) 
        await self.uow.commit()
        
        # Invalidate Student and School cache
        await self.cache.increment_version(f"student:{invoice.student_id}")
        await self.cache.increment_version(f"school:{invoice.school_id}")
        
        return payment.id

    async def delete_invoice(self, invoice_id: UUID) -> None:
        invoice = await self.invoice_repo.get_by_id(invoice_id)
        if not invoice:
            raise EntityNotFound(f"Invoice {invoice_id} not found")
            
        await self.invoice_repo.delete(invoice_id)
        await self.uow.commit()
        
        await self.cache.increment_version(f"student:{invoice.student_id}")
        await self.cache.increment_version(f"school:{invoice.school_id}")
