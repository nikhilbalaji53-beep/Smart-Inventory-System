from datetime import date, datetime
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session

from auth import verify_token
from database import get_db
from models import (
    Product,
    ProductSupplierMapping,
    ReorderDecision,
    Supplier,
    SupplierAlert,
    SupplierPerformance,
    User,
)

router = APIRouter(tags=["Supplier Workflow"])


class MappingCreate(BaseModel):
    product_id: int
    supplier_id: int
    unit_cost: Decimal = Field(gt=0)
    supplier_sku: str | None = None
    lead_time: int | None = Field(default=None, ge=0)
    minimum_order: int = Field(default=1, ge=1)
    is_preferred: int = Field(default=0, ge=0, le=1)
    is_active: int = Field(default=1, ge=0, le=1)
    notes: str | None = None


class MappingResponse(MappingCreate):
    id: int
    quality_score: Decimal | None = None
    last_purchase_date: datetime | None = None
    last_purchase_price: Decimal | None = None
    total_purchases: int
    model_config = ConfigDict(from_attributes=True)


class ReorderDecisionCreate(BaseModel):
    product_id: int
    supplier_id: int
    current_stock: int = Field(ge=0)
    predicted_usage: int | None = Field(default=None, ge=0)
    reorder_quantity: int = Field(gt=0)
    reorder_point: int = Field(ge=0)
    priority: str = "MEDIUM"
    reason: str | None = None
    estimated_lead_time: int | None = Field(default=None, ge=0)
    estimated_arrival_date: date | None = None


class ReorderDecisionResponse(ReorderDecisionCreate):
    id: int
    decision_date: datetime | None = None
    decision_status: str
    po_number: str | None = None
    model_config = ConfigDict(from_attributes=True)


class AlertCreate(BaseModel):
    supplier_id: int
    alert_type: str = Field(min_length=1, max_length=100)
    severity: str = Field(min_length=1, max_length=20)
    title: str = Field(min_length=1, max_length=255)
    message: str = Field(min_length=1)
    related_po: str | None = None
    notes: str | None = None


class AlertResponse(AlertCreate):
    id: int
    is_resolved: int
    resolution_date: datetime | None = None
    model_config = ConfigDict(from_attributes=True)


class PerformanceResponse(BaseModel):
    id: int
    supplier_id: int
    total_orders: int
    completed_orders: int
    cancelled_orders: int
    on_time_deliveries: int
    late_deliveries: int
    on_time_percentage: Decimal
    average_lead_time: int
    quality_issues: int
    quality_score: Decimal
    price_competitiveness: Decimal
    communication_rating: Decimal
    overall_rating: Decimal
    last_evaluation_date: datetime | None = None
    total_amount_spent: Decimal
    model_config = ConfigDict(from_attributes=True)


def get_actor(subject: str, db: Session):
    user = db.query(User).filter(User.username == subject).first()
    if user:
        return {"kind": "admin" if user.is_admin else "user", "id": user.id}

    supplier = db.query(Supplier).filter(Supplier.supplier_id == subject).first()
    if supplier:
        return {"kind": "supplier", "id": supplier.id}

    raise HTTPException(status_code=401, detail="Authenticated account not found")


