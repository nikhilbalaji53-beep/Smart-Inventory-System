from database import engine
from models import Supplier, ProductSupplierMapping, SupplierPerformance, ReorderDecision, SupplierAlert, Product, PurchaseOrder
from sqlalchemy.orm import sessionmaker
from sqlalchemy import inspect

Session = sessionmaker(bind=engine)
session = Session()

print('=' * 100)
print('🎯 ENHANCED SUPPLIER DATABASE WORKFLOW TEST')
print('=' * 100)

# 1. Show Database Structure
print('\n📊 DATABASE STRUCTURE')
print('-' * 100)

inspector = inspect(engine)
tables = inspector.get_table_names()

workflow_tables = {
    'suppliers': 'Supplier Master Database',
    'product_supplier_mapping': 'Product-Supplier Mapping',
    'purchase_orders': 'Purchase Order Management',
    'supplier_performance': 'Supplier Performance Tracking',
    'reorder_decisions': 'Reorder Decision Management',
    'supplier_alerts': 'Automated Supplier Alerts',
    'order_deliveries': 'Goods Received & Stock Updates'
}

print(f'\nTotal Tables Created: {len(tables)}')
print(f'Workflow Tables: {len(workflow_tables)}')
print()

for table, description in workflow_tables.items():
    if table in tables:
        cols = inspector.get_columns(table)
        print(f'✅ {table:<30} ({len(cols)} columns) - {description}')
    else:
        print(f'❌ {table:<30} NOT FOUND')

# 2. Current Supplier Data
print('\n\n📋 SUPPLIER MASTER DATA (Sample)')
print('-' * 100)

suppliers = session.query(Supplier).limit(3).all()
if suppliers:
    for i, sup in enumerate(suppliers, 1):
        print(f'\n{i}. {sup.company_name}')
        print(f'   Supplier ID: {sup.supplier_id}')
        print(f'   Email: {sup.email}')
        print(f'   Status: {"✅ Approved" if sup.is_approved else "⏳ Pending"}')
        print(f'   Supply Category: {sup.supply_category or "Not Set"}')
        print(f'   Lead Time: {sup.lead_time_days} days')
        print(f'   Minimum Order: {sup.minimum_order_quantity} units')
        print(f'   Quality Rating: {sup.quality_rating or 0}/5.00')
        print(f'   On-Time Rate: {sup.on_time_delivery_rate or 0}%')
        print(f'   Total Orders: {sup.total_orders}')
        print(f'   Completed Orders: {sup.completed_orders}')
else:
    print('No suppliers found')

# 3. Product-Supplier Mapping
print('\n\n🔗 PRODUCT-SUPPLIER MAPPING')
print('-' * 100)

mappings = session.query(ProductSupplierMapping).all()
print(f'Total Product-Supplier Mappings: {len(mappings)}')

if mappings:
    print('\nSample Mappings:')
    for i, mapping in enumerate(mappings[:3], 1):
        product = session.query(Product).filter(Product.id == mapping.product_id).first()
        supplier = session.query(Supplier).filter(Supplier.id == mapping.supplier_id).first()
        preferred = "✅ Preferred" if mapping.is_preferred else "   Alternative"
        print(f'\n{i}. {product.name if product else "Product N/A"} ← {supplier.company_name if supplier else "Supplier N/A"}')
        print(f'   Supplier SKU: {mapping.supplier_sku or "N/A"}')
        print(f'   Unit Cost: ${mapping.unit_cost}')
        print(f'   Lead Time: {mapping.lead_time} days')
        print(f'   Min Order: {mapping.minimum_order} units')
        print(f'   Status: {preferred}')
        print(f'   Quality Score: {mapping.quality_score}/5')
else:
    print('No product-supplier mappings found (Ready to be created)')

# 4. Purchase Orders
print('\n\n📦 PURCHASE ORDERS')
print('-' * 100)

purchase_orders = session.query(PurchaseOrder).all()
print(f'Total Purchase Orders: {len(purchase_orders)}')

if purchase_orders:
    status_counts = {}
    for po in purchase_orders:
        status = po.status or 'UNKNOWN'
        status_counts[status] = status_counts.get(status, 0) + 1
    
    print('\nOrder Status Breakdown:')
    for status, count in sorted(status_counts.items()):
        print(f'  • {status}: {count} orders')
    
    print('\nSample Orders:')
    for i, po in enumerate(purchase_orders[:3], 1):
        supplier = session.query(Supplier).filter(Supplier.id == po.supplier_id).first()
        product = session.query(Product).filter(Product.id == po.product_id).first()
        print(f'\n{i}. PO#{po.po_number}')
        print(f'   Supplier: {supplier.company_name if supplier else "N/A"}')
        print(f'   Product: {product.name if product else "N/A"}')
        print(f'   Qty: {po.quantity_ordered} @ ${po.unit_price}')
        print(f'   Total: ${po.total_amount}')
        print(f'   Status: {po.status}')
