@echo off
echo ========================================
echo Starting AI Email Assistant
echo ========================================
echo.

REM Check if we're in the correct directory
if not exist "ai-email-assistant" (
    echo Error: Please run this script from the email-agent root directory
    pause
    exit /b 1
)

echo [1/4] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    pause
    exit /b 1
)

echo [2/4] Checking Node.js installation...
node --version >nul 2>&1
if errorlevel 1 (
    echo Error: Node.js is not installed or not in PATH
    pause
    exit /b 1
)

echo [3/4] Starting Backend Server...
cd ai-email-assistant\backend
start "Backend Server" cmd /k "python main.py"
cd ..\..

echo [4/4] Starting Frontend Server...
cd ai-email-assistant\frontend
start "Frontend Server" cmd /k "npm run dev"
cd ..\..

echo.
echo ========================================
echo Both servers are starting!
echo ========================================
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:5173
echo ========================================
echo.
echo Press any key to close this window...
pause >nul
