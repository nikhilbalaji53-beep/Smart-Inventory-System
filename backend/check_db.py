from database import SessionLocal
from sqlalchemy import text

db = SessionLocal()

print('\n' + '='*60)
print('📊 DATABASE CONNECTION SUCCESSFUL!')
print('='*60)

print('\n🔹 PRODUCTS TABLE STRUCTURE:')
print('-' * 60)
result = db.execute(text('DESCRIBE products'))
for row in result:
    print(f'  {row[0]:<25} {row[1]:<20}')

print('\n🔹 USERS TABLE STRUCTURE:')
print('-' * 60)
result = db.execute(text('DESCRIBE users'))
for row in result:
    print(f'  {row[0]:<25} {row[1]:<20}')

print('\n🔹 TABLE RECORD COUNTS:')
print('-' * 60)
products_count = db.execute(text('SELECT COUNT(*) FROM products')).scalar()
users_count = db.execute(text('SELECT COUNT(*) FROM users')).scalar()
print(f'  Products: {products_count} records')
print(f'  Users:    {users_count} records')

db.close()
print('\n' + '='*60)
print('✅ Database is fully initialized and ready to use!')
print('='*60 + '\n')
