from database import engine
from models import Base, Supplier, ProductSupplierMapping, SupplierPerformance, ReorderDecision, SupplierAlert, PurchaseOrder
from sqlalchemy import inspect

print('=' * 80)
print('🔄 CREATING ENHANCED DATABASE SCHEMA')
print('=' * 80)

# Create all tables
Base.metadata.create_all(bind=engine)

print('\n✅ Database tables created/updated successfully')

# Display all tables
inspector = inspect(engine)
tables = inspector.get_table_names()

print(f'\nTotal Tables: {len(tables)}')
print()

for table_name in sorted(tables):
    columns = inspector.get_columns(table_name)
    print(f'📋 {table_name.upper()}')
    print('-' * 80)
    for col in columns:
        col_type = str(col['type'])
        nullable = 'NULL' if col['nullable'] else 'NOT NULL'
        print(f'  • {col["name"]:<30} {col_type:<30} {nullable}')
    print()

print('=' * 80)
print('✨ ENHANCED SUPPLIER DATABASE READY')
print('=' * 80)
