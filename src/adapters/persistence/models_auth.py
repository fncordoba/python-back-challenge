from sqlalchemy import Column, String, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from src.adapters.persistence import Base
from src.domain.auth import UserRole

class UserModel(Base):
    __tablename__ = "users"
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    role = Column(SAEnum(UserRole), nullable=False)
    
    # Optional foreign keys to link with business entities
    school_id = Column(PG_UUID(as_uuid=True), ForeignKey("schools.id"), nullable=True)
    student_id = Column(PG_UUID(as_uuid=True), ForeignKey("students.id"), nullable=True)
    
    created_at = Column(DateTime, nullable=False)
