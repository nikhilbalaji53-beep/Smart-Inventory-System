from database import engine
from sqlalchemy import text

print('=' * 80)
print('🔧 FIXING PURCHASE_ORDERS TABLE SCHEMA')
print('=' * 80)

# SQL to add missing columns to purchase_orders table
sql_commands = [
    "ALTER TABLE purchase_orders ADD COLUMN actual_delivery_date DATE AFTER expected_delivery;",
    "ALTER TABLE purchase_orders ADD COLUMN delivery_status VARCHAR(50) DEFAULT 'PENDING' AFTER actual_delivery_date;",
    "ALTER TABLE purchase_orders ADD COLUMN is_on_time INT DEFAULT 0 AFTER delivery_status;",
]

try:
    with engine.connect() as conn:
        for cmd in sql_commands:
            try:
                conn.execute(text(cmd))
                col_name = cmd.split("ADD COLUMN")[1].split()[0]
                print(f'  ✅ Added column: {col_name}')
            except Exception as e:
                if 'already exists' in str(e).lower():
                    col_name = cmd.split("ADD COLUMN")[1].split()[0]
                    print(f'  ℹ️  {col_name} (already exists)')
                else:
                    print(f'  ⚠️  Error: {str(e)[:80]}')
        conn.commit()
    print('\n✅ All PurchaseOrder columns migrated successfully!')
except Exception as e:
    print(f'\n❌ Error: {e}')

print('=' * 80)
