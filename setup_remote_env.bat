@echo off
echo Setting up remote management environment variables...

REM Set your Railway portal URL
set PORTAL_URL=https://narrow-clocks-staging.up.railway.app

REM Set your admin API key (change this to something secure!)
set ADMIN_API_KEY=your_secure_admin_key_change_me_123

echo ✅ Environment variables set!
echo.
echo PORTAL_URL: %PORTAL_URL%
echo ADMIN_API_KEY: %ADMIN_API_KEY%
echo.
echo Now you can run:
echo   python remote_data_manager.py test
echo   python remote_data_manager.py list
echo   python remote_data_manager.py upload database.db customer@email.com "Project"
echo.
pause
