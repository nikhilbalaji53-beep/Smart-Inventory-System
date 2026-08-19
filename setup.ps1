# Smart Inventory System - Unified Server Setup Script
# This script sets up both backend and frontend for a unified server

Write-Host "================================" -ForegroundColor Cyan
Write-Host "Smart Inventory System - Setup" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan

# Check if we're in the correct directory
if (-not (Test-Path "backend") -or -not (Test-Path "frontend")) {
    Write-Host "Error: This script must be run from the project root directory!" -ForegroundColor Red
    exit 1
}

# Step 1: Backend Setup
Write-Host "`n[1/4] Setting up Backend..." -ForegroundColor Yellow

$backendDir = "backend"
if (Test-Path "$backendDir/venv") {
    Write-Host "Virtual environment already exists" -ForegroundColor Green
} else {
    Write-Host "Creating Python virtual environment..."
    Push-Location $backendDir
    python -m venv venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Error: Failed to create virtual environment" -ForegroundColor Red
        Pop-Location
        exit 1
    }
    Pop-Location
}

# Activate virtual environment
Write-Host "Activating virtual environment..."
& "$backendDir/venv/Scripts/Activate.ps1"

# Install backend dependencies
Write-Host "Installing backend dependencies..."
$requirementsFile = "$backendDir/requirements.txt"
if (Test-Path $requirementsFile) {
    pip install -r $requirementsFile
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Error: Failed to install backend dependencies" -ForegroundColor Red
        deactivate
        exit 1
    }
} else {
    Write-Host "Warning: requirements.txt not found!" -ForegroundColor Yellow
}

Write-Host "Backend setup completed!" -ForegroundColor Green

# Step 2: Frontend Setup
Write-Host "`n[2/4] Setting up Frontend..." -ForegroundColor Yellow

$frontendDir = "frontend"

# Check if Node.js is installed
$nodeVersion = node --version 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Node.js is not installed. Please install Node.js first." -ForegroundColor Red
    deactivate
    exit 1
}
Write-Host "Node.js version: $nodeVersion" -ForegroundColor Cyan

# Install frontend dependencies
Push-Location $frontendDir
if (Test-Path "node_modules") {
    Write-Host "node_modules already exists" -ForegroundColor Green
} else {
    Write-Host "Installing frontend dependencies..."
    npm install
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Error: Failed to install frontend dependencies" -ForegroundColor Red
        Pop-Location
        deactivate
        exit 1
    }
}

Write-Host "Frontend dependencies installed!" -ForegroundColor Green

# Step 3: Build Frontend
Write-Host "`n[3/4] Building Frontend..." -ForegroundColor Yellow

npm run build
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Frontend build failed" -ForegroundColor Red
    Pop-Location
    deactivate
    exit 1
}

Write-Host "Frontend built successfully!" -ForegroundColor Green
Pop-Location

# Step 4: Verify Database Configuration
Write-Host "`n[4/4] Verifying Configuration..." -ForegroundColor Yellow

$envFile = "$backendDir/.env"
if (Test-Path $envFile) {
    Write-Host ".env file found" -ForegroundColor Green
} else {
    Write-Host "`nWarning: .env file not found!" -ForegroundColor Yellow
    Write-Host "Make sure to create a .env file in the backend directory with database credentials:"
    Write-Host "  DB_USER=root"
    Write-Host "  DB_PASSWORD=your_password"
    Write-Host "  DB_HOST=localhost"
    Write-Host "  DB_PORT=3306"
    Write-Host "  DB_NAME=smart_inventory"
}

Write-Host "`n================================" -ForegroundColor Cyan
Write-Host "Setup completed successfully!" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Cyan
Write-Host "`nNext steps:" -ForegroundColor Cyan
Write-Host "1. Ensure MySQL is running" -ForegroundColor White
Write-Host "2. Run: .\run-server.ps1" -ForegroundColor White
Write-Host "3. Open browser to http://localhost:8000" -ForegroundColor White
Write-Host ""
