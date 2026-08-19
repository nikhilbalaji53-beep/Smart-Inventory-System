import requests
import json
from datetime import datetime
import random
import string

BASE_URL = 'http://localhost:8000'

print('=' * 80)
print('🧪 SUPPLIER REGISTRATION COMPREHENSIVE TEST')
print('=' * 80)

def generate_test_data():
    """Generate unique test data"""
    timestamp = int(datetime.now().timestamp())
    suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=5))
    return {
        'supplier_id': f'sup_test_{timestamp}_{suffix}',
        'email': f'supplier_{timestamp}_{suffix}@example.com',
        'company_name': f'Test Company {timestamp}',
        'contact_person': f'Contact Person {suffix}',
        'phone': '+91-' + ''.join(random.choices(string.digits, k=10)),
        'address': f'Test Address {timestamp}, India',
        'gst_number': f'{random.randint(10, 30):02d}AABCT{random.randint(1000, 9999)}A1Z{random.randint(0, 9)}'
    }

# Test 1: Basic Registration
print('\n📝 TEST 1: BASIC SUPPLIER REGISTRATION')
print('-' * 80)

test_data = generate_test_data()
print(f'Test Data Generated:')
print(f'  Supplier ID: {test_data["supplier_id"]}')
print(f'  Email: {test_data["email"]}')
print(f'  Company: {test_data["company_name"]}')
print(f'  Phone: {test_data["phone"]}')

try:
    response = requests.post(
        f'{BASE_URL}/supplier/register',
        json={
            **test_data,
            'password': 'TestPassword@123'
        }
    )
    
    if response.status_code == 200:
        supplier = response.json()
        print(f'\n✅ Registration Successful')
        print(f'  Supplier ID: {supplier["supplier_id"]}')
        print(f'  DB ID: {supplier["id"]}')
        print(f'  Company: {supplier["company_name"]}')
        print(f'  Email: {supplier["email"]}')
        print(f'  Approval Status: {"✅ Approved" if supplier["is_approved"] else "⏳ Pending"}')
        print(f'  Active: {"✅ Yes" if supplier["is_active"] else "❌ No"}')
        
        registered_supplier_id = supplier['supplier_id']
        registered_email = supplier['email']
    else:
        print(f'❌ Registration Failed: {response.status_code}')
        print(f'  Error: {response.text}')
        exit(1)
        
except Exception as e:
    print(f'❌ Error: {e}')
    exit(1)

# Test 2: Login with Newly Registered Supplier
print('\n🔑 TEST 2: LOGIN WITH NEWLY REGISTERED SUPPLIER')
print('-' * 80)

try:
    # Login with Supplier ID
    response = requests.post(
        f'{BASE_URL}/supplier/login',
        json={
            'supplier_id_or_email': registered_supplier_id,
            'password': 'TestPassword@123'
        }
    )
    
    if response.status_code == 200:
        login_data = response.json()
        print(f'✅ Login Successful (via Supplier ID)')
        print(f'  Token Generated: {login_data["access_token"][:50]}...')
        print(f'  Token Type: {login_data["token_type"]}')
        print(f'  Supplier ID: {login_data["supplier_id"]}')
        print(f'  Company: {login_data["company_name"]}')
        token = login_data['access_token']
    else:
        print(f'❌ Login Failed: {response.status_code}')
        print(f'  Error: {response.text}')
        exit(1)
        
except Exception as e:
    print(f'❌ Error: {e}')
    exit(1)

# Test 3: Login with Email
print('\n📧 TEST 3: LOGIN WITH EMAIL (ALTERNATIVE METHOD)')
print('-' * 80)

try:
    response = requests.post(
        f'{BASE_URL}/supplier/login',
        json={
            'supplier_id_or_email': registered_email,
            'password': 'TestPassword@123'
        }
    )
    
    if response.status_code == 200:
        login_data = response.json()
        print(f'✅ Email Login Successful')
        print(f'  Supplier ID: {login_data["supplier_id"]}')
        print(f'  Company: {login_data["company_name"]}')
    else:
        print(f'❌ Email Login Failed: {response.status_code}')
        
