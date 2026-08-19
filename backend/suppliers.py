from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime, timedelta
import jwt
import re
import os
from passlib.context import CryptContext

from database import get_db
from models import Supplier
from auth import verify_token, hash_password

# Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "local-development-secret-change-me")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = 30

router = APIRouter(prefix="/supplier", tags=["Supplier"])

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Schemas
class SupplierRegister(BaseModel):
    supplier_id: str
    email: str
    company_name: str
    contact_person: str = ""
    password: str
    phone: str = ""
    address: str = ""
    gst_number: str = ""

    class Config:
        from_attributes = True


class SupplierLogin(BaseModel):
    supplier_id_or_email: str
    password: str

    class Config:
        from_attributes = True


class SupplierResponse(BaseModel):
    id: int
    supplier_id: str
    email: str
    company_name: str
    contact_person: str | None = None
    phone: str | None = None
    address: str | None = None
    gst_number: str | None = None
    is_approved: int
    is_active: int
    created_at: datetime

    class Config:
        from_attributes = True


class SupplierTokenResponse(BaseModel):
    access_token: str
    token_type: str
    supplier_id: str
    company_name: str
    is_approved: int
    supplier_type: str = "supplier"

    class Config:
        from_attributes = True


# Password validation function
def validate_password(password: str) -> bool:
    """Validate password strength"""
    if len(password) < 8:
        return False
    if not re.search(r'[A-Z]', password):  # Uppercase
        return False
    if not re.search(r'[a-z]', password):  # Lowercase
        return False
    if not re.search(r'\d', password):  # Digit
        return False
    if not re.search(r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?]', password):  # Special char
        return False
    return True


# Detailed password validation for error messages
def get_password_validation_error(password: str) -> str | None:
    """Return detailed password validation error message, or None if valid"""
    if len(password) < 8:
        return "Password must be at least 8 characters long"
    if not re.search(r'[A-Z]', password):
        return "Password must contain at least one uppercase letter (A-Z)"
    if not re.search(r'[a-z]', password):
        return "Password must contain at least one lowercase letter (a-z)"
    if not re.search(r'\d', password):
        return "Password must contain at least one digit (0-9)"
    if not re.search(r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?]', password):
        return "Password must contain at least one special character (!@#$%^&*)"
    return None


# Supplier ID validation function
def validate_supplier_id(supplier_id: str) -> bool:
    """Validate supplier ID format (alphanumeric + underscore)"""
    return bool(re.match(r'^[a-zA-Z0-9_]{3,50}$', supplier_id))


@router.post("/register", response_model=SupplierResponse)
def register_supplier(supplier_data: SupplierRegister, db: Session = Depends(get_db)):
    """Register a new supplier"""
    
    # Validate supplier ID
    if not validate_supplier_id(supplier_data.supplier_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Supplier ID must be 3-50 characters, alphanumeric and underscore only"
        )
    
    # Validate password strength with detailed error
    password_error = get_password_validation_error(supplier_data.password)
    if password_error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=password_error
        )
    
    # Check if supplier ID already exists
    existing_supplier = db.query(Supplier).filter(
        Supplier.supplier_id == supplier_data.supplier_id
    ).first()
    
    if existing_supplier:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Supplier ID already registered"
        )
    
    # Check if email already exists
    existing_email = db.query(Supplier).filter(
        Supplier.email == supplier_data.email
    ).first()
    
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Hash password
    hashed_password = hash_password(supplier_data.password)
    
    # Create new supplier
    new_supplier = Supplier(
        supplier_id=supplier_data.supplier_id,
        email=supplier_data.email,
        company_name=supplier_data.company_name,
        contact_person=supplier_data.contact_person,
        hashed_password=hashed_password,
        phone=supplier_data.phone,
        address=supplier_data.address,
        gst_number=supplier_data.gst_number,
        is_approved=1,  # Auto-approved upon registration
        is_active=1
    )
    
    db.add(new_supplier)
    db.commit()
    db.refresh(new_supplier)
    
    return new_supplier


