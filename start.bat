@echo off
echo 🚀 Starting Document Analysis Platform Manager
echo.
echo Activating virtual environment...
call venv\Scripts\activate
echo.
echo Starting interactive manager...
python interactive_manager.py
pause
