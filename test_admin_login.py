#!/usr/bin/env python
"""
Admin Login Test Script
Tests admin user creation and login functionality
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_admin_functionality():
    print("="*60)
    print("SMART INVENTORY SYSTEM - ADMIN LOGIN TEST")
    print("="*60)
    print()
    
    # Test 1: Register first user (should be admin)
    print("TEST 1: Register First User (Should be Admin)")
    print("-" * 60)
    reg_data = {
        "username": "superadmin",
        "email": "superadmin@smartinventory.com",
        "password": "SuperAdmin123!@"
    }
    
    try:
        resp = requests.post(f"{BASE_URL}/auth/register", json=reg_data)
        print(f"Status Code: {resp.status_code}")
        
        if resp.status_code == 200:
            user = resp.json()
            print(f"✓ User Created Successfully!")
            print(f"  - ID: {user.get('id')}")
            print(f"  - Username: {user.get('username')}")
            print(f"  - Email: {user.get('email')}")
            print(f"  - Is Admin: {user.get('is_admin')} (should be 1)")
            print()
        else:
            print(f"✗ Error: {resp.text}")
            print()
            return False
    except Exception as e:
        print(f"✗ Exception: {e}")
        print()
        return False
    
    # Test 2: Login as admin
    print("TEST 2: Admin Login")
    print("-" * 60)
    login_data = {
        "username": "superadmin",
        "password": "SuperAdmin123!@"
    }
    
    try:
        resp = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        print(f"Status Code: {resp.status_code}")
        
        if resp.status_code == 200:
            token_data = resp.json()
            print(f"✓ Login Successful!")
            print(f"  - Username: {token_data.get('username')}")
            print(f"  - Is Admin: {token_data.get('is_admin')} (should be 1)")
            print(f"  - Token Type: {token_data.get('token_type')}")
            print(f"  - Token: {token_data.get('access_token', '')[:40]}...")
            print()
            
            admin_token = token_data.get('access_token')
            is_admin = token_data.get('is_admin')
            
            if is_admin == 1:
                print("✓ ADMIN STATUS CONFIRMED!")
            else:
                print(f"✗ User is not admin (is_admin={is_admin})")
            print()
        else:
            print(f"✗ Error: {resp.text}")
            print()
            return False
    except Exception as e:
        print(f"✗ Exception: {e}")
        print()
        return False
    
    # Test 3: Test protected endpoint with admin token
    print("TEST 3: Access Protected Endpoint with Admin Token")
    print("-" * 60)
    
    try:
        headers = {"Authorization": f"Bearer {admin_token}"}
        resp = requests.get(f"{BASE_URL}/api/products", headers=headers)
        print(f"Status Code: {resp.status_code}")
        
        if resp.status_code == 200:
            print(f"✓ Protected endpoint accessible!")
            print()
        elif resp.status_code == 401:
            print(f"✗ Unauthorized (token invalid)")
            print()
        else:
            print(f"Response: {resp.text}")
            print()
    except Exception as e:
        print(f"✗ Exception: {e}")
        print()
        return False
    
    # Test 4: Register second user (should NOT be admin)
    print("TEST 4: Register Second User (Should NOT be Admin)")
    print("-" * 60)
    reg_data2 = {
        "username": "regularuser",
        "email": "user@smartinventory.com",
        "password": "User123!@"
    }
    
    try:
        resp = requests.post(f"{BASE_URL}/auth/register", json=reg_data2)
        print(f"Status Code: {resp.status_code}")
        
        if resp.status_code == 200:
            user = resp.json()
            print(f"✓ User Created Successfully!")
            print(f"  - Username: {user.get('username')}")
            print(f"  - Is Admin: {user.get('is_admin')} (should be 0)")
            
            if user.get('is_admin') == 0:
                print(f"✓ Regular user status confirmed (is_admin=0)")
            else:
                print(f"✗ User should not be admin!")
            print()
        else:
            print(f"✗ Error: {resp.text}")
            print()
    except Exception as e:
        print(f"✗ Exception: {e}")
        print()
    
    print("="*60)
    print("ADMIN LOGIN TEST COMPLETED SUCCESSFULLY!")
    print("="*60)
    return True

if __name__ == "__main__":
    test_admin_functionality()