def require_admin(subject: str, db: Session):
    actor = get_actor(subject, db)
    if actor["kind"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return actor


def get_supplier_or_404(supplier_id: int, db: Session):
    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return supplier


def enforce_supplier_scope(supplier_id: int, subject: str, db: Session):
    actor = get_actor(subject, db)
    if actor["kind"] == "supplier" and actor["id"] != supplier_id:
        raise HTTPException(status_code=403, detail="Cannot access another supplier")
    return actor


@router.post("/product-supplier-mapping", response_model=MappingResponse, status_code=201)
def create_mapping(data: MappingCreate, subject: str = Depends(verify_token), db: Session = Depends(get_db)):
    require_admin(subject, db)
    if not db.query(Product).filter(Product.id == data.product_id).first():
        raise HTTPException(status_code=404, detail="Product not found")
    get_supplier_or_404(data.supplier_id, db)

    mapping = ProductSupplierMapping(**data.model_dump())
    if mapping.is_preferred:
        db.query(ProductSupplierMapping).filter(
            ProductSupplierMapping.product_id == mapping.product_id
        ).update({"is_preferred": 0})
    db.add(mapping)
    db.commit()
    db.refresh(mapping)
    return mapping


@router.get("/product/{product_id}/suppliers", response_model=list[MappingResponse])
def list_product_suppliers(product_id: int, subject: str = Depends(verify_token), db: Session = Depends(get_db)):
    get_actor(subject, db)
    if not db.query(Product).filter(Product.id == product_id).first():
        raise HTTPException(status_code=404, detail="Product not found")
    return db.query(ProductSupplierMapping).filter(
        ProductSupplierMapping.product_id == product_id,
        ProductSupplierMapping.is_active == 1,
    ).all()


@router.get("/supplier/{supplier_id}/performance", response_model=PerformanceResponse | None)
def get_supplier_performance(supplier_id: int, subject: str = Depends(verify_token), db: Session = Depends(get_db)):
    enforce_supplier_scope(supplier_id, subject, db)
    get_supplier_or_404(supplier_id, db)
    return db.query(SupplierPerformance).filter(SupplierPerformance.supplier_id == supplier_id).first()


@router.get("/supplier/{supplier_id}/alerts", response_model=list[AlertResponse])
def get_supplier_alerts(
    supplier_id: int,
    active_only: bool = Query(default=True),
    subject: str = Depends(verify_token),
    db: Session = Depends(get_db),
):
    enforce_supplier_scope(supplier_id, subject, db)
    get_supplier_or_404(supplier_id, db)
    query = db.query(SupplierAlert).filter(SupplierAlert.supplier_id == supplier_id)
    if active_only:
        query = query.filter(SupplierAlert.is_resolved == 0)
    return query.order_by(SupplierAlert.created_at.desc()).all()


@router.post("/reorder-decision", response_model=ReorderDecisionResponse, status_code=201)
def create_reorder_decision(
    data: ReorderDecisionCreate,
    subject: str = Depends(verify_token),
    db: Session = Depends(get_db),
):
    require_admin(subject, db)
    if not db.query(Product).filter(Product.id == data.product_id).first():
        raise HTTPException(status_code=404, detail="Product not found")
    get_supplier_or_404(data.supplier_id, db)
    decision = ReorderDecision(**data.model_dump())
    db.add(decision)
    db.commit()
    db.refresh(decision)
    return decision


@router.get("/reorder-decisions", response_model=list[ReorderDecisionResponse])
def list_reorder_decisions(
    decision_status: str | None = None,
    subject: str = Depends(verify_token),
    db: Session = Depends(get_db),
):
    actor = get_actor(subject, db)
    query = db.query(ReorderDecision)
    if actor["kind"] == "supplier":
        query = query.filter(ReorderDecision.supplier_id == actor["id"])
    if decision_status:
        query = query.filter(ReorderDecision.decision_status == decision_status)
    return query.order_by(ReorderDecision.decision_date.desc()).all()


@router.post("/supplier-alert", response_model=AlertResponse, status_code=201)
def create_supplier_alert(
    data: AlertCreate,
    subject: str = Depends(verify_token),
    db: Session = Depends(get_db),
):
    require_admin(subject, db)
    get_supplier_or_404(data.supplier_id, db)
    alert = SupplierAlert(**data.model_dump())
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert


@router.patch("/supplier-alert/{alert_id}/resolve", response_model=AlertResponse)
def resolve_supplier_alert(alert_id: int, subject: str = Depends(verify_token), db: Session = Depends(get_db)):
    require_admin(subject, db)
    alert = db.query(SupplierAlert).filter(SupplierAlert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Supplier alert not found")
    alert.is_resolved = 1
    db.commit()
    db.refresh(alert)
    return alert