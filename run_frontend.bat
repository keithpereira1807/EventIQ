@echo off
cd /d "%~dp0frontend"
echo ===================================================
echo [EventIQ] Starting React + Vite Frontend
echo ===================================================

REM Check for node_modules, install if missing
if not exist "node_modules" (
    echo [INFO] Installing frontend packages (first run only)...
    call npm.cmd install
    if errorlevel 1 (
        echo [ERROR] npm install failed. Ensure Node.js is installed.
        pause
        exit /b 1
    )
)

echo.
echo ===================================================
echo [EventIQ] Frontend UI: http://localhost:5173
echo ===================================================
echo.

call npm.cmd run dev
pause
