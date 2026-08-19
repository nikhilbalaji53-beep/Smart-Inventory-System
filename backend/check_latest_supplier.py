from database import engine
from models import Supplier
from sqlalchemy.orm import sessionmaker
from sqlalchemy import desc

Session = sessionmaker(bind=engine)
session = Session()

# Get the most recent supplier
recent = session.query(Supplier).order_by(desc(Supplier.created_at)).first()

if recent:
    print('=' * 80)
    print('✅ LATEST REGISTERED SUPPLIER')
    print('=' * 80)
    print(f'Supplier ID: {recent.supplier_id}')
    print(f'Company: {recent.company_name}')
    print(f'Email: {recent.email}')
    print(f'Contact: {recent.contact_person}')
    print(f'Phone: {recent.phone}')
    print(f'Address: {recent.address}')
    print(f'GST: {recent.gst_number}')
    approved_status = 'Yes' if recent.is_approved else 'No'
    active_status = 'Yes' if recent.is_active else 'No'
    print(f'Approved: {approved_status}')
    print(f'Active: {active_status}')
    print(f'Created: {recent.created_at}')
    print('=' * 80)
else:
    print('No suppliers found')

session.close()
