# Supplier Registration System - Complete Test Suite
# This script runs all tests for the supplier system

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║     SUPPLIER REGISTRATION SYSTEM - COMPLETE TEST SUITE         ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

$testsPassed = 0
$testsFailed = 0

# Check backend health
Write-Host "[PRE-CHECK] Verifying backend server..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "http://localhost:8000/health" -TimeoutSec 3
    Write-Host "✓ Backend is RUNNING at http://localhost:8000" -ForegroundColor Green
} catch {
    Write-Host "✗ Backend is NOT running!" -ForegroundColor Red
    Write-Host "Please start backend with: python -m uvicorn main:app --host 0.0.0.0 --port 8000"
    exit 1
}

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "TEST SCENARIO 1: COMPLETE REGISTRATION → LOGIN → PROFILE FLOW" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Test 1: Registration
Write-Host "[1/4] REGISTRATION TEST" -ForegroundColor Yellow

$supplier = @{
    supplier_id = "test_supplier_001"
    email = "test@testsupply.com"
    company_name = "Test Supply Co"
    contact_person = "Test Manager"
    password = "TestPass@123"
    phone = "555-0001"
    address = "100 Test St, Test City, TC 12345"
    gst_number = "12ABCDE1234F1Z5"
} | ConvertTo-Json

try {
    $reg = Invoke-RestMethod -Uri "http://localhost:8000/supplier/register" `
        -Method Post `
        -ContentType "application/json" `
        -Body $supplier `
        -TimeoutSec 5

    if ($reg.supplier_id -eq "test_supplier_001" -and $reg.is_approved -eq 1) {
        Write-Host "✓ PASS: Supplier registered successfully" -ForegroundColor Green
        Write-Host "  - ID: $($reg.supplier_id)"
        Write-Host "  - Company: $($reg.company_name)"
        Write-Host "  - Approved: Yes ✓ (auto-approved)"
        Write-Host "  - Active: Yes ✓"
        $testsPassed++
    } else {
        Write-Host "✗ FAIL: Registration did not return expected values" -ForegroundColor Red
        $testsFailed++
    }
} catch {
    Write-Host "✗ FAIL: Registration request failed" -ForegroundColor Red
    Write-Host "  Error: $($_.Exception.Message)"
    $testsFailed++
}

Write-Host ""

# Test 2: Login
Write-Host "[2/4] LOGIN TEST" -ForegroundColor Yellow

$login = @{
    supplier_id_or_email = "test_supplier_001"
    password = "TestPass@123"
} | ConvertTo-Json

try {
    $auth = Invoke-RestMethod -Uri "http://localhost:8000/supplier/login" `
        -Method Post `
        -ContentType "application/json" `
        -Body $login `
        -TimeoutSec 5

    if ($auth.access_token -and $auth.token_type -eq "bearer") {
        Write-Host "✓ PASS: Login successful" -ForegroundColor Green
        Write-Host "  - Token Type: $($auth.token_type)"
        Write-Host "  - Company: $($auth.company_name)"
        Write-Host "  - Token: $($auth.access_token.Substring(0,40))..."
        $global:testToken = $auth.access_token
        $testsPassed++
    } else {
        Write-Host "✗ FAIL: Login did not return token" -ForegroundColor Red
        $testsFailed++
    }
} catch {
    Write-Host "✗ FAIL: Login request failed" -ForegroundColor Red
    Write-Host "  Error: $($_.Exception.Message)"
    $testsFailed++
}

Write-Host ""

# Test 3: Get Profile
Write-Host "[3/4] PROFILE TEST" -ForegroundColor Yellow

if ($null -ne $global:testToken) {
    $headers = @{Authorization = "Bearer $($global:testToken)"}

    try {
        $profile = Invoke-RestMethod -Uri "http://localhost:8000/supplier/profile" `
            -Headers $headers `
            -TimeoutSec 5

        if ($profile.supplier_id -eq "test_supplier_001") {
            Write-Host "✓ PASS: Profile retrieved successfully" -ForegroundColor Green
            Write-Host "  - ID: $($profile.supplier_id)"
            Write-Host "  - Company: $($profile.company_name)"
            Write-Host "  - Email: $($profile.email)"
            Write-Host "  - Contact: $($profile.contact_person)"
            $testsPassed++
        } else {
            Write-Host "✗ FAIL: Profile did not return expected supplier" -ForegroundColor Red
            $testsFailed++
        }
    } catch {
        Write-Host "✗ FAIL: Profile request failed" -ForegroundColor Red
        Write-Host "  Error: $($_.Exception.Message)"
        $testsFailed++
    }
} else {
    Write-Host "⊘ SKIP: No token from login" -ForegroundColor Yellow
}

Write-Host ""

