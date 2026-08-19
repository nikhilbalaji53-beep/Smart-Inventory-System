@echo off
REM Smart Inventory System - Unified Server Setup Script (Batch version)
REM This script sets up both backend and frontend for a unified server

setlocal enabledelayedexpansion

echo.
echo ================================
echo Smart Inventory System - Setup
echo ================================
echo.

REM Check if we're in the correct directory
if not exist backend (
    echo Error: This script must be run from the project root directory!
    exit /b 1
)
if not exist frontend (
    echo Error: This script must be run from the project root directory!
    exit /b 1
)

REM Step 1: Backend Setup
echo [1/4] Setting up Backend...

if exist backend\venv (
    echo Virtual environment already exists
) else (
    echo Creating Python virtual environment...
    cd backend
    python -m venv venv
    if !errorlevel! neq 0 (
        echo Error: Failed to create virtual environment
        cd ..
        exit /b 1
    )
    cd ..
)

REM Activate virtual environment
echo Activating virtual environment...
call backend\venv\Scripts\activate.bat

REM Install backend dependencies
echo Installing backend dependencies...
if exist backend\requirements.txt (
    pip install -r backend\requirements.txt
    if !errorlevel! neq 0 (
        echo Error: Failed to install backend dependencies
        exit /b 1
    )
) else (
    echo Warning: requirements.txt not found!
)

echo Backend setup completed!

REM Step 2: Frontend Setup
echo.
echo [2/4] Setting up Frontend...

REM Check if Node.js is installed
node --version >nul 2>&1
if !errorlevel! neq 0 (
    echo Error: Node.js is not installed. Please install Node.js first.
    exit /b 1
)

REM Install frontend dependencies
cd frontend
if exist node_modules (
    echo node_modules already exists
) else (
    echo Installing frontend dependencies...
    call npm install
    if !errorlevel! neq 0 (
        echo Error: Failed to install frontend dependencies
        cd ..
        exit /b 1
    )
)

echo Frontend dependencies installed!

REM Step 3: Build Frontend
echo.
echo [3/4] Building Frontend...

call npm run build
if !errorlevel! neq 0 (
    echo Error: Frontend build failed
    cd ..
    exit /b 1
)

echo Frontend built successfully!
cd ..

REM Step 4: Verify Database Configuration
echo.
echo [4/4] Verifying Configuration...

if exist backend\.env (
    echo .env file found
) else (
    echo.
    echo Warning: .env file not found!
    echo Make sure to create a .env file in the backend directory with database credentials:
    echo   DB_USER=root
    echo   DB_PASSWORD=your_password
    echo   DB_HOST=localhost
    echo   DB_PORT=3306
    echo   DB_NAME=smart_inventory
)

echo.
echo ================================
echo Setup completed successfully!
echo ================================
echo.
echo Next steps:
echo 1. Ensure MySQL is running
echo 2. Run: run-server.bat
echo 3. Open browser to http://localhost:8000
echo.
