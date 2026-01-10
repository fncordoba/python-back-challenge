from dataclasses import dataclass, field
from datetime import datetime, date
from uuid import UUID, uuid4
from typing import List, Optional
from decimal import Decimal

from src.domain.enums import InvoiceStatus, Currency
from src.domain.value_objects import Money
from src.domain.exceptions import PaymentExceedsDueAmount, InvalidInvoiceStateTransition

@dataclass
class School:
    id: UUID
    name: str
    created_at: datetime = field(default_factory=datetime.utcnow)

    @classmethod
    def create(cls, name: str) -> 'School':
        return cls(id=uuid4(), name=name)

@dataclass
class Student:
    id: UUID
    school_id: UUID
    name: str
    created_at: datetime = field(default_factory=datetime.utcnow)

    @classmethod
    def create(cls, name: str, school_id: UUID) -> 'Student':
        return cls(id=uuid4(), school_id=school_id, name=name)

@dataclass
class Payment:
    id: UUID
    invoice_id: UUID
    amount: Money
    paid_at: datetime = field(default_factory=datetime.utcnow)

    @classmethod
    def create(cls, invoice_id: UUID, amount: Money) -> 'Payment':
        return cls(id=uuid4(), invoice_id=invoice_id, amount=amount)

@dataclass
class Invoice:
    id: UUID
    student_id: UUID
    school_id: UUID
    amount: Money
    due_date: date
    status: InvoiceStatus
    issued_at: datetime = field(default_factory=datetime.utcnow)
    payments: List[Payment] = field(default_factory=list)

    @property
    def amount_paid(self) -> Money:
        total = Decimal('0.00')
        for p in self.payments:
            total += p.amount.amount
        return Money(amount=total, currency=self.amount.currency)

    @property
    def amount_due(self) -> Money:
        return self.amount - self.amount_paid
    
    def is_overdue(self) -> bool:
        # Simplified: Check this at Query/Read time or via Domain Service usually.
        # But entity logic can hold invariant checks.
        today = date.today()
        return self.status != InvoiceStatus.PAID and self.due_date < today

    @classmethod
    def create(cls, student_id: UUID, school_id: UUID, amount: Money, due_date: date) -> 'Invoice':
        return cls(
            id=uuid4(),
            student_id=student_id,
            school_id=school_id,
            amount=amount,
            due_date=due_date,
            status=InvoiceStatus.PENDING
        )

    def register_payment(self, amount: Money) -> Payment:
        if amount.currency != self.amount.currency:
            raise ValueError("Payment currency must match invoice currency")
        
        current_due = self.amount_due
        if amount.amount > current_due.amount:
            raise PaymentExceedsDueAmount(f"Payment amount {amount.amount} exceeds due amount {current_due.amount}")

        payment = Payment.create(invoice_id=self.id, amount=amount)
        self.payments.append(payment)
        
        self._update_status()
        return payment

    def _update_status(self):
        paid = self.amount_paid
        if paid.amount >= self.amount.amount:
            self.status = InvoiceStatus.PAID
        elif paid.amount > 0:
            self.status = InvoiceStatus.PARTIALLY_PAID
        else:
            self.status = InvoiceStatus.PENDING
