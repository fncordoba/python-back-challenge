import pytest
from httpx import AsyncClient
from uuid import uuid4

# We assume conftest.py provides 'async_client' fixture or we can use specific client logic
# But for now, let's write simple integration tests using the client

@pytest.mark.asyncio
async def test_login(async_client):
    # This requires the admin seeded in conftest or a fixture. 
    # Or we can create one here if we had direct access to repo.
    # Given the environment, maybe mocking is better for "Unit" tests, 
    # but "Integration" tests are more valuable here.
    
    # Let's try to login with the seeded admin (knowing the seed runs on startup/manually)
    # Ideally, tests should be isolated and seed their own data.
    pass

# Refactoring strategy:
# Since we are running `docker compose exec api pytest`, we are running against the DB.
# conftest.py usually sets up a clean DB.
# We need to make sure we can create a user in the test.

from src.domain.auth import User, UserRole
from src.adapters.auth.password_service import PasswordService
from src.adapters.persistence.repos.auth import SQLAlchemyAuthRepository

@pytest.mark.asyncio
async def test_auth_flow(async_client, session):
    # 1. Create User directly in DB
    email = f"test_admin_{uuid4()}@example.com"
    pwd = "securepassword"
    pwd_hash = PasswordService.get_password_hash(pwd)
    
    repo = SQLAlchemyAuthRepository(session)
    user = User.create(email=email, password_hash=pwd_hash, role=UserRole.ADMIN)
    await repo.save(user)
    await session.commit()
    
    # 2. Try Login
    resp = await async_client.post("/token", data={"username": email, "password": pwd})
    assert resp.status_code == 200
    token = resp.json()["access_token"]
    
    # 3. Access Protected Endpoint
    headers = {"Authorization": f"Bearer {token}"}
    school_payload = {"name": "Auth Test School"}
    resp = await async_client.post("/schools", json=school_payload, headers=headers)
    assert resp.status_code == 201
    
    # 4. Try Access with User Role (Should fail for School Creation?)
    # Create Student User
    student_email = f"student_{uuid4()}@example.com"
    student_user = User.create(email=student_email, password_hash=pwd_hash, role=UserRole.STUDENT)
    await repo.save(student_user)
    await session.commit()
    
    # Login as student
    resp = await async_client.post("/token", data={"username": student_email, "password": pwd})
    student_token = resp.json()["access_token"]
    student_headers = {"Authorization": f"Bearer {student_token}"}
    
    # Try Create School
    resp = await async_client.post("/schools", json={"name": "Hacker School"}, headers=student_headers)
    assert resp.status_code == 403
