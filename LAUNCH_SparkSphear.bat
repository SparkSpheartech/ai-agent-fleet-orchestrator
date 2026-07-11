@echo off
title SparkSphear Tech - Smart Pricing (READY for 1:30 PM visit)
cd /d "%USERPROFILE%\Desktop"

echo ================================================================
echo   SPARKSPHEAR TECH - SMART PRICING APP
echo ================================================================
echo.
echo [INFO] Launching app for TODAY'S 1:30 PM visit...
echo [INFO] Client: 2523 Caroline St, Fort Wayne, IN
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found!
    echo Please install Python and add to PATH
    pause
    exit /b 1
)

echo [OK] Python found
echo [INFO] Starting app in 3 seconds...
timeout /t 3 >nul

REM Launch the app
start "SparkSphear App" python "SparkSphear_Simple_Working.py"

echo.
echo [SUCCESS] App launched!
echo [INFO] App window should be open now
echo.
echo If app doesn't open, check:
echo   1. Python is installed
echo   2. File "SparkSphear_Simple_Working.py" is on Desktop
echo.
pause
