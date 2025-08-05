@echo off
REM Launch script for Public Comment Analysis Tool GUI
echo Starting Public Comment Analysis Tool...
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.8+ first.
    pause
    exit /b 1
)

REM Check if required modules are available
python -c "import tkinter" >nul 2>&1
if errorlevel 1 (
    echo ERROR: tkinter not available. Please install complete Python package.
    pause
    exit /b 1
)

REM Launch the GUI application
echo Launching GUI application...
python gui_app.py

REM Keep window open if there was an error
if errorlevel 1 (
    echo.
    echo Application closed with an error. Check the messages above.
    pause
)