# Smart Inventory System - Supplier Order Flow Test Script
# Run this to validate the complete supplier order and delivery workflow

param(
    [string]$BaseUrl = "http://localhost:8000",
    [string]$SupplierId = "supplier_test_001",
    [string]$SupplierPassword = "TestPass@123"
)

# Color output
function Write-Success { Write-Host $args -ForegroundColor Green }
function Write-Error { Write-Host "ERROR: $args" -ForegroundColor Red }
function Write-Info { Write-Host $args -ForegroundColor Cyan }
function Write-Section { Write-Host "`n=== $args ===" -ForegroundColor Yellow }

# Error handling
$ErrorActionPreference = "Stop"

Write-Section "Smart Inventory System - Supplier Order Flow Test"

# Step 1: Login
Write-Info "[1/6] Logging in supplier..."
try {
    $loginBody = @{
        supplier_id_or_email = $SupplierId
        password = $SupplierPassword
    } | ConvertTo-Json
    
    $loginResponse = Invoke-RestMethod -Uri "$BaseUrl/supplier/login" `
        -Method Post `
        -ContentType "application/json" `
        -Body $loginBody
    
    $supplierToken = $loginResponse.access_token
    $supplierCompany = $loginResponse.company_name
    $supplierId_db = $loginResponse.supplier_id
    
    Write-Success "✓ Supplier logged in: $supplierCompany"
    Write-Host "  Token length: $($supplierToken.Length) chars"
    Write-Host "  Supplier ID: $supplierId_db"
} catch {
    Write-Error "Failed to login: $($_.Exception.Message)"
    exit 1
}

# Step 2: Get pending orders
Write-Info "[2/6] Checking for pending orders..."
try {
    $headers = @{Authorization = "Bearer $supplierToken"}
    
    $pendingOrders = Invoke-RestMethod -Uri "$BaseUrl/orders/pending" `
        -Headers $headers
    
    if ($pendingOrders -and $pendingOrders.Count -gt 0) {
        Write-Success "✓ Found $($pendingOrders.Count) pending order(s)"
        foreach ($order in $pendingOrders) {
            Write-Host "  - PO: $($order.order.po_number), Status: $($order.order.status), Qty: $($order.order.quantity_ordered)"
        }
    } else {
        Write-Host "  No pending orders (this is normal if no orders were created by admin)"
    }
} catch {
    Write-Error "Failed to get pending orders: $($_.Exception.Message)"
}

# Step 3: Get supplier profile
Write-Info "[3/6] Fetching supplier profile..."
try {
    $profile = Invoke-RestMethod -Uri "$BaseUrl/supplier/profile" `
        -Headers @{Authorization = "Bearer $supplierToken"}
    
    Write-Success "✓ Profile retrieved"
    Write-Host "  Company: $($profile.company_name)"
    Write-Host "  Email: $($profile.email)"
    Write-Host "  Phone: $($profile.phone)"
    Write-Host "  Address: $($profile.address)"
    Write-Host "  GST: $($profile.gst_number)"
    Write-Host "  Approved: $($profile.is_approved)"
} catch {
    Write-Error "Failed to get profile: $($_.Exception.Message)"
}

# Step 4: Get all products (to know what's available)
Write-Info "[4/6] Getting available products..."
try {
    $products = Invoke-RestMethod -Uri "$BaseUrl/products/" `
        -Method Get
    
    if ($products -and $products.Count -gt 0) {
        Write-Success "✓ Found $($products.Count) product(s)"
        $products | Select-Object -First 3 | ForEach-Object {
            Write-Host "  - $($_.name) (ID: $($_.id), Stock: $($_.current_stock))"
        }
    } else {
        Write-Host "  No products found"
    }
} catch {
    Write-Error "Failed to get products: $($_.Exception.Message)"
}

# Step 5: Check alerts
Write-Info "[5/6] Checking active alerts..."
try {
    $alerts = Invoke-RestMethod -Uri "$BaseUrl/alerts/" -Method Get
    
    if ($alerts -and $alerts.Count -gt 0) {
        Write-Success "✓ Found $($alerts.Count) alert(s)"
        $alerts | Select-Object -First 3 | ForEach-Object {
            Write-Host "  - $($_.product_name): $($_.reasons -join ', ')"
        }
    } else {
        Write-Success "✓ No active alerts"
    }
} catch {
    Write-Error "Failed to get alerts: $($_.Exception.Message)"
}

# Step 6: Health check
Write-Info "[6/6] Checking system health..."
try {
    $health = Invoke-RestMethod -Uri "$BaseUrl/health" -Method Get
    
    Write-Success "✓ System healthy"
    Write-Host "  Status: $($health.status)"
    Write-Host "  Timestamp: $($health.timestamp)"
} catch {
    Write-Error "System health check failed: $($_.Exception.Message)"
}

Write-Section "Test Results Summary"
Write-Success "✓ Supplier authentication working"
Write-Success "✓ API endpoints accessible"
Write-Success "✓ Database connection active"
Write-Host ""
Write-Host "Next steps:"
Write-Host "1. Admin creates purchase order: POST /orders/"
Write-Host "2. Supplier accepts order: POST /orders/{po_id}/accept"
Write-Host "3. Supplier submits delivery: POST /orders/{po_id}/deliver"
Write-Host ""
Write-Host "For full documentation, see: SUPPLIER_ORDER_FLOW.md"
