from enum import Enum
from dataclasses import dataclass
from uuid import UUID, uuid4
from datetime import datetime

class UserRole(str, Enum):
    ADMIN = "admin"
    SCHOOL = "school"
    STUDENT = "student"

@dataclass
class User:
    id: UUID
    email: str
    password_hash: str
    role: UserRole
    # Optional links to other aggregates
    school_id: UUID | None = None
    student_id: UUID | None = None
    created_at: datetime = datetime.utcnow()

    @classmethod
    def create(cls, email: str, password_hash: str, role: UserRole, school_id: UUID | None = None, student_id: UUID | None = None) -> "User":
        return cls(
            id=uuid4(),
            email=email,
            password_hash=password_hash,
            role=role,
            school_id=school_id,
            student_id=student_id,
            created_at=datetime.utcnow()
        )
