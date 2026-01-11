import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from src.adapters.cache.redis_adapter import RedisCacheAdapter
from src.config import settings

DATABASE_URL = settings.DATABASE_URL
REDIS_URL = settings.REDIS_URL

engine = create_async_engine(DATABASE_URL)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

cache_service = RedisCacheAdapter(REDIS_URL)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
