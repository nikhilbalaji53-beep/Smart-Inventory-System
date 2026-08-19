from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
from pydantic import BaseModel, field_validator, constr
import re
import html

from database import get_db
from models import User
from auth import (
    hash_password,
    verify_password,
    create_access_token,
    verify_token,
    ACCESS_TOKEN_EXPIRE_MINUTES
)


class UserRegister(BaseModel):
    username: constr(min_length=3, max_length=50)  # type: ignore
    email: constr(max_length=120)  # type: ignore
    password: constr(min_length=8, max_length=128)  # type: ignore
    
    @field_validator('email', mode='before')
    @classmethod
    def sanitize_email(cls, v):
        """Sanitize and validate email"""
        v = v.strip().lower()
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', v):
            raise ValueError('Invalid email format')
        return v
    
    @field_validator('username', mode='before')
    @classmethod
    def sanitize_username(cls, v):
        """Sanitize username - alphanumeric and underscore only"""
        v = v.strip()
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('Username can only contain letters, numbers, and underscores')
        return v
    
    @field_validator('password', mode='before')
    @classmethod
    def validate_password_strength(cls, v):
        """Validate password strength"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'[0-9]', v):
            raise ValueError('Password must contain at least one digit')
        if not re.search(r'[!@#$%^&*()_+\-=\[\]{};:\'",.<>?/\\|`~]', v):
            raise ValueError('Password must contain at least one special character')
        return v


class UserLogin(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    username: str
    is_admin: int


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    is_admin: int

    class Config:
        from_attributes = True


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post("/register", response_model=UserResponse)
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """Register a new user (first user becomes admin)"""
    
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(
            (User.username == user_data.username) | 
            (User.email == user_data.email)
        ).first()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username or email already registered"
            )
        
        # Check if this is the first user (auto-admin)
        user_count = db.query(User).count()
        is_admin = 1 if user_count == 0 else 0
        
        # Create new user
        hashed_password = hash_password(user_data.password)
        new_user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hashed_password,
            is_admin=is_admin
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        return new_user
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Registration error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )


@router.post("/login", response_model=TokenResponse)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """Login user and return JWT token"""
    
    # Find user by username
    user = db.query(User).filter(User.username == credentials.username).first()
    
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "username": user.username,
        "is_admin": user.is_admin
    }


@router.get("/me", response_model=UserResponse)
def get_current_user(
    username: str = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Get current authenticated user"""
    
    user = db.query(User).filter(User.username == username).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user


@router.post("/admin/register", response_model=UserResponse)
def register_admin(user_data: UserRegister, db: Session = Depends(get_db)):
    """Register a new admin user (First user is auto-admin, others need verification)"""
    
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(
            (User.username == user_data.username) | 
            (User.email == user_data.email)
        ).first()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username or email already registered"
            )
        
        # Check if this is the first user (auto-admin)
        user_count = db.query(User).count()
        is_admin = 1 if user_count == 0 else 0
        
        # Create new admin user
        hashed_password = hash_password(user_data.password)
        new_user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hashed_password,
            is_admin=is_admin
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        return new_user
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Admin registration error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Admin registration failed: {str(e)}"
        )


@router.post("/admin/promote", response_model=UserResponse)
def promote_to_admin(
    target_username: str,
    current_username: str = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Promote a user to admin (requires current admin)"""
    
    # Check if current user is admin
    current_user = db.query(User).filter(User.username == current_username).first()
    if not current_user or current_user.is_admin != 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can promote users"
        )
    
    # Find target user
    target_user = db.query(User).filter(User.username == target_username).first()
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Target user not found"
        )
    
    # Promote user
    target_user.is_admin = 1
    db.commit()
    db.refresh(target_user)
    
    return target_user
