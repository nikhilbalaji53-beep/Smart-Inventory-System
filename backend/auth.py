from datetime import datetime, timedelta
from typing import Optional, Any
import os
import jwt
import hashlib
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from passlib.context import CryptContext

# Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "local-development-secret-change-me")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing using PBKDF2 (no bcrypt compatibility issues)
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
security = HTTPBearer()


def hash_password(password: str) -> str:
    """Hash a password using PBKDF2"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt


class TokenPayload(str):
    """String representing the token subject, with dict-like access to payload claims."""
    def __new__(cls, sub: str, payload: dict | None = None):
        instance = super().__new__(cls, sub or "")
        instance.payload = payload or {}
        return instance

    def get(self, key, default=None):
        return self.payload.get(key, default)

    def __getitem__(self, key):
        if isinstance(key, str):
            return self.payload[key]
        return super().__getitem__(key)

    def __contains__(self, key):
        if isinstance(key, str):
            return key in self.payload or super().__contains__(key)
        return super().__contains__(key)


def verify_token(credentials: Any = Depends(security)) -> TokenPayload:
    """Verify JWT token and return the authenticated user ID."""
    token = credentials.credentials

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str | None = payload.get("sub") or payload.get("supplier_id") or payload.get("username")

        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return TokenPayload(user_id, payload)
    
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
