from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from database import get_db
from models import Product, ProductSupplierMapping, PurchaseOrder, PurchaseTransaction, SalesTransaction
from prediction import predict_demand

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)


@router.get("/")
def dashboard(
    db: Session = Depends(get_db)
):

    products = db.query(Product).all()

    total_products = len(products)

    total_stock = sum(
        p.current_stock
        for p in products
    )

    low_stock = sum(
        1
        for p in products
        if p.current_stock <= p.minimum_stock
    )

    # Expiry metrics
    today = datetime.now().date()
    expiry_soon = sum(
        1
        for p in products
        if p.expiry_date and (p.expiry_date - today).days <= 7 and (p.expiry_date - today).days > 0
    )
    
    expired = sum(
        1
        for p in products
        if p.expiry_date and (p.expiry_date - today).days < 0
    )

    predicted_demand = 0

    for product in products:
        try:
            forecast = predict_demand(
                product.id,
                7
            )

            predicted_demand += sum(
                x["predicted_units"]
                for x in forecast
            )
        except:
            pass

    return {
        "total_products": total_products,
        "total_stock": total_stock,
        "low_stock_products": low_stock,
        "expiring_soon_products": expiry_soon,
        "expired_products": expired,
        "predicted_7_day_demand": round(predicted_demand, 2)
    }


