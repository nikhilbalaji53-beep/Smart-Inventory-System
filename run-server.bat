@echo off
REM Smart Inventory System - Unified Server Run Script (Batch version)
REM This script runs both backend and frontend from a single server

setlocal enabledelayedexpansion

echo.
echo ================================
echo Smart Inventory System - Server
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

REM Check if frontend is built
if not exist frontend\dist (
    echo Error: Frontend is not built!
    echo Run: npm run build
    echo from the frontend directory first
    exit /b 1
)

REM Activate virtual environment
echo Activating Python virtual environment...
if exist backend\venv\Scripts\activate.bat (
    call backend\venv\Scripts\activate.bat
) else (
    echo Error: Virtual environment not found!
    echo Run setup.bat first
    exit /b 1
)

REM Start the server
echo.
echo ================================
echo Starting Unified Server...
echo ================================
echo.
echo API Documentation: http://localhost:8000/docs
echo Application: http://localhost:8000
echo.
echo Press Ctrl+C to stop the server
echo ================================
echo.

REM Run the backend server
cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
cd ..
