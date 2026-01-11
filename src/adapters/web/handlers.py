from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import List, Optional


from src.application.dtos import (
    CreateSchoolCommand, CreateStudentCommand, 
    CreateInvoiceCommand, ProcessPaymentCommand,
    SchoolDTO, StudentDTO, InvoiceDTO, AccountStatementDTO
)
from src.adapters.persistence.repos import (
    SQLAlchemyUnitOfWork, 
    SQLAlchemySchoolRepository, 
    SQLAlchemyStudentRepository, 
    SQLAlchemyInvoiceRepository,
    SQLAlchemyStatementRepository
)
from src.adapters.web.auth_handlers import get_current_active_admin, get_current_user
from src.adapters.cache.redis_adapter import RedisCacheAdapter
from src.domain.exceptions import EntityNotFound, BusinessRuleViolation
from src.application.dtos import (
    PaginationParams, PaginatedResponse, UpdateSchoolCommand, UpdateStudentCommand
)
from src.application.use_cases.commands import CommandHandlers
from src.application.use_cases.queries import QueryHandlers

import os
from src.adapters.persistence.db import get_db, REDIS_URL, cache_service

async def get_command_handlers(session: AsyncSession = Depends(get_db)):
    uow = SQLAlchemyUnitOfWork(session)
    school_repo = SQLAlchemySchoolRepository(session)
    student_repo = SQLAlchemyStudentRepository(session)
    invoice_repo = SQLAlchemyInvoiceRepository(session)
    
    return CommandHandlers(
        uow=uow, 
        school_repo=school_repo, 
        student_repo=student_repo, 
        invoice_repo=invoice_repo, 
        cache=cache_service
    )

async def get_query_handlers(session: AsyncSession = Depends(get_db)):
    statement_repo = SQLAlchemyStatementRepository(session)
    school_repo = SQLAlchemySchoolRepository(session)
    student_repo = SQLAlchemyStudentRepository(session)
    invoice_repo = SQLAlchemyInvoiceRepository(session)
    return QueryHandlers(
        statement_repo=statement_repo, 
        school_repo=school_repo, 
        student_repo=student_repo, 
        invoice_repo=invoice_repo, 
        cache=cache_service
    )


router = APIRouter()

# --- Schools ---

@router.post("/schools", status_code=201, response_model=SchoolDTO)
async def create_school(
    cmd: CreateSchoolCommand,
    current_user = Depends(get_current_active_admin),
    handlers: CommandHandlers = Depends(get_command_handlers)
):
    return await handlers.create_school(cmd)

@router.get("/schools", response_model=PaginatedResponse[SchoolDTO])
async def list_schools(
    limit: int = 10, offset: int = 0,
    handlers: QueryHandlers = Depends(get_query_handlers)
):
    params = PaginationParams(limit=limit, offset=offset)
    return await handlers.list_schools(params)

@router.delete("/schools/{school_id}", status_code=204)
async def delete_school(
    school_id: UUID,
    current_user = Depends(get_current_active_admin),
    handlers: CommandHandlers = Depends(get_command_handlers)
):
    try:
        await handlers.delete_school(school_id)
    except EntityNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.patch("/schools/{school_id}", response_model=SchoolDTO)
async def update_school(
    school_id: UUID,
    cmd: UpdateSchoolCommand,
    current_user = Depends(get_current_active_admin),
    handlers: CommandHandlers = Depends(get_command_handlers)
):
    if school_id != cmd.school_id:
        raise HTTPException(status_code=400, detail="ID mismatch")
    try:
        return await handlers.update_school(cmd)
    except EntityNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))

# --- Students ---

@router.post("/students", status_code=201, response_model=StudentDTO)
async def create_student(
    cmd: CreateStudentCommand,
    current_user = Depends(get_current_active_admin),
    handlers: CommandHandlers = Depends(get_command_handlers)
):
    try:
        return await handlers.create_student(cmd)
    except EntityNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/students", response_model=PaginatedResponse[StudentDTO])
async def list_students(
    school_id: Optional[UUID] = None,
    limit: int = 10, offset: int = 0,
    handlers: QueryHandlers = Depends(get_query_handlers)
):
    params = PaginationParams(limit=limit, offset=offset)
    return await handlers.list_students(params, school_id)

@router.delete("/students/{student_id}", status_code=204)
async def delete_student(
    student_id: UUID,
    current_user = Depends(get_current_active_admin),
    handlers: CommandHandlers = Depends(get_command_handlers)
):
    try:
        await handlers.delete_student(student_id)
    except EntityNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.patch("/students/{student_id}", response_model=StudentDTO)
async def update_student(
    student_id: UUID,
    cmd: UpdateStudentCommand,
    current_user = Depends(get_current_active_admin),
    handlers: CommandHandlers = Depends(get_command_handlers)
):
    if student_id != cmd.student_id:
        raise HTTPException(status_code=400, detail="ID mismatch")
    try:
        return await handlers.update_student(cmd)
    except EntityNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))

# --- Invoices ---

@router.post("/invoices", status_code=201, response_model=InvoiceDTO)
async def create_invoice(
    cmd: CreateInvoiceCommand,
    current_user = Depends(get_current_active_admin),
    handlers: CommandHandlers = Depends(get_command_handlers)
):
    try:
        return await handlers.create_invoice(cmd)
    except EntityNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/invoices", response_model=PaginatedResponse[InvoiceDTO])
async def list_invoices(
    student_id: Optional[UUID] = None,
    limit: int = 10, offset: int = 0,
    handlers: QueryHandlers = Depends(get_query_handlers)
):
    params = PaginationParams(limit=limit, offset=offset)
    return await handlers.list_invoices(params, student_id)

@router.delete("/invoices/{invoice_id}", status_code=204)
async def delete_invoice(
    invoice_id: UUID,
    current_user = Depends(get_current_active_admin),
    handlers: CommandHandlers = Depends(get_command_handlers)
):
    try:
        await handlers.delete_invoice(invoice_id)
    except EntityNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/payments", status_code=201)
async def process_payment(
    cmd: ProcessPaymentCommand,
    current_user = Depends(get_current_active_admin),
    handlers: CommandHandlers = Depends(get_command_handlers)
):
    try:
        payment_id = await handlers.process_payment(cmd)
        return {"id": payment_id, "status": "processed"}
    except EntityNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except BusinessRuleViolation as e:
        raise HTTPException(status_code=409, detail=str(e))

@router.get("/students/{student_id}/account-statement", response_model=AccountStatementDTO)
async def get_student_statement(
    student_id: UUID, 
    handlers: QueryHandlers = Depends(get_query_handlers)
):
    try:
        return await handlers.get_student_account_statement(student_id)
    except EntityNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/schools/{school_id}/account-statement", response_model=AccountStatementDTO)
async def get_school_statement(
    school_id: UUID, 
    handlers: QueryHandlers = Depends(get_query_handlers)
):
    try:
        return await handlers.get_school_account_statement(school_id)
    except EntityNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/health")
async def health_check():
    return {"status": "ok"}
