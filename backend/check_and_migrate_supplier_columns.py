from database import engine
from sqlalchemy import text, inspect

print('=' * 80)
print('🔍 CHECKING SUPPLIER TABLE STRUCTURE')
print('=' * 80)

inspector = inspect(engine)
columns = inspector.get_columns('suppliers')

print(f'\nTotal Columns in SUPPLIERS table: {len(columns)}\n')

print('Current Columns:')
print('-' * 80)
for col in columns:
    col_type = str(col['type'])
    nullable = 'NULL' if col['nullable'] else 'NOT NULL'
    print(f'  • {col["name"]:<35} {col_type:<30} {nullable}')

print('\n' + '=' * 80)

# Check if new columns exist
new_columns = [
    'supply_category', 'lead_time_days', 'minimum_order_quantity',
    'payment_terms', 'quality_rating', 'on_time_delivery_rate',
    'last_delivery_date', 'total_orders', 'completed_orders',
    'avg_quality_score', 'price_competitiveness', 'communication_rating',
    'reliability_score', 'bank_name', 'bank_account', 'ifsc_code'
]

existing_cols = [col['name'] for col in columns]
missing_cols = [col for col in new_columns if col not in existing_cols]

if missing_cols:
    print(f'\n⚠️  Missing columns ({len(missing_cols)}):')
    for col in missing_cols:
        print(f'  • {col}')
    
    print('\n🔧 Adding missing columns to SUPPLIERS table...')
    
    # SQL to add missing columns
    sql_commands = [
        "ALTER TABLE suppliers ADD COLUMN supply_category VARCHAR(100) AFTER is_active;",
        "ALTER TABLE suppliers ADD COLUMN lead_time_days INT DEFAULT 7 AFTER supply_category;",
        "ALTER TABLE suppliers ADD COLUMN minimum_order_quantity INT DEFAULT 1 AFTER lead_time_days;",
        "ALTER TABLE suppliers ADD COLUMN payment_terms VARCHAR(100) AFTER minimum_order_quantity;",
        "ALTER TABLE suppliers ADD COLUMN quality_rating DECIMAL(3,2) DEFAULT 0 AFTER payment_terms;",
        "ALTER TABLE suppliers ADD COLUMN on_time_delivery_rate DECIMAL(5,2) DEFAULT 0 AFTER quality_rating;",
        "ALTER TABLE suppliers ADD COLUMN last_delivery_date TIMESTAMP AFTER on_time_delivery_rate;",
        "ALTER TABLE suppliers ADD COLUMN total_orders INT DEFAULT 0 AFTER last_delivery_date;",
        "ALTER TABLE suppliers ADD COLUMN completed_orders INT DEFAULT 0 AFTER total_orders;",
        "ALTER TABLE suppliers ADD COLUMN avg_quality_score DECIMAL(3,2) DEFAULT 0 AFTER completed_orders;",
        "ALTER TABLE suppliers ADD COLUMN price_competitiveness VARCHAR(50) AFTER avg_quality_score;",
        "ALTER TABLE suppliers ADD COLUMN communication_rating DECIMAL(3,2) DEFAULT 0 AFTER price_competitiveness;",
        "ALTER TABLE suppliers ADD COLUMN reliability_score DECIMAL(3,2) DEFAULT 0 AFTER communication_rating;",
        "ALTER TABLE suppliers ADD COLUMN bank_name VARCHAR(100) AFTER reliability_score;",
        "ALTER TABLE suppliers ADD COLUMN bank_account VARCHAR(50) AFTER bank_name;",
        "ALTER TABLE suppliers ADD COLUMN ifsc_code VARCHAR(20) AFTER bank_account;",
    ]
    
    try:
        with engine.connect() as conn:
            for cmd in sql_commands:
                try:
                    conn.execute(text(cmd))
                    print(f'  ✅ {cmd.split("ADD COLUMN")[1].split()[0]}')
                except Exception as e:
                    if 'already exists' in str(e).lower():
                        print(f'  ℹ️  {cmd.split("ADD COLUMN")[1].split()[0]} (already exists)')
                    else:
                        print(f'  ❌ Error: {str(e)[:50]}')
            conn.commit()
        print('\n✅ All columns added successfully!')
    except Exception as e:
        print(f'\n❌ Error adding columns: {e}')
else:
    print(f'\n✅ All enhanced columns present in SUPPLIERS table!')

print('\n' + '=' * 80)
