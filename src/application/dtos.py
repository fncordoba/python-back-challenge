from pydantic import BaseModel, Field
from typing import List, Optional, Generic, TypeVar
from datetime import datetime, date
from uuid import UUID
from decimal import Decimal
from src.domain.enums import InvoiceStatus, Currency

# --- Pagination ---
T = TypeVar("T")

class PaginationParams(BaseModel):
    limit: int = Field(10, ge=1, le=100)
    offset: int = Field(0, ge=0)

class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    limit: int
    offset: int

# --- Command DTOs ---

class CreateSchoolCommand(BaseModel):
    name: str

class UpdateSchoolCommand(BaseModel):
    school_id: UUID
    name: str

class CreateStudentCommand(BaseModel):
    school_id: UUID
    name: str

class UpdateStudentCommand(BaseModel):
    student_id: UUID
    name: str

class CreateInvoiceCommand(BaseModel):
    student_id: UUID
    amount: Decimal
    currency: Currency
    due_date: date

class ProcessPaymentCommand(BaseModel):
    invoice_id: UUID
    amount: Decimal

# --- Query Result DTOs ---

class SchoolDTO(BaseModel):
    id: UUID
    name: str
    created_at: datetime

class StudentDTO(BaseModel):
    id: UUID
    school_id: UUID
    name: str
    created_at: datetime

class InvoiceDTO(BaseModel):
    id: UUID
    amount_total: Decimal
    amount_paid: Decimal
    amount_due: Decimal
    currency: Currency
    status: InvoiceStatus
    issued_at: datetime
    due_date: date

class AccountStatementDTO(BaseModel):
    entity_id: UUID
    generated_at: datetime
    invoices: List[InvoiceDTO]
    total_due: Decimal
    currency: str
