@echo off
REM Uninstaller for Public Comment Analysis Tool
echo ========================================
echo   PUBLIC COMMENT ANALYSIS TOOL
echo          Uninstaller
echo ========================================
echo.

echo This will remove the Public Comment Analysis Tool.
echo.
echo ⚠️  IMPORTANT: Your data files will be preserved:
echo   • input/        (your CSV files)
echo   • downloads/    (downloaded documents)  
echo   • text/         (extracted text)
echo   • output/       (results and database)
echo   • logs/         (processing logs)
echo.

set /p confirm="Continue with uninstallation? (y/N): "
if /i not "%confirm%"=="y" goto :cancel

echo.
echo 🧹 Cleaning up shortcuts...
del "%USERPROFILE%\Desktop\Public Comment Analysis Tool.lnk" 2>nul
rmdir /s /q "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Public Comment Analysis Tool" 2>nul

echo 🗑️  Removing application files...
del gui_app.py 2>nul
del main.py 2>nul
del downloader.py 2>nul
del extractor.py 2>nul
del indexer.py 2>nul
del grouper.py 2>nul
del INSTALL.py 2>nul
del INSTALL.bat 2>nul
del setup_wizard.py 2>nul
del create_shortcuts.py 2>nul
del launch_gui.bat 2>nul
del requirements.txt 2>nul
del README*.md 2>nul
del GUI_USER_GUIDE.md 2>nul
del .gitignore 2>nul
rmdir /s /q shortcuts 2>nul
rmdir /s /q .git 2>nul

echo 📋 Preserving your data...
echo   ✅ Keeping: input/, downloads/, text/, output/, logs/
echo   ✅ Your CSV files and results are safe

echo.
echo ✅ Uninstallation completed successfully!
echo.
echo 📁 Your data files remain in:
echo   %CD%\input\
echo   %CD%\downloads\
echo   %CD%\text\
echo   %CD%\output\
echo   %CD%\logs\
echo.
echo 💡 To reinstall: Download the tool again and run INSTALL.bat
echo.
pause
goto :end

:cancel
echo Uninstallation cancelled by user.
pause

:end
del "%~f0" 2>nul & exit /b 0