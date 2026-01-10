import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
from datetime import date as dt_date, datetime

from src.application.use_cases.commands import CommandHandlers
from src.application.dtos import CreateInvoiceCommand, CreateStudentCommand
from src.domain.entities import Student, School, Invoice
from src.domain.value_objects import Money
from src.domain.enums import Currency
