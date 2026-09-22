from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordBearer
from fastapi import HTTPException, status
from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .db import get_async_session
from .models import User
from .schemas import RolesUser
import os
from dotenv import load_dotenv, find_dotenv


load_dotenv(find_dotenv())
SECRET_KEY = os.getenv("SECRET_KEY")


#password start
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
#password start



ALGORITHM =  "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def create_access_token(data: dict) -> str:
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode.update({"exp": expire})

    token = jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

def decode_access_token(token: str):
    try:
        payload = jwt.decode(
        token,
        SECRET_KEY,
        algorithms=[ALGORITHM]
        )
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
    user_id = payload.get("sub") 

    if not user_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return user_id


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_async_session)
):
    try:
        user_id = int(decode_access_token(token))
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    result = await session.execute(select(User).where(User.id == user_id))
    existing_user = result.scalar_one_or_none()

    if existing_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    return existing_user


def has_permission(user_role:RolesUser, endpoint_category:str, policy:str) -> bool:

    Permissions = {
        "Permissions":{
            "admin":{
            "project":["update_any", "delete_any", "read_any"],
            "task":["update_any", "delete_any", "read_any"]           
        }        
        }
    }
    if user_role.value == "admin":
        policy_list = Permissions["Permissions"][user_role.value][endpoint_category]
        return policy in policy_list
    else:
        return False