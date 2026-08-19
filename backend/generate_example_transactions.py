from decimal import Decimal

from database import SessionLocal
from models import Product, PurchaseTransaction, SalesTransaction


DEMO_NOTE = "EXAMPLE_GRAPH_DATA"
EXAMPLES = {
    1: {"quantity": 10, "unit_cost": Decimal("40.00"), "unit_price": Decimal("60.00")},
    2: {"quantity": 10, "unit_cost": Decimal("100.00"), "unit_price": Decimal("140.00")},
    3: {"quantity": 10, "unit_cost": Decimal("12.00"), "unit_price": Decimal("20.00")},
}


db = SessionLocal()
try:
    existing = db.query(PurchaseTransaction).filter(PurchaseTransaction.notes == DEMO_NOTE).count()
    if existing:
        print(f"Example data already exists ({existing} purchase records). No changes made.")
    else:
        for product_id, values in EXAMPLES.items():
            product = db.query(Product).filter(Product.id == product_id).first()
            if not product:
                print(f"Skipped missing product {product_id}")
                continue

            quantity = values["quantity"]
            db.add(PurchaseTransaction(
                product_id=product_id,
                quantity=quantity,
                unit_cost=values["unit_cost"],
                total_cost=quantity * values["unit_cost"],
                notes=DEMO_NOTE,
            ))
            db.add(SalesTransaction(
                product_id=product_id,
                quantity=quantity,
                unit_price=values["unit_price"],
                total_revenue=quantity * values["unit_price"],
                notes=DEMO_NOTE,
            ))

        db.commit()
        print("Example purchase and sales data created.")
        print("Products: Rice, Cooking Oil, Biscuits")
        print("Expected realized gross profit: ₹680")
finally:
    db.close()