#!/usr/bin/env python
"""
Supplier Data Testing & Interaction Guide
Smart Inventory System - Backend API

This script demonstrates how to:
1. Login as a supplier
2. Retrieve supplier information
3. Test supplier API endpoints
4. Manage supplier credentials
"""

import requests
import json
from datetime import datetime

# API Configuration
API_BASE_URL = "http://localhost:8000"
SUPPLIER_API_PREFIX = "/supplier"

# Color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}")
    print(f"{text}")
    print(f"{'='*60}{Colors.ENDC}\n")

def print_success(text):
    print(f"{Colors.OKGREEN}✅ {text}{Colors.ENDC}")

def print_error(text):
    print(f"{Colors.FAIL}❌ {text}{Colors.ENDC}")

def print_info(text):
    print(f"{Colors.OKCYAN}ℹ️  {text}{Colors.ENDC}")

def print_json(data):
    print(json.dumps(data, indent=2, default=str))

# Sample Supplier Test Data
TEST_SUPPLIERS = [
    {
        "name": "TechSupply Electronics",
        "supplier_id": "sup_electronics_001",
        "email": "contact@techsupply.com",
        "password": "TechSupply@2024"
    },
    {
        "name": "Fresh Foods Wholesale",
        "supplier_id": "sup_food_001",
        "email": "order@freshfoods.com",
        "password": "FreshFood@2024"
    },
    {
        "name": "MedHub Pharmaceuticals",
        "supplier_id": "sup_pharma_001",
        "email": "sales@medhub.com",
        "password": "MedHub@2024"
    },
    {
        "name": "Fabric World",
        "supplier_id": "sup_textile_001",
        "email": "inquiry@fabricworld.com",
        "password": "Fabric@2024"
    },
]

def test_supplier_login(supplier_id_or_email, password):
    """Test supplier login"""
    print_header("Testing Supplier Login")
    
    url = f"{API_BASE_URL}{SUPPLIER_API_PREFIX}/login"
    payload = {
        "supplier_id_or_email": supplier_id_or_email,
        "password": password
    }
    
    print_info(f"Attempting login with: {supplier_id_or_email}")
    print(f"URL: {url}")
    print(f"Payload: {json.dumps(payload, indent=2)}\n")
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Login successful!")
            print(f"\nResponse:")
            print_json(data)
            return data.get("access_token")
        else:
            print_error(f"Login failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return None
    
    except requests.exceptions.RequestException as e:
        print_error(f"Request failed: {e}")
        return None

def get_pending_suppliers():
    """Retrieve list of pending suppliers"""
    print_header("Fetching Pending Suppliers")
    
    url = f"{API_BASE_URL}{SUPPLIER_API_PREFIX}/pending"
    
    print_info(f"Fetching pending suppliers from: {url}\n")
    
    try:
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            suppliers = response.json()
            print_success(f"Retrieved {len(suppliers)} pending suppliers")
            print(f"\nPending Suppliers:")
            
            for i, supplier in enumerate(suppliers, 1):
                print(f"\n{i}. {supplier.get('company_name')}")
                print(f"   ID: {supplier.get('supplier_id')}")
                print(f"   Email: {supplier.get('email')}")
                print(f"   Contact: {supplier.get('contact_person')}")
                print(f"   Status: {'⏳ Pending' if supplier.get('is_approved') == 0 else '✅ Approved'}")
        else:
            print_error(f"Failed to fetch suppliers: {response.status_code}")
    
    except requests.exceptions.RequestException as e:
        print_error(f"Request failed: {e}")

def register_new_supplier(supplier_data):
    """Register a new supplier"""
    print_header("Testing Supplier Registration")
    
    url = f"{API_BASE_URL}{SUPPLIER_API_PREFIX}/register"
    
    print_info(f"Registering new supplier: {supplier_data['company_name']}")
    print(f"URL: {url}")
    print(f"Payload:")
    print_json(supplier_data)
    print()
    
    try:
        response = requests.post(url, json=supplier_data, timeout=10)
        
        if response.status_code == 200:
            print_success("Registration successful!")
            print(f"\nResponse:")
            print_json(response.json())
        else:
            print_error(f"Registration failed: {response.status_code}")
            print(f"Response: {response.text}")
    
    except requests.exceptions.RequestException as e:
        print_error(f"Request failed: {e}")

def test_api_connection():
    """Test if API server is running"""
    print_header("Testing API Connection")
    
    docs_url = f"{API_BASE_URL}/docs"
    print_info(f"Testing API at: {API_BASE_URL}")
    
    try:
        response = requests.get(docs_url, timeout=5)
        if response.status_code == 200:
            print_success("✅ API server is running and responding")
            print(f"   API Documentation: {docs_url}")
            return True
        else:
            print_error(f"API returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_error("Cannot connect to API server")
        print_info("Make sure the server is running: python -m uvicorn main:app --reload")
        return False
    except Exception as e:
        print_error(f"Connection error: {e}")
        return False

def run_tests():
    """Run all supplier tests"""
    print(f"\n{Colors.BOLD}{Colors.HEADER}")
    print("╔" + "="*58 + "╗")
    print("║" + " "*58 + "║")
    print("║" + "  Smart Inventory System - Supplier API Testing  ".center(58) + "║")
    print("║" + " "*58 + "║")
    print("╚" + "="*58 + "╝")
    print(f"{Colors.ENDC}")
    
    # Test API connection
    if not test_api_connection():
        print_error("Cannot proceed: API server is not running")
        return
    
    # Test login for each supplier
    print_header("Testing Multiple Supplier Logins")
    for supplier in TEST_SUPPLIERS:
        token = test_supplier_login(supplier["supplier_id"], supplier["password"])
        if token:
            print_success(f"Token obtained for {supplier['name']}")
            print(f"Token (first 50 chars): {token[:50]}...\n")
    
    # Get pending suppliers
    get_pending_suppliers()
    
    print_header("Test Summary")
    print_success("All tests completed!")
    print_info("For more details, visit: http://localhost:8000/docs")

if __name__ == "__main__":
    print("Supplier Testing Module - Smart Inventory System")
    print("Usage: python supplier_test.py\n")
    
    # Uncomment the test you want to run:
    
    # Test API connection
    test_api_connection()
    
    # Test single login
    # test_supplier_login("sup_electronics_001", "TechSupply@2024")
    
    # Get pending suppliers
    # get_pending_suppliers()
    
    # Run all tests
    # run_tests()
