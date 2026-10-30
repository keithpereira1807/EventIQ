@echo off
cd /d "%~dp0"
echo ===================================================
echo [EventIQ] Starting FastAPI Backend Service
echo ===================================================

REM Check for virtual environment, create if not present
if not exist "venv" (
    echo [INFO] Creating Python virtual environment (venv)...
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Python is not installed or not in PATH. Please install Python 3.10+.
        pause
        exit /b 1
    )
)

echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat

echo [INFO] Verifying backend dependencies...
pip install -r backend\requirements.txt

echo.
echo ===================================================
echo [EventIQ] Backend running at http://127.0.0.1:8000
echo [EventIQ] Swagger Docs at http://127.0.0.1:8000/docs
echo ===================================================
echo.

python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
pause
