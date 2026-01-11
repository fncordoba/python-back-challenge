import pytest
import pytest_asyncio
import os
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from src.adapters.persistence.db import DATABASE_URL
from src.main import app
from src.adapters.web.handlers import get_db
from src.adapters.persistence import Base

@pytest_asyncio.fixture(scope="session")
async def engine():
    engine = create_async_engine(DATABASE_URL)
    yield engine
    await engine.dispose()

@pytest_asyncio.fixture(scope="function")
async def session(engine):
    # For tests, we might want to start transaction and rollback
    # But for simplicity in this setup, we just yield a session
    # Ideally, we should drop/create tables or use nested transaction
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    async with async_session() as session:
         yield session

@pytest_asyncio.fixture(scope="function")
async def async_client(session):
    async def override_get_db():
        yield session
    
    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
    app.dependency_overrides.clear()