# Test 4: Get Orders
Write-Host "[4/4] ORDERS TEST" -ForegroundColor Yellow

if ($null -ne $global:testToken) {
    try {
        $orders = Invoke-RestMethod -Uri "http://localhost:8000/orders/pending" `
            -Headers $headers `
            -TimeoutSec 5

        Write-Host "✓ PASS: Orders endpoint accessible" -ForegroundColor Green
        if ($orders -and $orders.Count -gt 0) {
            Write-Host "  - Orders Found: $($orders.Count)"
            Write-Host "  - Status: Pending orders available"
        } else {
            Write-Host "  - Orders Found: 0 (None created yet)"
            Write-Host "  - Status: Normal (create via admin to test)"
        }
        $testsPassed++
    } catch {
        Write-Host "✗ FAIL: Orders request failed" -ForegroundColor Red
        Write-Host "  Error: $($_.Exception.Message)"
        $testsFailed++
    }
} else {
    Write-Host "⊘ SKIP: No token available" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "TEST SCENARIO 2: ERROR HANDLING TESTS" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Test 5: Duplicate Supplier ID
Write-Host "[5/6] DUPLICATE SUPPLIER ID TEST" -ForegroundColor Yellow

$duplicate = @{
    supplier_id = "test_supplier_001"
    email = "different@email.com"
    company_name = "Different Co"
    contact_person = "Different"
    password = "TestPass@123"
} | ConvertTo-Json

try {
    Invoke-RestMethod -Uri "http://localhost:8000/supplier/register" `
        -Method Post `
        -ContentType "application/json" `
        -Body $duplicate `
        -TimeoutSec 5
    
    Write-Host "✗ FAIL: Should have rejected duplicate supplier_id" -ForegroundColor Red
    $testsFailed++
} catch {
    if ($_.Exception.Response.StatusCode -eq "BadRequest" -or $_.Exception.Response.StatusCode -eq 400) {
        Write-Host "✓ PASS: Duplicate supplier_id correctly rejected" -ForegroundColor Green
        $testsPassed++
    } else {
        Write-Host "✗ FAIL: Wrong error code" -ForegroundColor Red
        $testsFailed++
    }
}

Write-Host ""

# Test 6: Invalid Login
Write-Host "[6/6] INVALID LOGIN TEST" -ForegroundColor Yellow

$badLogin = @{
    supplier_id_or_email = "test_supplier_001"
    password = "WrongPassword123"
} | ConvertTo-Json

try {
    Invoke-RestMethod -Uri "http://localhost:8000/supplier/login" `
        -Method Post `
        -ContentType "application/json" `
        -Body $badLogin `
        -TimeoutSec 5
    
    Write-Host "✗ FAIL: Should have rejected invalid password" -ForegroundColor Red
    $testsFailed++
} catch {
    if ($_.Exception.Response.StatusCode -eq "Unauthorized" -or $_.Exception.Response.StatusCode -eq 401) {
        Write-Host "✓ PASS: Invalid credentials correctly rejected" -ForegroundColor Green
        $testsPassed++
    } else {
        Write-Host "✗ FAIL: Wrong error code" -ForegroundColor Red
        $testsFailed++
    }
}

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "TEST RESULTS" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

Write-Host "Tests Passed: $testsPassed" -ForegroundColor Green
Write-Host "Tests Failed: $testsFailed" -ForegroundColor Red
Write-Host "Total Tests:  $($testsPassed + $testsFailed)"
Write-Host ""

if ($testsFailed -eq 0) {
    Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Green
    Write-Host "║  ✓ ALL TESTS PASSED - SYSTEM IS WORKING CORRECTLY!            ║" -ForegroundColor Green
    Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Green
    Write-Host ""
    Write-Host "System Status:" -ForegroundColor Green
    Write-Host "  ✓ Registration: Working (auto-approved)"
    Write-Host "  ✓ Login: Working (JWT tokens generated)"
    Write-Host "  ✓ Profile: Working (full details retrieved)"
    Write-Host "  ✓ Orders: Working (endpoints accessible)"
    Write-Host "  ✓ Error Handling: Working (duplicates rejected, auth enforced)"
    Write-Host ""
    Write-Host "READY FOR DEPLOYMENT! 🚀" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next Steps:" -ForegroundColor Cyan
    Write-Host "1. Review documentation: SUPPLIER_REGISTRATION_GUIDE.md"
    Write-Host "2. Create test purchase orders from admin panel"
    Write-Host "3. Test order acceptance and delivery workflow"
    Write-Host "4. Deploy to staging environment"
    Write-Host ""
} else {
    Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Red
    Write-Host "║  ✗ SOME TESTS FAILED - PLEASE REVIEW ERRORS ABOVE            ║" -ForegroundColor Red
    Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Red
    exit 1
}