@router.get("/summary")
def dashboard_summary(db: Session = Depends(get_db)):
    """Detailed dashboard summary with all metrics"""
    
    products = db.query(Product).all()
    today = datetime.now().date()
    
    # Basic metrics
    total_products = len(products)
    total_stock = sum(p.current_stock for p in products)
    total_value = sum(float(p.price) * p.current_stock for p in products)

    # Estimate gross profit from current inventory using the preferred supplier
    # cost, then the latest purchase-order cost when no mapping exists.
    mapping_costs = {}
    for row in db.query(ProductSupplierMapping).filter(
        ProductSupplierMapping.is_active == 1
    ).order_by(
        ProductSupplierMapping.is_preferred.desc(),
        ProductSupplierMapping.updated_at.desc()
    ).all():
        mapping_costs.setdefault(row.product_id, (float(row.unit_cost), "supplier mapping"))

    purchase_costs = {}
    for order in db.query(PurchaseOrder).order_by(PurchaseOrder.order_date.desc()).all():
        if order.product_id not in purchase_costs:
            purchase_costs[order.product_id] = (float(order.unit_price), "purchase order")

    purchase_transactions = db.query(PurchaseTransaction).all()
    sales_transactions = db.query(SalesTransaction).all()
    purchase_totals = {}
    for transaction in purchase_transactions:
        entry = purchase_totals.setdefault(transaction.product_id, {"quantity": 0, "cost": 0.0})
        entry["quantity"] += transaction.quantity
        entry["cost"] += float(transaction.total_cost)

    sales_totals = {}
    for transaction in sales_transactions:
        entry = sales_totals.setdefault(transaction.product_id, {"quantity": 0, "revenue": 0.0})
        entry["quantity"] += transaction.quantity
        entry["revenue"] += float(transaction.total_revenue)

    product_names = {product.id: product.name for product in products}
    transaction_history = [
        {
            "id": transaction.id,
            "type": "PURCHASE",
            "product_id": transaction.product_id,
            "product_name": product_names.get(transaction.product_id, "Unknown product"),
            "quantity": transaction.quantity,
            "unit_amount": round(float(transaction.unit_cost), 2),
            "total_amount": round(float(transaction.total_cost), 2),
            "transaction_date": transaction.transaction_date,
            "notes": transaction.notes,
        }
        for transaction in purchase_transactions
    ] + [
        {
            "id": transaction.id,
            "type": "SALE",
            "product_id": transaction.product_id,
            "product_name": product_names.get(transaction.product_id, "Unknown product"),
            "quantity": transaction.quantity,
            "unit_amount": round(float(transaction.unit_price), 2),
            "total_amount": round(float(transaction.total_revenue), 2),
            "transaction_date": transaction.transaction_date,
            "notes": transaction.notes,
        }
        for transaction in sales_transactions
    ]
    transaction_history.sort(key=lambda item: item["transaction_date"] or datetime.min, reverse=True)

    inventory_cost = 0.0
    costed_products = 0
    product_profit_loss = []
    for product in products:
        cost_data = mapping_costs.get(product.id, purchase_costs.get(product.id))
        purchase_data = purchase_totals.get(product.id)
        sales_data = sales_totals.get(product.id)
        average_purchase_cost = (
            purchase_data["cost"] / purchase_data["quantity"]
            if purchase_data and purchase_data["quantity"]
            else None
        )
        if average_purchase_cost is not None:
            cost_data = (average_purchase_cost, "purchase transactions")

        if cost_data is not None:
            unit_cost, cost_source = cost_data
            product_cost = unit_cost * product.current_stock
            product_value = float(product.price) * product.current_stock
            realized_revenue = sales_data["revenue"] if sales_data else 0.0
            realized_cost = average_purchase_cost * sales_data["quantity"] if average_purchase_cost and sales_data else 0.0
            product_profit = realized_revenue - realized_cost if sales_data else product_value - product_cost
            inventory_cost += product_cost
            costed_products += 1
            product_profit_loss.append({
                "product_id": product.id,
                "product_name": product.name,
                "current_stock": product.current_stock,
                "selling_price": round(float(product.price), 2),
                "unit_cost": round(unit_cost, 2),
                "cost_source": cost_source,
                "sales_value": round(product_value, 2),
                "inventory_cost": round(product_cost, 2),
                "profit_loss": round(product_profit, 2),
                "sales_quantity": sales_data["quantity"] if sales_data else 0,
                "realized_revenue": round(realized_revenue, 2),
                "realized_cost": round(realized_cost, 2),
                "basis": "realized sales" if sales_data else "current inventory estimate",
                "margin_percent": round((product_profit / realized_revenue) * 100, 2) if sales_data and realized_revenue else round((product_profit / product_value) * 100, 2) if product_value else 0,
                "status": "PROFIT" if product_profit > 0 else "LOSS" if product_profit < 0 else "BREAK-EVEN"
            })
        else:
            product_profit_loss.append({
                "product_id": product.id,
                "product_name": product.name,
                "current_stock": product.current_stock,
                "selling_price": round(float(product.price), 2),
                "unit_cost": None,
                "cost_source": None,
                "sales_value": round(float(product.price) * product.current_stock, 2),
                "inventory_cost": None,
                "profit_loss": None,
                "sales_quantity": sales_data["quantity"] if sales_data else 0,
                "realized_revenue": round(sales_data["revenue"], 2) if sales_data else 0,
                "realized_cost": None,
                "basis": "sales recorded but purchase cost unavailable" if sales_data else "cost unavailable",
                "margin_percent": None,
                "status": "COST UNAVAILABLE"
            })

    estimated_profit = total_value - inventory_cost
    cost_coverage = round((costed_products / total_products) * 100, 2) if total_products else 0
    
    # Stock alerts
    low_stock_products = [
        {
            "id": p.id,
            "name": p.name,
            "current_stock": p.current_stock,
            "minimum_stock": p.minimum_stock,
            "deficit": p.minimum_stock - p.current_stock
        }
        for p in products
        if p.current_stock <= p.minimum_stock
    ]
    
    # Expiry alerts
    expiry_alerts = []
    for p in products:
        if not p.expiry_date:
            continue
        
        days_until_exp = (p.expiry_date - today).days
        
        if days_until_exp <= 7:
            status = "EXPIRED" if days_until_exp < 0 else "EXPIRING_SOON"
            severity = "CRITICAL" if days_until_exp <= 0 else "WARNING"
            
            expiry_alerts.append({
                "id": p.id,
                "name": p.name,
                "expiry_date": p.expiry_date,
                "days_until_expiry": days_until_exp,
                "current_stock": p.current_stock,
                "status": status,
                "severity": severity
            })
    
    # Prediction metrics
    predicted_demand = 0
    for product in products:
        try:
            forecast = predict_demand(product.id, 7)
            predicted_demand += sum(x["predicted_units"] for x in forecast)
        except:
            pass
    
    return {
        "inventory_metrics": {
            "total_products": total_products,
            "total_stock": total_stock,
            "inventory_value": round(total_value, 2)
        },
        "profit_loss": {
            "potential_sales_value": round(total_value, 2),
            "inventory_cost": round(inventory_cost, 2),
            "estimated_gross_profit": round(estimated_profit, 2) if costed_products else None,
            "estimated_margin_percent": round((estimated_profit / total_value) * 100, 2) if costed_products and total_value else None,
            "costed_products": costed_products,
            "cost_coverage_percent": cost_coverage,
            "products": product_profit_loss,
            "transactions": {
                "total_purchases": len(purchase_transactions),
                "total_purchase_cost": round(sum(float(item.total_cost) for item in purchase_transactions), 2),
                "total_sales": len(sales_transactions),
                "total_sales_revenue": round(sum(float(item.total_revenue) for item in sales_transactions), 2),
                "history": transaction_history[:50],
            },
            "note": "Estimate based on product prices and supplier purchase costs; sales revenue is not tracked yet."
        },
        "alerts": {
            "low_stock_count": len(low_stock_products),
            "low_stock_products": low_stock_products,
            "expiry_alerts_count": len(expiry_alerts),
            "expiry_alerts": expiry_alerts
        },
        "demand_forecast": {
            "predicted_7_day_demand": round(predicted_demand, 2)
        }
    }