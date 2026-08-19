from datetime import datetime
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session

from auth import verify_token
from database import get_db
from models import Product, PurchaseTransaction, SalesTransaction, Supplier, User

router = APIRouter(prefix="/transactions", tags=["Transactions"])


class PurchaseCreate(BaseModel):
    product_id: int
    quantity: int = Field(gt=0)
    unit_cost: Decimal = Field(gt=0)
    supplier_id: int | None = None
    notes: str | None = None


class SaleCreate(BaseModel):
    product_id: int
    quantity: int = Field(gt=0)
    unit_price: Decimal = Field(gt=0)
    notes: str | None = None


class TransactionResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    transaction_date: datetime
    model_config = ConfigDict(from_attributes=True)


def require_admin(subject: str, db: Session):
    user = db.query(User).filter(User.username == subject, User.is_admin == 1).first()
    if not user:
        raise HTTPException(status_code=403, detail="Admin access required")


@router.post("/purchase", response_model=TransactionResponse, status_code=201)
def record_purchase(data: PurchaseCreate, subject: str = Depends(verify_token), db: Session = Depends(get_db)):
    require_admin(subject, db)
    product = db.query(Product).filter(Product.id == data.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    if data.supplier_id and not db.query(Supplier).filter(Supplier.id == data.supplier_id).first():
        raise HTTPException(status_code=404, detail="Supplier not found")

    transaction = PurchaseTransaction(
        **data.model_dump(),
        total_cost=data.quantity * data.unit_cost,
    )
    product.current_stock += data.quantity
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction


@router.post("/sale", response_model=TransactionResponse, status_code=201)
def record_sale(data: SaleCreate, subject: str = Depends(verify_token), db: Session = Depends(get_db)):
    require_admin(subject, db)
    product = db.query(Product).filter(Product.id == data.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    if product.current_stock < data.quantity:
        raise HTTPException(status_code=400, detail="Insufficient stock for this sale")

    transaction = SalesTransaction(
        **data.model_dump(),
        total_revenue=data.quantity * data.unit_price,
    )
    product.current_stock -= data.quantity
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction