from sqlalchemy import Column, Integer, String, Numeric, Date, TIMESTAMP, Text, Boolean, ForeignKey
from sqlalchemy.sql import func

from database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    category = Column(String(100))
    price = Column(Numeric(10, 2), nullable=False)
    current_stock = Column(Integer, default=0, nullable=False)
    minimum_stock = Column(Integer, default=10, nullable=False)
    supplier = Column(String(150))
    expiry_date = Column(Date)
    created_at = Column(
        TIMESTAMP,
        server_default=func.current_timestamp() 
    )


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    is_admin = Column(Integer, default=0, nullable=False)
    created_at = Column(
        TIMESTAMP,
        server_default=func.current_timestamp()
    )


class Supplier(Base):
    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True, index=True)
    supplier_id = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    company_name = Column(String(150), nullable=False)
    contact_person = Column(String(150))
    hashed_password = Column(String(255), nullable=False)
    phone = Column(String(20))
    address = Column(Text)
    gst_number = Column(String(50))
    is_approved = Column(Integer, default=0, nullable=False)  # 0 = pending, 1 = approved
    is_active = Column(Integer, default=1, nullable=False)
    
    # Supplier Master Data Fields
    supply_category = Column(String(100))  # Electronics, Food, Pharma, etc.
    lead_time_days = Column(Integer, default=7)  # Average delivery time
    minimum_order_quantity = Column(Integer, default=1)
    payment_terms = Column(String(100))  # Net 30, COD, etc.
    quality_rating = Column(Numeric(3, 2), default=0)  # 0-5 star rating
    on_time_delivery_rate = Column(Numeric(5, 2), default=0)  # Percentage 0-100
    last_delivery_date = Column(TIMESTAMP)
    total_orders = Column(Integer, default=0)
    completed_orders = Column(Integer, default=0)
    
    # Performance Metrics
    avg_quality_score = Column(Numeric(3, 2), default=0)
    price_competitiveness = Column(String(50))  # Low, Medium, High
    communication_rating = Column(Numeric(3, 2), default=0)
    reliability_score = Column(Numeric(3, 2), default=0)
    
    # Bank & Payment Details
    bank_name = Column(String(100))
    bank_account = Column(String(50))
    ifsc_code = Column(String(20))
    
    created_at = Column(
        TIMESTAMP,
        server_default=func.current_timestamp()
    )
    updated_at = Column(
        TIMESTAMP,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp()
    )


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    alert_type = Column(String(50), nullable=False, index=True)  # LOW_STOCK, EXPIRY, DEMAND, etc.
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    severity = Column(String(20), nullable=False)  # CRITICAL, WARNING, INFO
    is_read = Column(Boolean, default=False, index=True)
    created_at = Column(
        TIMESTAMP,
        server_default=func.current_timestamp(),
        index=True
    )
    updated_at = Column(
        TIMESTAMP,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp()
    )


class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"

    id = Column(Integer, primary_key=True, index=True)
    po_number = Column(String(50), unique=True, nullable=False, index=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity_ordered = Column(Integer, nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    total_amount = Column(Numeric(12, 2), nullable=False)
    status = Column(String(50), default="PENDING", index=True)  # PENDING, ACCEPTED, DELIVERED, CANCELLED
    order_date = Column(TIMESTAMP, server_default=func.current_timestamp(), index=True)
    expected_delivery = Column(Date)
    actual_delivery_date = Column(Date)  # Tracks actual delivery date
    delivery_status = Column(String(50), default="PENDING")  # PENDING, DELIVERED, LATE, CANCELLED
    is_on_time = Column(Integer, default=0)  # 1 if delivered on time, 0 if late
    notes = Column(Text)
    created_at = Column(
        TIMESTAMP,
        server_default=func.current_timestamp()
    )
    updated_at = Column(
        TIMESTAMP,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp()
    )


class OrderDelivery(Base):
    __tablename__ = "order_deliveries"

    id = Column(Integer, primary_key=True, index=True)
    purchase_order_id = Column(Integer, ForeignKey("purchase_orders.id"), nullable=False, index=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False, index=True)
    quantity_delivered = Column(Integer, nullable=False)
    delivery_date = Column(TIMESTAMP, server_default=func.current_timestamp())
    delivery_reference = Column(String(100))
    shipping_carrier = Column(String(100))
    tracking_number = Column(String(100))
    notes = Column(Text)
    created_at = Column(
        TIMESTAMP,
        server_default=func.current_timestamp()
    )
    updated_at = Column(
        TIMESTAMP,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp()
    )


class ProductSupplierMapping(Base):
    """Maps products to multiple suppliers for sourcing flexibility"""
    __tablename__ = "product_supplier_mapping"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False, index=True)
    supplier_sku = Column(String(100))  # Supplier's SKU for this product
    unit_cost = Column(Numeric(10, 2), nullable=False)  # Cost from this supplier
    lead_time = Column(Integer)  # Days to deliver
    minimum_order = Column(Integer, default=1)
    is_preferred = Column(Integer, default=0)  # Primary supplier flag
    is_active = Column(Integer, default=1)
    quality_score = Column(Numeric(3, 2), default=0)  # Historical quality 0-5
    last_purchase_date = Column(TIMESTAMP)
    last_purchase_price = Column(Numeric(10, 2))
    total_purchases = Column(Integer, default=0)
    notes = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())


