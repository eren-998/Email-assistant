@echo off
echo Starting Backend Server...
cd ai-email-assistant\backend

REM Check if virtual environment exists
if exist "venv" (
    echo Activating virtual environment...
    call venv\Scripts\activate
)

REM Install dependencies if needed
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    call venv\Scripts\activate
    echo Installing dependencies...
    pip install -r requirements.txt
)

echo.
echo ========================================
echo Backend Server Starting...
echo URL: http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo ========================================
echo.

python main.py
