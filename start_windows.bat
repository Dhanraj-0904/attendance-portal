@echo off
echo ====================================================
echo NGO Attendance Portal - Starting Server
echo ====================================================

if not exist venv (
    echo [ERROR] Virtual environment 'venv' not found.
    echo Please run setup_windows.bat first to install dependencies.
    pause
    exit /b 1
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo ====================================================
echo   Server is starting! 
echo.
echo   - To access on this laptop: http://localhost:8000
echo.
echo   - To access on a phone (same WiFi):
echo     Find your IPv4 Address by looking at the output below:
ipconfig | findstr "IPv4 Address"
echo     Then open: http://[your-ip-address]:8000 on your phone.
echo.
echo   - Press Ctrl+C in this window to stop the server.
echo ====================================================
echo.

python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
pause