class SupplierPerformance(Base):
    """Tracks supplier performance metrics over time"""
    __tablename__ = "supplier_performance"

    id = Column(Integer, primary_key=True, index=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False, unique=True, index=True)
    total_orders = Column(Integer, default=0)
    completed_orders = Column(Integer, default=0)
    cancelled_orders = Column(Integer, default=0)
    on_time_deliveries = Column(Integer, default=0)
    late_deliveries = Column(Integer, default=0)
    on_time_percentage = Column(Numeric(5, 2), default=0)  # 0-100
    average_lead_time = Column(Integer, default=0)  # Days
    quality_issues = Column(Integer, default=0)
    quality_score = Column(Numeric(3, 2), default=5)  # 0-5
    price_competitiveness = Column(Numeric(3, 2), default=3)  # 0-5
    communication_rating = Column(Numeric(3, 2), default=5)  # 0-5
    overall_rating = Column(Numeric(3, 2), default=3)  # 0-5
    last_evaluation_date = Column(TIMESTAMP)
    total_amount_spent = Column(Numeric(15, 2), default=0)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())


class ReorderDecision(Base):
    """Automated reorder decisions based on stock prediction and supplier performance"""
    __tablename__ = "reorder_decisions"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False, index=True)
    current_stock = Column(Integer, nullable=False)
    predicted_usage = Column(Integer)  # 7-day forecast
    reorder_quantity = Column(Integer, nullable=False)
    reorder_point = Column(Integer, nullable=False)
    decision_date = Column(TIMESTAMP, server_default=func.current_timestamp(), index=True)
    decision_status = Column(String(50), default="PENDING")  # PENDING, APPROVED, PO_CREATED, CANCELLED
    priority = Column(String(50))  # CRITICAL, HIGH, MEDIUM, LOW
    reason = Column(Text)  # Why reorder was triggered
    estimated_lead_time = Column(Integer)  # Days
    estimated_arrival_date = Column(Date)
    po_number = Column(String(50), ForeignKey("purchase_orders.po_number"))  # Link to PO if created
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())


class SupplierAlert(Base):
    """Automated alerts for supplier issues and actions needed"""
    __tablename__ = "supplier_alerts"

    id = Column(Integer, primary_key=True, index=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False, index=True)
    alert_type = Column(String(100), nullable=False)  # QUALITY_ISSUE, LATE_DELIVERY, APPROVAL_PENDING, etc.
    severity = Column(String(20), nullable=False)  # CRITICAL, WARNING, INFO
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    related_po = Column(String(50), ForeignKey("purchase_orders.po_number"))
    is_resolved = Column(Integer, default=0)
    resolution_date = Column(TIMESTAMP)
    notes = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp(), index=True)
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())


class PurchaseTransaction(Base):
    __tablename__ = "purchase_transactions"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=True, index=True)
    quantity = Column(Integer, nullable=False)
    unit_cost = Column(Numeric(10, 2), nullable=False)
    total_cost = Column(Numeric(12, 2), nullable=False)
    transaction_date = Column(TIMESTAMP, server_default=func.current_timestamp(), index=True)
    notes = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())


class SalesTransaction(Base):
    __tablename__ = "sales_transactions"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    total_revenue = Column(Numeric(12, 2), nullable=False)
    transaction_date = Column(TIMESTAMP, server_default=func.current_timestamp(), index=True)
    notes = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())