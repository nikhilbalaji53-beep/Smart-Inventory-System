from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from models import Product, User
from prediction import predict_demand
from notifications import create_notification


router = APIRouter(
    prefix="/alerts",
    tags=["Alerts"]
)


@router.get("/")
def get_alerts(
    db: Session = Depends(get_db)
):

    products = db.query(
        Product
    ).order_by(
        Product.id
    ).all()


    alerts = []


    for product in products:

        reasons = []


        # Rule 1: stock below minimum
        if product.current_stock <= product.minimum_stock:

            reasons.append(
                "LOW_STOCK"
            )


        # Rule 2: predicted demand greater than stock

        try:

            forecast = predict_demand(
                product.id,
                7
            )

            predicted_demand = sum(
                item["predicted_units"]
                for item in forecast
            )

        except:

            predicted_demand = 0


        if predicted_demand > product.current_stock:

            reasons.append(
                "DEMAND_EXCEEDS_STOCK"
            )


        # Create alert

        if reasons:

            severity = (
                "CRITICAL"
                if "LOW_STOCK" in reasons
                else "WARNING"
            )


            alerts.append({

                "product_id":
                    product.id,

                "product_name":
                    product.name,

                "current_stock":
                    product.current_stock,

                "minimum_stock":
                    product.minimum_stock,

                "predicted_7_day_demand":
                    round(
                        predicted_demand,
                        2
                    ),

                "severity":
                    severity,

                "reasons":
                    reasons,

                "recommended_reorder_qty":
                    calculate_reorder_quantity(
                        product,
                        predicted_demand
                    )
            })

    # Create notifications for critical alerts
    try:
        # Get or create admin user for notifications
        admin_user = db.query(User).filter(User.is_admin == 1).first()
        
        if admin_user:
            for alert in alerts:
                if alert["severity"] == "CRITICAL":
                    # Create notification for critical alerts
                    title = f"🚨 CRITICAL: {alert['product_name']}"
                    message = f"Stock: {alert['current_stock']} units (Min: {alert['minimum_stock']}). {', '.join(alert['reasons'])}"
                    
                    create_notification(
                        db,
                        user_id=admin_user.id,
                        product_id=alert["product_id"],
                        alert_type="LOW_STOCK" if "LOW_STOCK" in alert["reasons"] else "DEMAND",
                        title=title,
                        message=message,
                        severity="CRITICAL"
                    )
    except Exception as e:
        # Log error but don't fail the request
        print(f"Error creating notifications: {e}")


    return {

        "count":
            len(alerts),

        "alerts":
            alerts

    }


def calculate_reorder_quantity(product, predicted_demand):
    """
    Calculate recommended reorder quantity based on:
    - Predicted demand for next 7 days
    - Current stock level
    - Minimum stock threshold
    - Safety stock (20% buffer)
    """
    lead_time_days = 7  # Assume 7 day lead time from supplier
    safety_stock_buffer = 0.2  # 20% buffer for unexpected demand spikes

    # Calculate total demand during lead time
    total_demand_needed = predicted_demand * (lead_time_days / 7)

    # Add safety stock
    demand_with_safety = total_demand_needed * (1 + safety_stock_buffer)

    # Calculate reorder quantity
    reorder_qty = max(
        0,
        int(demand_with_safety + product.minimum_stock - product.current_stock)
    )

    return reorder_qty