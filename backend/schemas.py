from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class ProductBase(BaseModel):
    name: str
    category: str | None = None
    price: Decimal
    current_stock: int = 0
    minimum_stock: int = 10
    supplier: str | None = None
    expiry_date: date | None = None


class ProductCreate(ProductBase):
    pass


class ProductResponse(ProductBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
class ProductUpdate(BaseModel):
    quantity: int