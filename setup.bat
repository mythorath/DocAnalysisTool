@echo off
echo 🚀 Document Analysis Platform Setup (Windows)
echo ===============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

echo ✅ Python found
echo.

REM Run the setup script
echo 🔧 Running setup script...
python setup.py

echo.
echo 📋 To activate your environment later, run:
echo    venv\Scripts\activate
echo.
echo 🎉 Setup complete! Check the output above for your portal URL.
pause