@router.post("/login", response_model=SupplierTokenResponse)
def login_supplier(login_data: SupplierLogin, db: Session = Depends(get_db)):
    """Login supplier with supplier ID or email"""
    
    # Find supplier by ID or email
    supplier = db.query(Supplier).filter(
        (Supplier.supplier_id == login_data.supplier_id_or_email) |
        (Supplier.email == login_data.supplier_id_or_email)
    ).first()
    
    if not supplier:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid supplier ID/email or password"
        )
    
    # Check if supplier is active
    if supplier.is_active == 0:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Supplier account is inactive"
        )
    
    # Verify password
    from auth import verify_password
    if not verify_password(login_data.password, supplier.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid supplier ID/email or password"
        )
    
    # Generate JWT token
    payload = {
        "sub": supplier.supplier_id,
        "supplier_id": supplier.supplier_id,
        "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    }
    access_token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "supplier_id": supplier.supplier_id,
        "company_name": supplier.company_name,
        "is_approved": supplier.is_approved,
        "supplier_type": "supplier"
    }


@router.get("/pending")
def get_pending_suppliers(db: Session = Depends(get_db)):
    """List suppliers waiting for admin approval."""
    suppliers = db.query(Supplier).filter(Supplier.is_approved == 0).all()
    return [
        {
            "id": supplier.id,
            "supplier_id": supplier.supplier_id,
            "email": supplier.email,
            "company_name": supplier.company_name,
            "contact_person": supplier.contact_person,
            "phone": supplier.phone,
            "address": supplier.address,
            "gst_number": supplier.gst_number,
            "is_approved": supplier.is_approved,
            "is_active": supplier.is_active,
            "created_at": supplier.created_at,
        }
        for supplier in suppliers
    ]


@router.post("/approve/{supplier_id}")
def approve_supplier(supplier_id: str, payload: dict | None = None, db: Session = Depends(get_db)):
    """Approve or reject a supplier registration."""
    supplier = db.query(Supplier).filter(Supplier.supplier_id == supplier_id).first()
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")

    decision = (payload or {}).get("status", "approved").strip().lower()
    if decision not in {"approved", "reject", "rejected"}:
        raise HTTPException(status_code=400, detail="Status must be 'approved' or 'rejected'")

    supplier.is_approved = 1 if decision in {"approved"} else 0
    supplier.is_active = 1 if decision == "approved" else 0
    db.commit()
    db.refresh(supplier)

    return {
        "supplier_id": supplier.supplier_id,
        "email": supplier.email,
        "company_name": supplier.company_name,
        "is_approved": supplier.is_approved,
        "is_active": supplier.is_active,
        "status": "approved" if supplier.is_approved == 1 else "rejected",
        "message": "Supplier approved successfully" if supplier.is_approved == 1 else "Supplier rejected and disabled"
    }


@router.get("/all")
def get_all_suppliers(db: Session = Depends(get_db)):
    """List all suppliers for admin review."""
    suppliers = db.query(Supplier).order_by(Supplier.created_at.desc()).all()
    return [
        {
            "id": supplier.id,
            "supplier_id": supplier.supplier_id,
            "email": supplier.email,
            "company_name": supplier.company_name,
            "contact_person": supplier.contact_person,
            "phone": supplier.phone,
            "address": supplier.address,
            "gst_number": supplier.gst_number,
            "is_approved": supplier.is_approved,
            "is_active": supplier.is_active,
            "created_at": supplier.created_at,
        }
        for supplier in suppliers
    ]


@router.get("/profile", response_model=SupplierResponse)
def get_supplier_profile(current_supplier_id: str = Depends(verify_token), db: Session = Depends(get_db)):
    """Get current supplier profile"""
    
    supplier = db.query(Supplier).filter(
        Supplier.supplier_id == current_supplier_id
    ).first()
    
    if not supplier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Supplier not found"
        )
    
    return supplier


@router.get("/status/{supplier_id}")
def get_supplier_status(supplier_id: str, db: Session = Depends(get_db)):
    """Get supplier approval status"""
    
    supplier = db.query(Supplier).filter(
        Supplier.supplier_id == supplier_id
    ).first()
    
    if not supplier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Supplier not found"
        )
    
    return {
        "supplier_id": supplier.supplier_id,
        "is_approved": supplier.is_approved,
        "is_active": supplier.is_active,
        "message": "Pending admin approval" if supplier.is_approved == 0 else "Approved"
    }
