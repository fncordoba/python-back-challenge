import pytest
from datetime import date, timedelta, datetime
from decimal import Decimal
from uuid import uuid4

from src.domain.entities import Invoice, Payment
from src.domain.value_objects import Money
from src.domain.enums import Currency, InvoiceStatus
from src.domain.exceptions import PaymentExceedsDueAmount

def test_invoice_creation():
    student_id = uuid4()
    school_id = uuid4()
    amount = Money(Decimal("100.00"), Currency.USD)
    due_date = date.today() + timedelta(days=30)
    
    invoice = Invoice.create(student_id, school_id, amount, due_date)
    
    assert invoice.status == InvoiceStatus.PENDING
    assert invoice.amount_due == amount
    assert invoice.amount_paid.amount == Decimal("0.00")

def test_full_payment():
    student_id = uuid4()
    school_id = uuid4()
    amount = Money(Decimal("100.00"), Currency.USD)
    invoice = Invoice.create(student_id, school_id, amount, date.today())
    
    payment_amount = Money(Decimal("100.00"), Currency.USD)
    invoice.register_payment(payment_amount)
    
    assert invoice.status == InvoiceStatus.PAID
    assert invoice.amount_paid == amount
    assert invoice.amount_due.amount == Decimal("0.00")

def test_partial_payment():
    student_id = uuid4()
    school_id = uuid4()
    amount = Money(Decimal("100.00"), Currency.USD)
    invoice = Invoice.create(student_id, school_id, amount, date.today())
    
    payment_amount = Money(Decimal("40.00"), Currency.USD)
    invoice.register_payment(payment_amount)
    
    assert invoice.status == InvoiceStatus.PARTIALLY_PAID
    assert invoice.amount_paid.amount == Decimal("40.00")
    assert invoice.amount_due.amount == Decimal("60.00")

def test_overpayment_fails():
    student_id = uuid4()
    school_id = uuid4()
    amount = Money(Decimal("100.00"), Currency.USD)
    invoice = Invoice.create(student_id, school_id, amount, date.today())
    
    with pytest.raises(PaymentExceedsDueAmount):
        invoice.register_payment(Money(Decimal("101.00"), Currency.USD))

def test_currency_mismatch():
    student_id = uuid4()
    school_id = uuid4()
    amount = Money(Decimal("100.00"), Currency.USD)
    invoice = Invoice.create(student_id, school_id, amount, date.today())
    
    with pytest.raises(ValueError):
        invoice.register_payment(Money(Decimal("100.00"), Currency.EUR))
