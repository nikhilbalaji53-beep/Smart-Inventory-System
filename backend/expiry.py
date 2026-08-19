from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from database import get_db
from models import Product


router = APIRouter(
    prefix="/expiry",
    tags=["Expiry Monitoring"]
)


@router.get("/alerts")
def get_expiry_alerts(
    days_until_expiry: int = 7,
    db: Session = Depends(get_db)
):
    """
    Get products expiring within specified days
    
    Parameters:
    - days_until_expiry: Number of days to check for expiry (default: 7)
    """
    
    products = db.query(Product).all()
    
    today = datetime.now().date()
    expiry_alerts = []
    
    for product in products:
        if not product.expiry_date:
            continue
        
        days_until_exp = (product.expiry_date - today).days
        
        # Check if product is expiring or already expired
        if days_until_exp <= days_until_expiry:
            severity = "CRITICAL" if days_until_exp <= 0 else "WARNING"
            status = "EXPIRED" if days_until_exp < 0 else "EXPIRING_SOON"
            
            expiry_alerts.append({
                "product_id": product.id,
                "product_name": product.name,
                "expiry_date": product.expiry_date,
                "days_until_expiry": days_until_exp,
                "current_stock": product.current_stock,
                "severity": severity,
                "status": status
            })
    
    # Sort by days until expiry (expired items first)
    expiry_alerts.sort(key=lambda x: x["days_until_expiry"])
    
    return {
        "count": len(expiry_alerts),
        "alerts": expiry_alerts,
        "check_period_days": days_until_expiry
    }


@router.get("/expiring-soon")
def get_expiring_soon_products(db: Session = Depends(get_db)):
    """Get products expiring in next 7 days with stock"""
    
    today = datetime.now().date()
    expiry_threshold = today + timedelta(days=7)
    
    expiring_products = db.query(Product).filter(
        (Product.expiry_date >= today) &
        (Product.expiry_date <= expiry_threshold)
    ).order_by(Product.expiry_date).all()
    
    products_data = []
    
    for product in expiring_products:
        days_until_exp = (product.expiry_date - today).days
        
        products_data.append({
            "product_id": product.id,
            "product_name": product.name,
            "category": product.category,
            "current_stock": product.current_stock,
            "expiry_date": product.expiry_date,
            "days_until_expiry": days_until_exp,
            "price": float(product.price)
        })
    
    return {
        "count": len(products_data),
        "products": products_data
    }


@router.get("/expired")
def get_expired_products(db: Session = Depends(get_db)):
    """Get all expired products"""
    
    today = datetime.now().date()
    
    expired_products = db.query(Product).filter(
        Product.expiry_date < today
    ).order_by(Product.expiry_date.desc()).all()
    
    products_data = []
    
    for product in expired_products:
        days_expired = (today - product.expiry_date).days
        
        products_data.append({
            "product_id": product.id,
            "product_name": product.name,
            "category": product.category,
            "expiry_date": product.expiry_date,
            "days_expired": days_expired,
            "current_stock": product.current_stock,
            "price": float(product.price)
        })
    
    return {
        "count": len(products_data),
        "products": products_data
    }
