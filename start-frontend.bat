@echo off
echo Starting Frontend Server...
cd ai-email-assistant\frontend

REM Install dependencies if node_modules doesn't exist
if not exist "node_modules" (
    echo Installing dependencies...
    npm install
)

echo.
echo ========================================
echo Frontend Server Starting...
echo URL: http://localhost:5173
echo ========================================
echo.

npm run dev
