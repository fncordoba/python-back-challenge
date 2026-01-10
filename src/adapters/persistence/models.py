from sqlalchemy import Column, String, DateTime, ForeignKey, Date, Numeric, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import declarative_base, relationship

from src.domain.enums import InvoiceStatus, Currency

Base = declarative_base()

class SchoolModel(Base):
    __tablename__ = "schools"
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False)
    
    # Relationships
    students = relationship("StudentModel", back_populates="school")

class StudentModel(Base):
    __tablename__ = "students"
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True)
    school_id = Column(PG_UUID(as_uuid=True), ForeignKey("schools.id"), nullable=False, index=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False)
    
    # Relationships
    school = relationship("SchoolModel", back_populates="students")
    invoices = relationship("InvoiceModel", back_populates="student")

class InvoiceModel(Base):
    __tablename__ = "invoices"
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True)
    student_id = Column(PG_UUID(as_uuid=True), ForeignKey("students.id"), nullable=False, index=True)
    school_id = Column(PG_UUID(as_uuid=True), ForeignKey("schools.id"), nullable=False, index=True)
    
    amount_total = Column(Numeric(10, 2), nullable=False)
    currency = Column(SAEnum(Currency), nullable=False)
    
    issued_at = Column(DateTime, nullable=False)
    due_date = Column(Date, nullable=False)
    status = Column(SAEnum(InvoiceStatus), nullable=False, index=True)
    
    # Relationships
    student = relationship("StudentModel", back_populates="invoices")
    payments = relationship("PaymentModel", back_populates="invoice")

class PaymentModel(Base):
    __tablename__ = "payments"
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True)
    invoice_id = Column(PG_UUID(as_uuid=True), ForeignKey("invoices.id"), nullable=False, index=True)
    
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(SAEnum(Currency), nullable=False) 
    paid_at = Column(DateTime, nullable=False)
    
    # Relationships
    invoice = relationship("InvoiceModel", back_populates="payments")
