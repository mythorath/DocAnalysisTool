#!/usr/bin/env python3
"""
create_shortcuts.py - Create desktop shortcuts and system integration

Creates shortcuts, start menu entries, and system integration
for easy access to the Public Comment Analysis Tool.
"""

import os
import sys
import platform
import subprocess
from pathlib import Path
import tkinter as tk
from tkinter import messagebox


def create_windows_shortcuts():
    """Create Windows shortcuts and start menu entries."""
    try:
        import winshell
        from win32com.client import Dispatch
    except ImportError:
        print("Installing Windows shortcut dependencies...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "winshell", "pywin32"])
        import winshell
        from win32com.client import Dispatch
    
    current_dir = Path.cwd()
    
    # Desktop shortcut
    desktop = winshell.desktop()
    shortcut_path = Path(desktop) / "Public Comment Analysis Tool.lnk"
    
    shell = Dispatch('WScript.Shell')
    shortcut = shell.CreateShortCut(str(shortcut_path))
    shortcut.Targetpath = str(current_dir / "launch_gui.bat")
    shortcut.WorkingDirectory = str(current_dir)
    shortcut.IconLocation = str(current_dir / "gui_app.py")
    shortcut.Description = "Public Comment Analysis Tool - AI-powered document analysis"
    shortcut.save()
    
    print(f"✅ Desktop shortcut created: {shortcut_path}")
    
    # Start menu shortcut
    try:
        start_menu = winshell.start_menu()
        programs_path = Path(start_menu) / "Programs" / "Public Comment Analysis Tool"
        programs_path.mkdir(exist_ok=True)
        
        start_shortcut_path = programs_path / "Public Comment Analysis Tool.lnk"
        start_shortcut = shell.CreateShortCut(str(start_shortcut_path))
        start_shortcut.Targetpath = str(current_dir / "launch_gui.bat")
        start_shortcut.WorkingDirectory = str(current_dir)
        start_shortcut.IconLocation = str(current_dir / "gui_app.py")
        start_shortcut.Description = "Public Comment Analysis Tool - AI-powered document analysis"
        start_shortcut.save()
        
        # Create additional shortcuts
        cli_shortcut_path = programs_path / "Command Line Interface.lnk"
        cli_shortcut = shell.CreateShortCut(str(cli_shortcut_path))
        cli_shortcut.Targetpath = "cmd.exe"
        cli_shortcut.Arguments = f'/k "cd /d "{current_dir}" && python main.py --help"'
        cli_shortcut.WorkingDirectory = str(current_dir)
        cli_shortcut.Description = "Public Comment Analysis Tool - Command Line"
        cli_shortcut.save()
        
        help_shortcut_path = programs_path / "User Guide.lnk"
        help_shortcut = shell.CreateShortCut(str(help_shortcut_path))
        help_shortcut.Targetpath = str(current_dir / "GUI_USER_GUIDE.md")
        help_shortcut.WorkingDirectory = str(current_dir)
        help_shortcut.Description = "Public Comment Analysis Tool - User Guide"
        help_shortcut.save()
        
        print(f"✅ Start menu shortcuts created: {programs_path}")
        
    except Exception as e:
        print(f"⚠️  Start menu shortcut failed: {str(e)}")
    
    # File association (optional)
    try:
        create_windows_file_association()
    except Exception as e:
        print(f"⚠️  File association failed: {str(e)}")


def create_windows_file_association():
    """Create file association for CSV files (optional)."""
    import winreg
    
    current_dir = Path.cwd()
    
    # Create file type
    with winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\Classes\.pcat") as key:
        winreg.SetValueEx(key, "", 0, winreg.REG_SZ, "PublicCommentAnalysisTool")
    
    # Create command
    with winreg.CreateKey(winreg.HKEY_CURRENT_USER, 
                         r"Software\Classes\PublicCommentAnalysisTool\shell\open\command") as key:
        command = f'"{sys.executable}" "{current_dir / "gui_app.py"}" "%1"'
        winreg.SetValueEx(key, "", 0, winreg.REG_SZ, command)
    
    # Create description
    with winreg.CreateKey(winreg.HKEY_CURRENT_USER, 
                         r"Software\Classes\PublicCommentAnalysisTool") as key:
        winreg.SetValueEx(key, "", 0, winreg.REG_SZ, "Public Comment Analysis Tool Project")
    
    print("✅ File association created for .pcat files")


def create_linux_shortcuts():
    """Create Linux desktop shortcuts and menu entries."""
    current_dir = Path.cwd()
    
    # Desktop shortcut
    desktop_file_content = f"""[Desktop Entry]
Name=Public Comment Analysis Tool
Comment=AI-powered document analysis and clustering
Exec=python3 {current_dir}/gui_app.py
Path={current_dir}
Icon={current_dir}/icon.png
Type=Application
Categories=Office;Education;
Terminal=false
StartupNotify=true
MimeType=text/csv;
"""
    
    # Create desktop shortcut
    desktop_path = Path.home() / "Desktop" / "Public Comment Analysis Tool.desktop"
    try:
        desktop_path.write_text(desktop_file_content)
        desktop_path.chmod(0o755)
        print(f"✅ Desktop shortcut created: {desktop_path}")
    except Exception as e:
        print(f"⚠️  Desktop shortcut failed: {str(e)}")
    
    # Create application menu entry
    applications_dir = Path.home() / ".local" / "share" / "applications"
    applications_dir.mkdir(parents=True, exist_ok=True)
    
    app_file_path = applications_dir / "public-comment-analysis-tool.desktop"
    try:
        app_file_path.write_text(desktop_file_content)
        app_file_path.chmod(0o755)
        
        # Update desktop database
        try:
            subprocess.run(["update-desktop-database", str(applications_dir)], 
                          capture_output=True, check=False)
        except:
            pass
        
        print(f"✅ Application menu entry created: {app_file_path}")
    except Exception as e:
        print(f"⚠️  Application menu entry failed: {str(e)}")
    
    # Create launcher script
    launcher_script = current_dir / "launch_analysis_tool.sh"
    launcher_content = f"""#!/bin/bash
cd "{current_dir}"
python3 gui_app.py "$@"
"""
    try:
        launcher_script.write_text(launcher_content)
        launcher_script.chmod(0o755)
        print(f"✅ Launcher script created: {launcher_script}")
    except Exception as e:
        print(f"⚠️  Launcher script failed: {str(e)}")


def create_macos_shortcuts():
    """Create macOS shortcuts and Dock integration."""
    current_dir = Path.cwd()
    
    # Create AppleScript application
    app_script = f"""
on run
    tell application "Terminal"
        do script "cd '{current_dir}' && python3 gui_app.py"
    end tell
end run

on open theFiles
    repeat with aFile in theFiles
        tell application "Terminal"
            do script "cd '{current_dir}' && python3 gui_app.py '" & POSIX path of aFile & "'"
        end tell
    end repeat
end open
"""
    
    # Create .app bundle
    app_bundle = current_dir / "Public Comment Analysis Tool.app"
    contents_dir = app_bundle / "Contents"
    macos_dir = contents_dir / "MacOS"
    resources_dir = contents_dir / "Resources"
    
    try:
        macos_dir.mkdir(parents=True, exist_ok=True)
        resources_dir.mkdir(parents=True, exist_ok=True)
        
        # Create Info.plist
        info_plist = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>launch</string>
    <key>CFBundleIdentifier</key>
    <string>com.publiccomment.analysistool</string>
    <key>CFBundleName</key>
    <string>Public Comment Analysis Tool</string>
    <key>CFBundleDisplayName</key>
    <string>Public Comment Analysis Tool</string>
    <key>CFBundleVersion</key>
    <string>1.0</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.14</string>
    <key>CFBundleDocumentTypes</key>
    <array>
        <dict>
            <key>CFBundleTypeExtensions</key>
            <array>
                <string>csv</string>
            </array>
            <key>CFBundleTypeName</key>
            <string>CSV File</string>
            <key>CFBundleTypeRole</key>
            <string>Editor</string>
        </dict>
    </array>
</dict>
</plist>"""
        
        (contents_dir / "Info.plist").write_text(info_plist)
        
        # Create launcher script
        launcher = f"""#!/bin/bash
cd "{current_dir}"
python3 gui_app.py "$@"
"""
        
        launcher_path = macos_dir / "launch"
        launcher_path.write_text(launcher)
        launcher_path.chmod(0o755)
        
        print(f"✅ macOS app bundle created: {app_bundle}")
        
    except Exception as e:
        print(f"⚠️  macOS app bundle failed: {str(e)}")
    
    # Create simple launcher script
    launcher_script = current_dir / "launch_analysis_tool.command"
    launcher_content = f"""#!/bin/bash
cd "{current_dir}"
python3 gui_app.py
"""
    try:
        launcher_script.write_text(launcher_content)
        launcher_script.chmod(0o755)
        print(f"✅ macOS launcher script created: {launcher_script}")
    except Exception as e:
        print(f"⚠️  macOS launcher script failed: {str(e)}")


def create_uninstaller():
    """Create uninstaller script."""
    current_dir = Path.cwd()
    system = platform.system()
    
    if system == "Windows":
        uninstaller = current_dir / "UNINSTALL.bat"
        uninstall_content = f"""@echo off
echo ========================================
echo   PUBLIC COMMENT ANALYSIS TOOL
echo          Uninstaller
echo ========================================
echo.

echo This will remove the Public Comment Analysis Tool and all its files.
echo Your data files (CSV, downloaded documents) will be preserved.
echo.
set /p confirm="Are you sure you want to uninstall? (y/N): "
if /i not "%confirm%"=="y" goto :cancel

echo.
echo Removing shortcuts...
del "%USERPROFILE%\\Desktop\\Public Comment Analysis Tool.lnk" 2>nul
rmdir /s /q "%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\Public Comment Analysis Tool" 2>nul

echo Removing application files...
cd ..
rmdir /s /q "{current_dir.name}" 2>nul

echo.
echo ✅ Uninstallation completed.
echo Your data files have been preserved.
pause
exit /b 0

:cancel
echo Uninstallation cancelled.
pause
exit /b 1
"""
        
    else:  # Linux/macOS
        uninstaller = current_dir / "UNINSTALL.sh"
        uninstall_content = f"""#!/bin/bash
echo "========================================"
echo "  PUBLIC COMMENT ANALYSIS TOOL"
echo "         Uninstaller"
echo "========================================"
echo

echo "This will remove the Public Comment Analysis Tool and all its files."
echo "Your data files (CSV, downloaded documents) will be preserved."
echo
read -p "Are you sure you want to uninstall? (y/N): " confirm

if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
    echo "Uninstallation cancelled."
    exit 1
fi

echo
echo "Removing shortcuts..."
rm -f "$HOME/Desktop/Public Comment Analysis Tool.desktop" 2>/dev/null
rm -f "$HOME/.local/share/applications/public-comment-analysis-tool.desktop" 2>/dev/null
rm -f "{current_dir}/Public Comment Analysis Tool.app" 2>/dev/null
rm -f "{current_dir}/launch_analysis_tool.command" 2>/dev/null

echo "Removing application files..."
cd ..
rm -rf "{current_dir.name}" 2>/dev/null

echo
echo "✅ Uninstallation completed."
echo "Your data files have been preserved."
read -p "Press any key to continue..."
"""
    
    try:
        uninstaller.write_text(uninstall_content)
        if system != "Windows":
            uninstaller.chmod(0o755)
        print(f"✅ Uninstaller created: {uninstaller}")
    except Exception as e:
        print(f"⚠️  Uninstaller creation failed: {str(e)}")


def main():
    """Main shortcut creation entry point."""
    print("🔗 Creating shortcuts and system integration...")
    
    system = platform.system()
    
    try:
        if system == "Windows":
            create_windows_shortcuts()
        elif system == "Linux":
            create_linux_shortcuts()
        elif system == "Darwin":  # macOS
            create_macos_shortcuts()
        else:
            print(f"⚠️  Unsupported system: {system}")
            return
        
        # Create uninstaller for all systems
        create_uninstaller()
        
        print("\n✅ Shortcut creation completed!")
        print("\n🚀 You can now launch the application from:")
        
        if system == "Windows":
            print("  • Desktop shortcut: 'Public Comment Analysis Tool'")
            print("  • Start Menu: Programs → Public Comment Analysis Tool")
            print("  • Direct: Double-click launch_gui.bat")
        elif system == "Linux":
            print("  • Desktop shortcut: 'Public Comment Analysis Tool'")
            print("  • Application menu: Office → Public Comment Analysis Tool")
            print("  • Terminal: ./launch_analysis_tool.sh")
        elif system == "Darwin":
            print("  • Finder: Public Comment Analysis Tool.app")
            print("  • Terminal: ./launch_analysis_tool.command")
            print("  • Direct: python3 gui_app.py")
    
    except Exception as e:
        print(f"❌ Shortcut creation failed: {str(e)}")
        print("You can still launch the application manually:")
        print("  • Windows: python gui_app.py")
        print("  • Linux/macOS: python3 gui_app.py")


if __name__ == "__main__":
    # Check if running in GUI mode
    try:
        root = tk.Tk()
        root.withdraw()  # Hide main window
        
        result = messagebox.askquestion("Create Shortcuts", 
                                       "Create desktop shortcuts and system integration for easy access to the Public Comment Analysis Tool?")
        
        if result == 'yes':
            main()
            messagebox.showinfo("Shortcuts Created", 
                              "Shortcuts have been created successfully!\n\n"
                              "You can now launch the application from your desktop or start menu.")
        else:
            print("Shortcut creation cancelled by user.")
        
        root.destroy()
        
    except:
        # Fallback to command line
        main()


if __name__ == "__main__":
    main()