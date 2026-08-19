from database import engine
from models import Supplier, PurchaseOrder, OrderDelivery, Product
from sqlalchemy.orm import sessionmaker
from sqlalchemy import func

Session = sessionmaker(bind=engine)
session = Session()

print('=' * 80)
print('🧪 SUPPLIER DATABASE COMPREHENSIVE TEST')
print('=' * 80)

# Test 1: Supplier Summary
print('\n📊 TEST 1: SUPPLIER DATABASE SUMMARY')
print('-' * 80)

total_suppliers = session.query(Supplier).count()
approved = session.query(Supplier).filter(Supplier.is_approved == 1).count()
pending = session.query(Supplier).filter(Supplier.is_approved == 0).count()
active = session.query(Supplier).filter(Supplier.is_active == 1).count()

print(f'Total Suppliers: {total_suppliers}')
print(f'  ✅ Approved: {approved} ({100*approved/total_suppliers:.1f}%)')
print(f'  ⏳ Pending: {pending} ({100*pending/total_suppliers:.1f}%)')
print(f'  ✅ Active: {active}')

# Test 2: Supplier Details Sample
print('\n📋 TEST 2: SAMPLE SUPPLIER DETAILS')
print('-' * 80)

suppliers = session.query(Supplier).limit(5).all()
for i, sup in enumerate(suppliers, 1):
    status = '✅ Approved' if sup.is_approved else '⏳ Pending'
    print(f'{i}. {sup.company_name}')
    print(f'   ID: {sup.supplier_id}')
    print(f'   Email: {sup.email}')
    print(f'   Contact: {sup.contact_person}')
    print(f'   Phone: {sup.phone}')
    print(f'   Status: {status}')
    print()

# Test 3: Purchase Orders
print('\n📦 TEST 3: PURCHASE ORDERS')
print('-' * 80)

po_count = session.query(PurchaseOrder).count()
pending_orders = session.query(PurchaseOrder).filter(PurchaseOrder.status == 'PENDING').count()
accepted_orders = session.query(PurchaseOrder).filter(PurchaseOrder.status == 'ACCEPTED').count()
delivered_orders = session.query(PurchaseOrder).filter(PurchaseOrder.status == 'DELIVERED').count()

print(f'Total Purchase Orders: {po_count}')
print(f'  ⏳ PENDING: {pending_orders}')
print(f'  ✅ ACCEPTED: {accepted_orders}')
print(f'  📦 DELIVERED: {delivered_orders}')

if po_count > 0:
    print('\n📋 Sample Orders:')
    orders = session.query(PurchaseOrder).limit(3).all()
    for i, order in enumerate(orders, 1):
        supplier = session.query(Supplier).filter(Supplier.id == order.supplier_id).first()
        product = session.query(Product).filter(Product.id == order.product_id).first()
        supplier_name = supplier.company_name if supplier else "N/A"
        product_name = product.name if product else "N/A"
        print(f'{i}. PO#{order.po_number} | Status: {order.status}')
        print(f'   Supplier: {supplier_name}')
        print(f'   Product: {product_name}')
        print(f'   Qty: {order.quantity_ordered} @ ${order.unit_price}')
        print()

# Test 4: Order Deliveries
print('\n🚚 TEST 4: ORDER DELIVERIES')
print('-' * 80)

delivery_count = session.query(OrderDelivery).count()
print(f'Total Deliveries: {delivery_count}')

if delivery_count > 0:
    print('\n📋 Sample Deliveries:')
    deliveries = session.query(OrderDelivery).limit(3).all()
    for i, delivery in enumerate(deliveries, 1):
        supplier = session.query(Supplier).filter(Supplier.id == delivery.supplier_id).first()
        order = session.query(PurchaseOrder).filter(PurchaseOrder.id == delivery.purchase_order_id).first()
        supplier_name = supplier.company_name if supplier else "N/A"
        po_num = order.po_number if order else "N/A"
        print(f'{i}. Delivery ID: {delivery.id}')
        print(f'   Supplier: {supplier_name}')
        print(f'   PO: {po_num}')
        print(f'   Delivered: {delivery.quantity_delivered} units')
        print(f'   Carrier: {delivery.shipping_carrier}')
        print(f'   Tracking: {delivery.tracking_number}')
        print()

# Test 5: Data Integrity
print('\n✔️ TEST 5: DATA INTEGRITY CHECK')
print('-' * 80)

orphaned_orders = session.query(PurchaseOrder).filter(
    ~PurchaseOrder.supplier_id.in_(session.query(Supplier.id))
).count()

orphaned_deliveries = session.query(OrderDelivery).filter(
    ~OrderDelivery.purchase_order_id.in_(session.query(PurchaseOrder.id))
).count()

print(f'Orphaned Purchase Orders: {orphaned_orders}')
print(f'Orphaned Deliveries: {orphaned_deliveries}')

if orphaned_orders == 0 and orphaned_deliveries == 0:
    print('✅ Database integrity: PASSED')
else:
    print('❌ Database integrity issues detected')

# Test 6: Supplier Relationships
print('\n🔗 TEST 6: SUPPLIER ORDER RELATIONSHIPS')
print('-' * 80)

suppliers_with_orders = session.query(Supplier).filter(
    Supplier.id.in_(session.query(PurchaseOrder.supplier_id).distinct())
).all()

if suppliers_with_orders:
    print(f'Suppliers with Orders: {len(suppliers_with_orders)}')
    print()
    for supplier in suppliers_with_orders[:5]:
        order_count = session.query(PurchaseOrder).filter(PurchaseOrder.supplier_id == supplier.id).count()
        delivery_count = session.query(OrderDelivery).filter(OrderDelivery.supplier_id == supplier.id).count()
        print(f'{supplier.company_name}')
        print(f'  Orders: {order_count} | Deliveries: {delivery_count}')
else:
    print('No supplier-order relationships found')

print('\n' + '=' * 80)
print('✨ SUPPLIER DATABASE TEST COMPLETED ✨')
print('=' * 80)

session.close()
