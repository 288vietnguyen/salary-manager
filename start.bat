@echo off
setlocal

set ROOT=%~dp0

echo === Salary Manager ===

:: Kill any process still holding port 8080
echo [0/3] Clearing port 8080...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8080 " ^| findstr "LISTENING"') do (
    echo   Killing PID %%a
    taskkill /PID %%a /F >nul 2>&1
)

:: Create virtual environment if it doesn't exist
if not exist "%ROOT%venv\" (
    echo [1/3] Creating virtual environment...
    python -m venv "%ROOT%venv"
)

:: Install / update dependencies
echo [2/3] Installing dependencies...
"%ROOT%venv\Scripts\pip" install --quiet --upgrade pip
"%ROOT%venv\Scripts\pip" install --quiet -r "%ROOT%requirements.txt"

:: Create models directory if missing
if not exist "%ROOT%backend\models\" mkdir "%ROOT%backend\models"

:: Start server
echo [3/3] Starting server at http://localhost:8080
cd "%ROOT%backend"
"%ROOT%venv\Scripts\python" -m uvicorn main:app --host 127.0.0.1 --port 8080 --reload

pause
