@echo off
REM Test script for Supplier Order and Delivery Flow

echo ===========================================
echo Smart Inventory - Supplier Order Flow Test
echo ===========================================
echo.

REM Set variables
set BASE_URL=http://localhost:8000
set SUPPLIER_EMAIL=supplier_test_001@example.com
set SUPPLIER_ID=supplier_test_001
set SUPPLIER_PASSWORD=TestPass@123

echo [1] Logging in supplier...
powershell -Command ^
  "$body = @{supplier_id_or_email='%SUPPLIER_ID%'; password='%SUPPLIER_PASSWORD%'} | ConvertTo-Json; " ^
  "$login = Invoke-RestMethod -Uri '%BASE_URL%/supplier/login' -Method Post -ContentType 'application/json' -Body $body; " ^
  "$token = $login.access_token; " ^
  "Write-Host 'Supplier logged in. Token length: ' $token.Length; " ^
  "$env:SUPPLIER_TOKEN = $token"

echo [2] Creating a test product...
for /f %%I in ('powershell -Command "Get-Date -Format yyyyMMddHHmmss"') do set TIMESTAMP=%%I
powershell -Command ^
  "$body = @{" ^
  "name='Test Widget %TIMESTAMP%'; " ^
  "category='Electronics'; " ^
  "price=99.99; " ^
  "current_stock=50; " ^
  "minimum_stock=10" ^
  "} | ConvertTo-Json; " ^
  "$product = Invoke-RestMethod -Uri '%BASE_URL%/products/' -Method Post -ContentType 'application/json' -Body $body; " ^
  "Write-Host 'Product created with ID: ' $product.id; " ^
  "$env:PRODUCT_ID = $product.id"

echo [3] Creating a purchase order (Admin would do this)...
powershell -Command ^
  "Write-Host 'Purchase order creation would be called by admin endpoint"

echo [4] Getting pending orders for supplier...
powershell -Command ^
  "$headers = @{Authorization = 'Bearer ' + '$env:SUPPLIER_TOKEN'}; " ^
  "$orders = Invoke-RestMethod -Uri '%BASE_URL%/orders/pending' -Headers $headers; " ^
  "if ($orders) { Write-Host 'Pending orders count: ' $orders.Count } else { Write-Host 'No pending orders' }"

echo [5] Testing alerts endpoint...
powershell -Command ^
  "$alerts = Invoke-RestMethod -Uri '%BASE_URL%/alerts/'; " ^
  "Write-Host 'Alerts retrieved. Count: ' $alerts.Count"

echo.
echo ===========================================
echo Test completed
echo ===========================================
pause
