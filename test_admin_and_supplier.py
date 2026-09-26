#!/usr/bin/env python3
"""
Comprehensive Integration Test for Admin, Supplier, and Sales Workflows
Smart Inventory Management System
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def log_step(title):
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}")

def check(condition, message):
    if condition:
        print(f"  [PASS] {message}")
        return True
    else:
        print(f"  [FAIL] {message}")
        return False

def run_tests():
    total_passed = 0
    total_tests = 0
    timestamp = int(time.time())

    # ----------------------------------------------------
    # SECTION 0: HEALTH & ROOT
    # ----------------------------------------------------
    log_step("SECTION 0: SERVER & FRONTEND HEALTH")
    total_tests += 1
    r = requests.get(f"{BASE_URL}/health")
    if check(r.status_code == 200 and r.json().get("status") == "healthy", "Backend /health reports healthy status"):
        total_passed += 1

    total_tests += 1
    r = requests.get(f"{BASE_URL}/")
    if check(r.status_code == 200 and "<!doctype html>" in r.text.lower(), "Frontend root (/) serves SPA index.html"):
        total_passed += 1

    # ----------------------------------------------------
    # SECTION 1: ADMIN AUTHENTICATION
    # ----------------------------------------------------
    log_step("SECTION 1: ADMIN AUTHENTICATION & ACCESS")
    total_tests += 1
    admin_login_payload = {
        "username": "superadmin",
        "password": "SuperAdmin123!@"
    }
    r = requests.post(f"{BASE_URL}/auth/login", json=admin_login_payload)
    if check(r.status_code == 200, "Admin login successful (HTTP 200)"):
        total_passed += 1

    admin_data = r.json()
    admin_token = admin_data.get("access_token")
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    total_tests += 1
    if check(admin_data.get("is_admin") == 1, "Admin privilege verified (is_admin == 1)"):
        total_passed += 1

    total_tests += 1
    r = requests.get(f"{BASE_URL}/auth/me", headers=admin_headers)
    if check(r.status_code == 200 and r.json().get("username") == "superadmin", "Admin profile retrieved via /auth/me"):
        total_passed += 1

    # ----------------------------------------------------
    # SECTION 2: ADMIN PRODUCT & INVENTORY MANAGEMENT
    # ----------------------------------------------------
    log_step("SECTION 2: ADMIN PRODUCT & INVENTORY MANAGEMENT")
    total_tests += 1
    r = requests.get(f"{BASE_URL}/products/", headers=admin_headers)
    products = r.json() if r.status_code == 200 else []
    if check(r.status_code == 200 and isinstance(products, list), f"Listed {len(products)} products from catalog"):
        total_passed += 1

    total_tests += 1
    new_product_payload = {
        "name": f"Test Item {timestamp}",
        "category": "Electronics",
        "price": 249.99,
        "current_stock": 25,
        "minimum_stock": 10,
        "supplier": "Test Supplier Co"
    }
    r = requests.post(f"{BASE_URL}/products/", json=new_product_payload, headers=admin_headers)
    created_product = r.json() if r.status_code == 200 else {}
    test_product_id = created_product.get("id")
    if check(r.status_code == 200 and test_product_id is not None, f"Created product '{new_product_payload['name']}' (ID: {test_product_id})"):
        total_passed += 1

    total_tests += 1
    stock_payload = {"quantity": 10}
    r = requests.patch(f"{BASE_URL}/products/{test_product_id}/stock", json=stock_payload, headers=admin_headers)
    updated_stock = r.json().get("current_stock") if r.status_code == 200 else None
    if check(r.status_code == 200 and updated_stock == 35, f"Updated stock for product ID {test_product_id}: 25 + 10 = {updated_stock}"):
        total_passed += 1

    # ----------------------------------------------------
    # SECTION 3: ADMIN DASHBOARD & SYSTEM MONITORING
    # ----------------------------------------------------
    log_step("SECTION 3: ADMIN DASHBOARD & SYSTEM MONITORING")
    total_tests += 1
    r = requests.get(f"{BASE_URL}/dashboard/", headers=admin_headers)
    if check(r.status_code == 200, "Dashboard metrics retrieved successfully"):
        total_passed += 1

    total_tests += 1
    r = requests.get(f"{BASE_URL}/dashboard/summary", headers=admin_headers)
    if check(r.status_code == 200, "Dashboard financial and inventory summary retrieved"):
        total_passed += 1

    total_tests += 1
    r = requests.get(f"{BASE_URL}/alerts/", headers=admin_headers)
    alerts_data = r.json() if r.status_code == 200 else {}
    alerts_list = alerts_data.get("alerts", alerts_data) if isinstance(alerts_data, dict) else alerts_data
    if check(r.status_code == 200 and isinstance(alerts_list, list), f"System alerts queried ({len(alerts_list)} active alerts)"):
        total_passed += 1

    total_tests += 1
    r = requests.get(f"{BASE_URL}/predictions/1?days=7", headers=admin_headers)
    if check(r.status_code == 200 and len(r.json().get("predictions", [])) > 0, "ML demand forecast generated successfully"):
        total_passed += 1

    # ----------------------------------------------------
    # SECTION 4: SUPPLIER AUTHENTICATION & PROFILE
    # ----------------------------------------------------
    log_step("SECTION 4: SUPPLIER AUTHENTICATION & PROFILE")
    total_tests += 1
    supplier_login_payload = {
        "supplier_id_or_email": "supplier_test_001",
        "password": "TestPass@123"
    }
    r = requests.post(f"{BASE_URL}/supplier/login", json=supplier_login_payload)
    if check(r.status_code == 200, "Supplier login successful (supplier_test_001)"):
        total_passed += 1

    supplier_data = r.json()
    supplier_token = supplier_data.get("access_token")
    supplier_headers = {"Authorization": f"Bearer {supplier_token}"}

    total_tests += 1
    if check(supplier_data.get("is_approved") == 1, "Supplier approval confirmed (is_approved == 1)"):
        total_passed += 1

    total_tests += 1
    r = requests.get(f"{BASE_URL}/supplier/profile", headers=supplier_headers)
    profile = r.json() if r.status_code == 200 else {}
    if check(r.status_code == 200 and profile.get("supplier_id") == "supplier_test_001", f"Retrieved supplier profile ({profile.get('company_name')})"):
        total_passed += 1
    supplier_db_id = profile.get("id", 47)

    total_tests += 1
    r = requests.get(f"{BASE_URL}/supplier/status/supplier_test_001")
    is_approved_status = r.status_code == 200 and (r.json().get("is_approved") == 1 or r.json().get("message") == "Approved")
    if check(is_approved_status, "Supplier status public endpoint verified ('Approved')"):
        total_passed += 1

    # ----------------------------------------------------
    # SECTION 5: PURCHASE ORDER & DELIVERY WORKFLOW
    # ----------------------------------------------------
    log_step("SECTION 5: PURCHASE ORDER & DELIVERY LIFECYCLE")
    total_tests += 1
    po_num = f"PO-{timestamp}"
    po_params = {
        "po_number": po_num,
        "supplier_id": supplier_db_id,
        "product_id": test_product_id,
        "quantity_ordered": 20,
        "unit_price": 180.0,
        "notes": "Automated integration test order"
    }
    r = requests.post(f"{BASE_URL}/orders/", params=po_params, headers=admin_headers)
    po_data = r.json() if r.status_code == 200 else {}
    po_id = po_data.get("id")
    if check(r.status_code == 200 and po_id is not None, f"Admin created purchase order {po_num} (ID: {po_id})"):
        total_passed += 1

    total_tests += 1
    r = requests.get(f"{BASE_URL}/orders/pending", headers=supplier_headers)
    pending_orders = r.json() if r.status_code == 200 else []
    found_po = any(item.get("order", {}).get("id") == po_id for item in pending_orders)
    if check(r.status_code == 200 and found_po, f"Supplier sees PO {po_num} in pending orders list"):
        total_passed += 1

    total_tests += 1
    r = requests.post(f"{BASE_URL}/orders/{po_id}/accept", headers=supplier_headers)
    accepted = r.status_code == 200 and r.json().get("order", {}).get("status") == "ACCEPTED"
    if check(accepted, f"Supplier accepted order {po_num} (Status -> ACCEPTED)"):
        total_passed += 1

    r_stock_before = requests.get(f"{BASE_URL}/products/{test_product_id}", headers=admin_headers)
    stock_before = r_stock_before.json().get("current_stock", 0)

    total_tests += 1
    delivery_payload = {
        "purchase_order_id": po_id,
        "quantity_delivered": 20,
        "delivery_reference": f"DELIV-{timestamp}",
        "shipping_carrier": "Express Logistics",
        "tracking_number": f"TRK{timestamp}",
        "notes": "Delivered in full"
    }
    r = requests.post(f"{BASE_URL}/orders/{po_id}/deliver", json=delivery_payload, headers=supplier_headers)
    delivered = r.status_code == 200 and r.json().get("quantity_delivered") == 20
    if check(delivered, f"Supplier submitted delivery of 20 units for PO {po_num}"):
        total_passed += 1

    total_tests += 1
    r_stock_after = requests.get(f"{BASE_URL}/products/{test_product_id}", headers=admin_headers)
    stock_after = r_stock_after.json().get("current_stock", 0)
    stock_incremented = (stock_after == stock_before + 20)
    if check(stock_incremented, f"Inventory stock automatically incremented: {stock_before} -> {stock_after} (+20)"):
        total_passed += 1

    # ----------------------------------------------------
    # SECTION 6: SALES RECORDING API
    # ----------------------------------------------------
    log_step("SECTION 6: SALES RECORDING & HISTORY API")
    total_tests += 1
    sale_payload = {
        "product_id": test_product_id,
        "quantity": 5,
        "sale_date": "2026-09-26"
    }
    r = requests.post(f"{BASE_URL}/api/sales", json=sale_payload)
    if check(r.status_code == 201 and "Sale recorded successfully" in r.text, "POST /api/sales successfully recorded sale"):
        total_passed += 1

    total_tests += 1
    r_post_stock = requests.get(f"{BASE_URL}/products/{test_product_id}", headers=admin_headers)
    stock_post_sale = r_post_stock.json().get("current_stock", 0)
    if check(stock_post_sale == stock_after - 5, f"Inventory stock correctly deducted after sale: {stock_after} -> {stock_post_sale} (-5)"):
        total_passed += 1

    total_tests += 1
    r = requests.get(f"{BASE_URL}/api/sales")
    sales_history = r.json() if r.status_code == 200 else []
    found_sale = any(s.get("product_name") == new_product_payload["name"] for s in sales_history)
    if check(r.status_code == 200 and found_sale, f"GET /api/sales returns recorded sale in history"):
        total_passed += 1

    # Validation cases
    total_tests += 1
    r = requests.post(f"{BASE_URL}/api/sales", json={})
    if check(r.status_code == 400, "POST /api/sales rejects empty body (HTTP 400)"):
        total_passed += 1

    total_tests += 1
    r = requests.post(f"{BASE_URL}/api/sales", json={"product_id": test_product_id, "quantity": 999999})
    if check(r.status_code == 400 and "Insufficient stock" in r.text, "POST /api/sales rejects sale exceeding available stock (HTTP 400)"):
        total_passed += 1

    # Clean up test product
    try:
        requests.delete(f"{BASE_URL}/products/{test_product_id}", headers=admin_headers)
    except:
        pass

    # ----------------------------------------------------
    # FINAL SUMMARY
    # ----------------------------------------------------
    log_step("TEST RESULTS SUMMARY")
    print(f"  Total Tests Executed: {total_tests}")
    print(f"  Passed: {total_passed}")
    print(f"  Failed: {total_tests - total_passed}")
    print(f"  Success Rate: {(total_passed / total_tests) * 100:.1f}%\n")

    return total_passed == total_tests

if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)
