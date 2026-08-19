from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
from datetime import datetime, date
from typing import List

from database import get_db
from models import PurchaseOrder, OrderDelivery, Product, Supplier
from auth import verify_token
from alerts import get_alerts

router = APIRouter(prefix="/orders", tags=["Orders"])


# Schemas
class OrderDeliveryCreate(BaseModel):
    purchase_order_id: int
    quantity_delivered: int
    delivery_reference: str = ""
    shipping_carrier: str = ""
    tracking_number: str = ""
    notes: str = ""

    class Config:
        from_attributes = True


class OrderDeliveryResponse(BaseModel):
    id: int
    purchase_order_id: int
    supplier_id: int
    quantity_delivered: int
    delivery_date: datetime
    delivery_reference: str | None
    shipping_carrier: str | None
    tracking_number: str | None
    notes: str | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PurchaseOrderResponse(BaseModel):
    id: int
    po_number: str
    supplier_id: int
    product_id: int
    quantity_ordered: int
    unit_price: float
    total_amount: float
    status: str
    order_date: datetime
    expected_delivery: date | None
    notes: str | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PurchaseOrderWithDeliveries(BaseModel):
    order: PurchaseOrderResponse
    deliveries: List[OrderDeliveryResponse] = []

    class Config:
        from_attributes = True


# Supplier endpoints - get their pending purchase orders
@router.get("/pending")
def get_pending_orders(
    token_data: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Get pending purchase orders for the logged-in supplier"""
    
    supplier_id = token_data.get("supplier_id")
    if not supplier_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Not a supplier account"
        )
    
    supplier = db.query(Supplier).filter(
        Supplier.supplier_id == supplier_id
    ).first()
    
    if not supplier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Supplier not found"
        )
    
    pending_orders = db.query(PurchaseOrder).filter(
        PurchaseOrder.supplier_id == supplier.id,
        PurchaseOrder.status.in_(["PENDING", "ACCEPTED"])
    ).all()
    
    result = []
    for order in pending_orders:
        deliveries = db.query(OrderDelivery).filter(
            OrderDelivery.purchase_order_id == order.id
        ).all()
        
        result.append({
            "order": order,
            "deliveries": deliveries
        })
    
    return result


@router.get("/{po_id}")
def get_order_details(
    po_id: int,
    token_data: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Get details of a specific purchase order"""
    
    supplier_id = token_data.get("supplier_id")
    if not supplier_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Not a supplier account"
        )
    
    supplier = db.query(Supplier).filter(
        Supplier.supplier_id == supplier_id
    ).first()
    
    order = db.query(PurchaseOrder).filter(
        PurchaseOrder.id == po_id,
        PurchaseOrder.supplier_id == supplier.id
    ).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Purchase order not found"
        )
    
    deliveries = db.query(OrderDelivery).filter(
        OrderDelivery.purchase_order_id == po_id
    ).all()
    
    return {
        "order": order,
        "deliveries": deliveries
    }


@router.post("/{po_id}/accept")
def accept_order(
    po_id: int,
    token_data: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Supplier accepts a purchase order"""
    
    supplier_id = token_data.get("supplier_id")
    if not supplier_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Not a supplier account"
        )
    
    supplier = db.query(Supplier).filter(
        Supplier.supplier_id == supplier_id
    ).first()
    
    order = db.query(PurchaseOrder).filter(
        PurchaseOrder.id == po_id,
        PurchaseOrder.supplier_id == supplier.id
    ).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Purchase order not found"
        )
    
    if order.status != "PENDING":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot accept order with status {order.status}"
        )
    
    order.status = "ACCEPTED"
    db.commit()
    db.refresh(order)
    
    return {"message": "Order accepted successfully", "order": order}


@router.post("/{po_id}/deliver", response_model=OrderDeliveryResponse)
def submit_delivery(
    po_id: int,
    delivery: OrderDeliveryCreate,
    token_data: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Supplier submits delivery information for a purchase order"""
    
    supplier_id = token_data.get("supplier_id")
    if not supplier_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Not a supplier account"
        )
    
    supplier = db.query(Supplier).filter(
        Supplier.supplier_id == supplier_id
    ).first()
    
    order = db.query(PurchaseOrder).filter(
        PurchaseOrder.id == po_id,
        PurchaseOrder.supplier_id == supplier.id
    ).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Purchase order not found"
        )
    
    if order.status not in ["ACCEPTED", "DELIVERED"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot deliver order with status {order.status}"
        )
    
    if delivery.quantity_delivered > order.quantity_ordered:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Delivery quantity exceeds ordered quantity"
        )
    
    # Create delivery record
    new_delivery = OrderDelivery(
        purchase_order_id=po_id,
        supplier_id=supplier.id,
        quantity_delivered=delivery.quantity_delivered,
        delivery_reference=delivery.delivery_reference,
        shipping_carrier=delivery.shipping_carrier,
        tracking_number=delivery.tracking_number,
        notes=delivery.notes
    )
    
    db.add(new_delivery)
    
    # Update order status to DELIVERED if this is the full quantity
    total_delivered = db.query(
        func.sum(OrderDelivery.quantity_delivered)
    ).filter(
        OrderDelivery.purchase_order_id == po_id
    ).scalar() or 0
    
    if (total_delivered + delivery.quantity_delivered) >= order.quantity_ordered:
        order.status = "DELIVERED"
        
        # Update product stock immediately
        product = db.query(Product).filter(
            Product.id == order.product_id
        ).first()
        
        if product:
            product.current_stock += delivery.quantity_delivered
            db.add(product)
    
    db.commit()
    db.refresh(new_delivery)
    
    # Trigger alert check after stock update
    try:
        alerts = get_alerts(db)
    except:
        pass  # Silently continue if alerts fail
    
    return new_delivery


# Admin endpoints - create and manage purchase orders
@router.post("/")
def create_purchase_order(
    po_number: str,
    supplier_id: int,
    product_id: int,
    quantity_ordered: int,
    unit_price: float,
    expected_delivery: date = None,
    notes: str = "",
    token_data: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Admin creates a new purchase order for a supplier"""
    
    # Verify admin
    if not token_data.get("is_admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can create purchase orders"
        )
    
    # Verify supplier exists
    supplier = db.query(Supplier).filter(
        Supplier.id == supplier_id
    ).first()
    
    if not supplier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Supplier not found"
        )
    
    # Verify product exists
    product = db.query(Product).filter(
        Product.id == product_id
    ).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    total_amount = quantity_ordered * unit_price
    
    new_order = PurchaseOrder(
        po_number=po_number,
        supplier_id=supplier_id,
        product_id=product_id,
        quantity_ordered=quantity_ordered,
        unit_price=unit_price,
        total_amount=total_amount,
        expected_delivery=expected_delivery,
        notes=notes
    )
    
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    
    return new_order


@router.get("/", response_model=List[PurchaseOrderResponse])
def get_all_orders(
    status_filter: str = None,
    token_data: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Get all purchase orders (admin) or supplier's orders (supplier)"""
    
    query = db.query(PurchaseOrder)
    
    if status_filter:
        query = query.filter(PurchaseOrder.status == status_filter)
    
    return query.all()
