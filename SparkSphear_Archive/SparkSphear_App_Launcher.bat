@echo off
title SparkSphear Tech - Fully Integrated (Smart Pricing SYNCED)
cd /d "%USERPROFILE%\Desktop"

echo ================================================================
echo   SPARKSPHEAR TECH - SMART PRICING INTEGRATED
echo ================================================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found in PATH
    echo Please install Python and add to PATH
    pause
    exit /b 1
)

echo [OK] Python found
echo [INFO] Launching FULLY integrated app...
echo.

REM Launch the FULLY integrated app
python "SparkSphear_Fully_Integrated.py"

REM Error handling
if errorlevel 1 (
    echo.
    echo [ERROR] App closed with an error
    echo Check messages above for details
    echo.
    pause
)
