import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock

@pytest.fixture
def mock_uow():
    uow = AsyncMock()
    uow.commit = AsyncMock()
    uow.rollback = AsyncMock()
    return uow

@pytest.fixture
def mock_school_repo():
    repo = AsyncMock()
    # Setup common methods
    repo.save = AsyncMock()
    repo.get_by_id = AsyncMock(return_value=None)
    return repo

@pytest.fixture
def mock_student_repo():
    repo = AsyncMock()
    repo.save = AsyncMock()
    repo.get_by_id = AsyncMock(return_value=None)
    return repo

@pytest.fixture
def mock_invoice_repo():
    repo = AsyncMock()
    repo.save = AsyncMock()
    repo.get_by_id = AsyncMock(return_value=None)
    return repo

@pytest.fixture
def mock_cache():
    cache = AsyncMock()
    cache.get = AsyncMock(return_value=None)
    cache.set = AsyncMock()
    cache.increment_version = AsyncMock()
    return cache
