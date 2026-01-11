import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from src.adapters.persistence.repos.auth import SQLAlchemyAuthRepository
from src.adapters.auth.password_service import PasswordService
from src.domain.auth import User, UserRole
from src.config import settings

DATABASE_URL = settings.DATABASE_URL

async def seed_admin():
    engine = create_async_engine(DATABASE_URL)
    AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)
    
    async with AsyncSessionLocal() as session:
        repo = SQLAlchemyAuthRepository(session)
        
        # Check if exists
        existing = await repo.get_by_email("admin@mattilda.io")
        if existing:
            print("Admin already exists.")
            return

        print("Creating Admin user...")
        pwd_hash = PasswordService.get_password_hash("admin123")
        admin = User.create(
            email="admin@mattilda.io",
            password_hash=pwd_hash,
            role=UserRole.ADMIN
        )
        await repo.save(admin)
        await session.commit()
        print(f"Admin created: {admin.id}")

if __name__ == "__main__":
    asyncio.run(seed_admin())
