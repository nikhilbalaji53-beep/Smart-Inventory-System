# Smart Inventory System - Unified Server Run Script
# This script runs both backend and frontend from a single server

Write-Host "================================" -ForegroundColor Cyan
Write-Host "Smart Inventory System - Server" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan

# Check if we're in the correct directory
if (-not (Test-Path "backend") -or -not (Test-Path "frontend")) {
    Write-Host "Error: This script must be run from the project root directory!" -ForegroundColor Red
    exit 1
}

# Check if frontend is built
$distDir = "frontend/dist"
if (-not (Test-Path $distDir)) {
    Write-Host "Error: Frontend is not built!" -ForegroundColor Red
    Write-Host "Run: npm run build" -ForegroundColor Yellow
    Write-Host "from the frontend directory first" -ForegroundColor Yellow
    exit 1
}

# Activate virtual environment
Write-Host "`nActivating Python virtual environment..." -ForegroundColor Cyan
$venvPath = "backend/venv/Scripts/Activate.ps1"
if (Test-Path $venvPath) {
    & $venvPath
} else {
    Write-Host "Error: Virtual environment not found!" -ForegroundColor Red
    Write-Host "Run setup.ps1 first" -ForegroundColor Yellow
    exit 1
}

# Start the server
Write-Host "`n================================" -ForegroundColor Cyan
Write-Host "Starting Unified Server..." -ForegroundColor Green
Write-Host "================================" -ForegroundColor Cyan
Write-Host "`nAPI Documentation: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "Application: http://localhost:8000" -ForegroundColor Cyan
Write-Host "`nPress Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host "================================`n" -ForegroundColor Cyan

# Run the backend server
Push-Location backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
Pop-Location