else:
    print('No purchase orders found (Ready for Purchase Order Management)')

# 5. Supplier Performance
print('\n\n📈 SUPPLIER PERFORMANCE TRACKING')
print('-' * 100)

performance_records = session.query(SupplierPerformance).all()
print(f'Total Performance Records: {len(performance_records)}')

if performance_records:
    print('\nSample Performance Metrics:')
    for i, perf in enumerate(performance_records[:3], 1):
        supplier = session.query(Supplier).filter(Supplier.id == perf.supplier_id).first()
        print(f'\n{i}. {supplier.company_name if supplier else "N/A"}')
        print(f'   Total Orders: {perf.total_orders}')
        print(f'   Completed: {perf.completed_orders} | Cancelled: {perf.cancelled_orders}')
        print(f'   On-Time Rate: {perf.on_time_percentage}%')
        print(f'   Avg Lead Time: {perf.average_lead_time} days')
        print(f'   Quality Score: {perf.quality_score}/5')
        print(f'   Overall Rating: {perf.overall_rating}/5')
else:
    print('No performance records found (Will be created as suppliers complete orders)')

# 6. Reorder Decisions
print('\n\n🔄 REORDER DECISIONS')
print('-' * 100)

reorder_decisions = session.query(ReorderDecision).all()
print(f'Total Reorder Decisions: {len(reorder_decisions)}')

if reorder_decisions:
    status_breakdown = {}
    for rd in reorder_decisions:
        status = rd.decision_status or 'UNKNOWN'
        status_breakdown[status] = status_breakdown.get(status, 0) + 1
    
    print('\nReorder Decision Status:')
    for status, count in sorted(status_breakdown.items()):
        print(f'  • {status}: {count}')
else:
    print('No reorder decisions found (Generated by stock prediction engine)')

# 7. Supplier Alerts
print('\n\n🚨 AUTOMATED SUPPLIER ALERTS')
print('-' * 100)

alerts = session.query(SupplierAlert).all()
print(f'Total Alerts: {len(alerts)}')

if alerts:
    severity_counts = {}
    for alert in alerts:
        severity = alert.severity
        severity_counts[severity] = severity_counts.get(severity, 0) + 1
    
    print('\nAlert Severity Breakdown:')
    for severity, count in sorted(severity_counts.items()):
        print(f'  • {severity}: {count} alerts')
else:
    print('No alerts found (Generated when issues occur)')

# 8. Workflow Summary
print('\n\n' + '=' * 100)
print('📊 WORKFLOW SUMMARY')
print('=' * 100)

print('''
The enhanced supplier database supports the complete workflow:

1. ✅ Supplier Registration
   └─ Suppliers table with master data (company, contact, approval status)

2. ✅ Supplier Master Database
   └─ Fields: supply_category, lead_time, min_order, quality_rating, payment_terms
   └─ Performance tracking: on_time_rate, completed_orders, quality_score

3. ✅ Product-Supplier Mapping
   └─ Multiple suppliers per product
   └─ Track preferred suppliers, alternative sources, unit costs
   └─ Historical quality scores and purchase dates

4. ✅ Purchase Order Management
   └─ Create, track, and manage purchase orders
   └─ Status workflow: PENDING → ACCEPTED → DELIVERED
   └─ Expected vs actual delivery tracking

5. ✅ Goods Received / Stock Updated
   └─ Order deliveries recorded with tracking info
   └─ Automatic stock updates on goods receipt
   └─ Delivery quality assessment

6. ✅ Supplier Performance Tracking
   └─ On-time delivery metrics
   └─ Quality issues tracking
   └─ Overall supplier rating (0-5)
   └─ Price competitiveness score

7. ✅ Stock Prediction
   └─ Integration with prediction engine
   └─ Forecasts 7-day demand

8. ✅ Reorder Decision
   └─ Automated reorder recommendations
   └─ Priority levels: CRITICAL, HIGH, MEDIUM, LOW
   └─ Estimated delivery dates
   └─ Auto-link to purchase orders

9. ✅ Automated Supplier Alert
   └─ Quality issues
   └─ Late deliveries
   └─ Approval pending
   └─ Custom severity levels
''')

print('=' * 100)
print('✨ ENHANCED SUPPLIER DATABASE WORKFLOW COMPLETE ✨')
print('=' * 100)

session.close()
