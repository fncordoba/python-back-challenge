from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import declarative_base

Base = declarative_base()

from .models_business import SchoolModel, StudentModel, InvoiceModel, PaymentModel
from .models_auth import UserModel
