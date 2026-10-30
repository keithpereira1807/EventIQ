@echo off
cd /d "%~dp0"
echo ===================================================
echo [EventIQ] Starting Streamlit Interactive App
echo ===================================================

if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)

streamlit run streamlit_app.py
pause
