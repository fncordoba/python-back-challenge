from src.application.ports.repositories import (
    SchoolRepository, StudentRepository, InvoiceRepository, UnitOfWork
)
from src.application.ports.cache import CacheService
from .school import SchoolCommandsMixin
from .student import StudentCommandsMixin
from .invoice import InvoiceCommandsMixin

class CommandHandlers(SchoolCommandsMixin, StudentCommandsMixin, InvoiceCommandsMixin):
    def __init__(
        self,
        uow: UnitOfWork,
        school_repo: SchoolRepository,
        student_repo: StudentRepository,
        invoice_repo: InvoiceRepository,
        cache: CacheService
    ):
        self.uow = uow
        self.school_repo = school_repo
        self.student_repo = student_repo
        self.invoice_repo = invoice_repo
        self.cache = cache