except Exception as e:
    print(f'❌ Error: {e}')

# Test 4: Duplicate Registration (Should Fail)
print('\n🚫 TEST 4: DUPLICATE REGISTRATION (ERROR HANDLING)')
print('-' * 80)

try:
    response = requests.post(
        f'{BASE_URL}/supplier/register',
        json={
            **test_data,
            'password': 'DifferentPassword@123'
        }
    )
    
    if response.status_code != 200:
        print(f'✅ Correctly Rejected Duplicate: {response.status_code}')
        print(f'  Error Message: {response.json().get("detail", "Unknown error")}')
    else:
        print(f'⚠️  Warning: Duplicate was accepted (unexpected)')
        
except Exception as e:
    print(f'❌ Error: {e}')

# Test 5: Invalid Registration (Missing Fields)
print('\n❌ TEST 5: INVALID REGISTRATION (MISSING FIELDS)')
print('-' * 80)

try:
    response = requests.post(
        f'{BASE_URL}/supplier/register',
        json={
            'email': 'test@example.com',
            # Missing required fields
            'password': 'TestPassword@123'
        }
    )
    
    if response.status_code != 200:
        print(f'✅ Correctly Rejected Invalid Data: {response.status_code}')
        print(f'  Validation Error Detected')
    else:
        print(f'⚠️  Warning: Invalid data was accepted (unexpected)')
        
except Exception as e:
    print(f'❌ Error: {e}')

# Test 6: Multiple Suppliers Registration
print('\n👥 TEST 6: MULTIPLE SUPPLIERS REGISTRATION')
print('-' * 80)

success_count = 0
for i in range(3):
    try:
        test_data = generate_test_data()
        response = requests.post(
            f'{BASE_URL}/supplier/register',
            json={
                **test_data,
                'password': 'TestPassword@123'
            }
        )
        
        if response.status_code == 200:
            supplier = response.json()
            print(f'  ✅ Supplier {i+1}: {supplier["company_name"]} ({supplier["supplier_id"]})')
            success_count += 1
        else:
            print(f'  ❌ Supplier {i+1} Registration Failed')
            
    except Exception as e:
        print(f'  ❌ Error registering Supplier {i+1}: {e}')

print(f'\nRegistration Success Rate: {success_count}/3')

# Test 7: Database Verification
print('\n💾 TEST 7: DATABASE VERIFICATION')
print('-' * 80)

try:
    from database import engine
    from models import Supplier
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy import func
    
    Session = sessionmaker(bind=engine)
    session = Session()
    
    total_suppliers = session.query(Supplier).count()
    approved_count = session.query(Supplier).filter(Supplier.is_approved == 1).count()
    pending_count = session.query(Supplier).filter(Supplier.is_approved == 0).count()
    active_count = session.query(Supplier).filter(Supplier.is_active == 1).count()
    
    print(f'Total Suppliers in Database: {total_suppliers}')
    print(f'  ✅ Approved: {approved_count}')
    print(f'  ⏳ Pending Approval: {pending_count}')
    print(f'  ✅ Active: {active_count}')
    
    # Get recently added suppliers
    print(f'\nRecent Suppliers (Last 3):')
    recent = session.query(Supplier).order_by(Supplier.created_at.desc()).limit(3).all()
    for i, sup in enumerate(recent, 1):
        status = '✅ Approved' if sup.is_approved else '⏳ Pending'
        print(f'  {i}. {sup.company_name} ({sup.supplier_id}) - {status}')
    
    session.close()
    
except Exception as e:
    print(f'❌ Database Verification Error: {e}')

print('\n' + '=' * 80)
print('✨ SUPPLIER REGISTRATION TEST COMPLETED ✨')
print('=' * 80)
