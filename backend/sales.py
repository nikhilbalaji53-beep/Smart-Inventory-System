from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import text

from database import get_db
from models import Product, Sale, SalesTransaction

router = APIRouter(tags=["Sales"])


class SaleRequest(BaseModel):
    product_id: int
    quantity: int = Field(gt=0)
    sale_date: Optional[str] = None


class SaleHistoryItem(BaseModel):
    id: int
    product_name: str
    quantity: int
    sale_date: Optional[str] = None


def process_sale_record(product_id: int, quantity: int, sale_date: Optional[str], db: Session):
    if not product_id or not quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="product_id and quantity are required"
        )

    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": "Product not found"}
        )

    available_stock = product.current_stock if product.current_stock is not None else getattr(product, "quantity", 0)
    if available_stock < quantity:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": "Insufficient stock quantity"}
        )

    # Deduct stock from products table (both current_stock and quantity)
    product.current_stock = available_stock - quantity
    product.quantity = product.current_stock

    sale_record_date = sale_date if sale_date else datetime.today().strftime("%Y-%m-%d")
    new_sale = Sale(
        product_id=product_id,
        quantity=quantity,
        sale_date=sale_record_date
    )
    db.add(new_sale)

    # Also record in sales_transactions for dashboard integration
    unit_price = product.price if product.price else 0
    sales_tx = SalesTransaction(
        product_id=product_id,
        quantity=quantity,
        unit_price=unit_price,
        total_revenue=quantity * unit_price,
        notes=f"Sale recorded via /api/sales"
    )
    db.add(sales_tx)

    db.commit()
    db.refresh(new_sale)

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={"message": "Sale recorded successfully and stock updated"}
    )


def fetch_sales_history(db: Session):
    results = db.execute(text("""
        SELECT sales.id, products.name as product_name, sales.quantity, sales.sale_date
        FROM sales
        JOIN products ON sales.product_id = products.id
        ORDER BY sales.id DESC
    """)).fetchall()

    return [
        {
            "id": row[0],
            "product_name": row[1],
            "quantity": row[2],
            "sale_date": row[3]
        }
        for row in results
    ]


# Support /api/sales and /sales routes
@router.post("/api/sales", status_code=201)
@router.post("/sales", status_code=201)
async def record_sale_api(request: Request, db: Session = Depends(get_db)):
    try:
        data = await request.json()
    except Exception:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": "Request body is required"}
        )

    if not data:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": "Request body is required"}
        )

    product_id = data.get("product_id")
    quantity = data.get("quantity")
    sale_date = data.get("sale_date")

    if not product_id or not quantity:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": "product_id and quantity are required"}
        )

    return process_sale_record(product_id, quantity, sale_date, db)


@router.get("/api/sales")
@router.get("/sales")
def get_sales_api(db: Session = Depends(get_db)):
    return fetch_sales_history(db)
