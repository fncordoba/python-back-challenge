from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
import jwt

from src.adapters.persistence.db import get_db
from src.adapters.persistence.repos.auth import SQLAlchemyAuthRepository
from src.adapters.auth.password_service import PasswordService
from src.adapters.auth.jwt_service import JWTService
from src.domain.auth import User, UserRole
from src.domain.exceptions import AuthenticationError

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], session: AsyncSession = Depends(get_db)):
    payload = JWTService.decode_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    email: str = payload.get("sub")
    if email is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")
        
    repo = SQLAlchemyAuthRepository(session)
    user = await repo.get_by_email(email)
    if not user:
         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
         
    return user

async def get_current_active_admin(current_user: Annotated[User, Depends(get_current_user)]):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return current_user

@router.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: AsyncSession = Depends(get_db)
):
    repo = SQLAlchemyAuthRepository(session)
    user = await repo.get_by_email(form_data.username)
    if not user or not PasswordService.verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    access_token = JWTService.create_access_token(
        data={"sub": user.email, "role": user.role.value}
    )
    return {"access_token": access_token, "token_type": "bearer"}
