@echo off
REM One-Click Installer for Public Comment Analysis Tool
REM This script automatically installs everything needed

echo ========================================
echo   PUBLIC COMMENT ANALYSIS TOOL
echo         One-Click Installer
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERROR: Python not found!
    echo.
    echo Please install Python 3.8+ first from:
    echo https://www.python.org/downloads/
    echo.
    echo Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

echo ✅ Python found - starting installation...
echo.

REM Run the Python installer
python INSTALL.py

REM Check if installation was successful
if errorlevel 1 (
    echo.
    echo ❌ Installation encountered errors.
    echo Check the messages above for details.
    echo.
    pause
    exit /b 1
)

echo.
echo ✅ Installation completed successfully!
echo.
echo 🚀 To start the application:
echo   - Double-click "shortcuts\Launch_Analysis_Tool.bat"
echo   - Or run: python gui_app.py
echo.
pause