from src.application.ports.repositories import (
    StatementRepository, SchoolRepository, StudentRepository, InvoiceRepository
)
from src.application.ports.cache import CacheService
from .school import SchoolQueriesMixin
from .student import StudentQueriesMixin
from .invoice import InvoiceQueriesMixin

class QueryHandlers(SchoolQueriesMixin, StudentQueriesMixin, InvoiceQueriesMixin):
    def __init__(
        self,
        statement_repo: StatementRepository,
        school_repo: SchoolRepository,
        student_repo: StudentRepository,
        invoice_repo: InvoiceRepository,
        cache: CacheService
    ):
        self.statement_repo = statement_repo
        self.school_repo = school_repo
        self.student_repo = student_repo
        self.invoice_repo = invoice_repo
        self.cache = cache
