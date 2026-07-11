@echo off
title SparkSphear Tech - Smart Pricing App
cd /d "%USERPROFILE%\Desktop\SparkSphear_App"

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
echo [INFO] Starting app...
echo.

REM Launch the app
python "SparkSphear_Simple_Working.py"

REM Error handling
if errorlevel 1 (
    echo.
    echo [ERROR] App closed with an error
    echo Check messages above
    echo.
    pause
)
