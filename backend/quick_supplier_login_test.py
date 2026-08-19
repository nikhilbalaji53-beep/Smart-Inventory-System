#!/usr/bin/env python
"""
Quick Supplier Login Testing - Smart Inventory System
"""

import requests
import json

API_BASE_URL = "http://localhost:8000"

def test_login(supplier_id, password, description):
    """Test a login attempt"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/supplier/login",
            json={"supplier_id_or_email": supplier_id, "password": password},
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ {description}")
            print(f"   Company: {data.get('company_name')}")
            print(f"   Token: {data.get('access_token')[:50]}...")
            print(f"   Approved: {data.get('is_approved')}\n")
            return True
        else:
            print(f"❌ {description} - Status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ {description} - Error: {e}\n")
        return False

def main():
    print("\n" + "="*70)
    print("  SUPPLIER LOGIN PAGE - QUICK TEST".center(70))
    print("="*70 + "\n")
    
    print("🧪 Testing Supplier Login Functionality...\n")
    
    # Test 1: Approved supplier with ID
    print("Test 1: Login with Supplier ID (Approved Supplier)")
    result1 = test_login("sup_electronics_001", "TechSupply@2024", "TechSupply Electronics")
    
    # Test 2: Approved supplier with email
    print("Test 2: Login with Email (Approved Supplier)")
    result2 = test_login("contact@techsupply.com", "TechSupply@2024", "TechSupply via Email")
    
    # Test 3: Pending supplier
    print("Test 3: Login with Pending Supplier (Not Approved)")
    result3 = test_login("sup_textile_002", "ClothCorp@2024", "Cloth Corporation (Pending)")
    
    # Test 4: Invalid password
    print("Test 4: Invalid Password (Error Case)")
    try:
        response = requests.post(
            f"{API_BASE_URL}/supplier/login",
            json={"supplier_id_or_email": "sup_electronics_001", "password": "WrongPassword"},
            timeout=5
        )
        if response.status_code == 401:
            print(f"✅ Correctly returns 401 Unauthorized")
            print(f"   Error: {response.json().get('detail')}\n")
            result4 = True
        else:
            print(f"❌ Unexpected status: {response.status_code}\n")
            result4 = False
    except Exception as e:
        print(f"❌ Error: {e}\n")
        result4 = False
    
    # Test 5: Multiple suppliers
    print("Test 5: Multiple Suppliers Login")
    suppliers = [
        ("sup_food_001", "FreshFood@2024", "Fresh Foods Wholesale"),
        ("sup_pharma_001", "MedHub@2024", "MedHub Pharmaceuticals"),
    ]
    results = []
    for sid, pwd, name in suppliers:
        try:
            response = requests.post(
                f"{API_BASE_URL}/supplier/login",
                json={"supplier_id_or_email": sid, "password": pwd},
                timeout=5
            )
            if response.status_code == 200:
                print(f"   ✅ {name}")
                results.append(True)
            else:
                print(f"   ❌ {name}")
                results.append(False)
        except:
            results.append(False)
    result5 = all(results)
    print()
    
    # Test 6: Pending suppliers list
    print("Test 6: Fetch Pending Suppliers (Admin)")
    try:
        response = requests.get(f"{API_BASE_URL}/supplier/pending", timeout=5)
        if response.status_code == 200:
            pending = response.json()
            print(f"✅ Fetched {len(pending)} pending suppliers")
            for p in pending[:3]:
                print(f"   - {p.get('company_name')} ({p.get('supplier_id')})")
            print()
            result6 = True
        else:
            print(f"❌ Error fetching pending suppliers\n")
            result6 = False
    except Exception as e:
        print(f"❌ Error: {e}\n")
        result6 = False
    
    # Summary
    print("="*70)
    print("TEST SUMMARY")
    print("="*70)
    all_results = [result1, result2, result3, result4, result5, result6]
    passed = sum(all_results)
    total = len(all_results)
    
    print(f"Passed: {passed}/{total}")
    print(f"Pass Rate: {100*passed//total}%")
    print()
    
    print("✅ SUPPLIER LOGIN PAGE - FULLY OPERATIONAL" if passed == total else "⚠️  Some tests failed")
    print("\n" + "="*70 + "\n")

if __name__ == "__main__":
    main()
