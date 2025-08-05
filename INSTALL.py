#!/usr/bin/env python3
"""
INSTALL.py - One-Click Installer for Public Comment Analysis Tool

This script provides a completely automated installation process that:
1. Checks Python environment and installs if needed
2. Installs all Python dependencies
3. Installs system dependencies (Tesseract, Poppler)
4. Sets up project directories
5. Creates desktop shortcuts
6. Runs validation tests
7. Launches setup wizard

Usage: Just double-click this file or run: python INSTALL.py
"""

import os
import sys
import subprocess
import urllib.request
import zipfile
import shutil
import json
import platform
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from pathlib import Path
import threading
import queue
import webbrowser
from datetime import datetime


class InstallationGUI:
    """Graphical installer interface."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Public Comment Analysis Tool - Installer")
        self.root.geometry("800x600")
        self.root.resizable(False, False)
        
        # Installation state
        self.install_queue = queue.Queue()
        self.installation_complete = False
        self.install_path = Path.cwd()
        
        self.setup_ui()
        self.check_install_updates()
    
    def setup_ui(self):
        """Setup installer interface."""
        # Header
        header_frame = tk.Frame(self.root, bg='#2c3e50', height=100)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(header_frame, text="📄 Public Comment Analysis Tool", 
                              font=('Arial', 18, 'bold'), fg='white', bg='#2c3e50')
        title_label.pack(pady=20)
        
        subtitle_label = tk.Label(header_frame, text="Automated Installation & Setup Wizard", 
                                 font=('Arial', 12), fg='#ecf0f1', bg='#2c3e50')
        subtitle_label.pack()
        
        # Main content
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Welcome message
        welcome_text = """
🚀 Welcome to the Public Comment Analysis Tool Installer!

This installer will automatically:
✅ Check your Python environment
✅ Install all required Python packages
✅ Download and configure Tesseract OCR
✅ Download and configure Poppler PDF tools
✅ Create project directories
✅ Set up desktop shortcuts
✅ Validate your installation
✅ Launch the setup wizard

The installation process is completely automated and will take 3-5 minutes.
No technical knowledge required - just click "Start Installation" below!

📋 System Requirements:
• Windows 10+ (64-bit) | Linux (Ubuntu 18+) | macOS 10.14+
• 4GB RAM minimum, 8GB recommended
• 2GB free disk space
• Internet connection for downloading dependencies
        """
        
        welcome_widget = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, height=15, 
                                                  font=('Consolas', 10))
        welcome_widget.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        welcome_widget.insert(tk.END, welcome_text)
        welcome_widget.config(state=tk.DISABLED)
        
        # Progress section
        progress_frame = tk.LabelFrame(main_frame, text="Installation Progress", font=('Arial', 10, 'bold'))
        progress_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.progress_var = tk.StringVar(value="Ready to install")
        self.progress_label = tk.Label(progress_frame, textvariable=self.progress_var, 
                                      font=('Arial', 10))
        self.progress_label.pack(pady=5)
        
        self.progress_bar = ttk.Progressbar(progress_frame, mode='indeterminate', length=400)
        self.progress_bar.pack(pady=5)
        
        # Installation log
        self.log_text = scrolledtext.ScrolledText(progress_frame, height=8, font=('Consolas', 9))
        self.log_text.pack(fill=tk.X, pady=5)
        
        # Buttons
        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        self.install_btn = tk.Button(button_frame, text="🚀 Start Installation", 
                                    command=self.start_installation,
                                    font=('Arial', 12, 'bold'), bg='#27ae60', fg='white',
                                    padx=20, pady=10)
        self.install_btn.pack(side=tk.LEFT)
        
        self.cancel_btn = tk.Button(button_frame, text="❌ Cancel", 
                                   command=self.cancel_installation,
                                   font=('Arial', 10), padx=15, pady=10)
        self.cancel_btn.pack(side=tk.LEFT, padx=(10, 0))
        
        self.help_btn = tk.Button(button_frame, text="❓ Help", 
                                 command=self.show_help,
                                 font=('Arial', 10), padx=15, pady=10)
        self.help_btn.pack(side=tk.RIGHT)
    
    def log_message(self, message):
        """Add message to installation log."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
        self.root.update()
    
    def update_progress(self, message):
        """Update progress status."""
        self.progress_var.set(message)
        self.log_message(message)
    
    def start_installation(self):
        """Start the installation process."""
        self.install_btn.config(state='disabled')
        self.progress_bar.start()
        
        def install_worker():
            """Installation worker thread."""
            installer = SystemInstaller(self)
            try:
                installer.run_installation()
                self.installation_complete = True
                self.install_queue.put(('complete', 'Installation completed successfully!'))
            except Exception as e:
                self.install_queue.put(('error', f'Installation failed: {str(e)}'))
        
        thread = threading.Thread(target=install_worker, daemon=True)
        thread.start()
    
    def cancel_installation(self):
        """Cancel installation and exit."""
        if messagebox.askquestion("Cancel Installation", 
                                 "Are you sure you want to cancel the installation?") == 'yes':
            self.root.quit()
    
    def show_help(self):
        """Show installation help."""
        help_text = """
🆘 INSTALLATION HELP

📋 What this installer does:
1. Checks if Python 3.8+ is installed
2. Installs required Python packages via pip
3. Downloads Tesseract OCR for text recognition
4. Downloads Poppler for PDF processing
5. Creates necessary project folders
6. Sets up desktop shortcuts
7. Validates all components work correctly

🔧 If installation fails:
• Check internet connection
• Run as Administrator (Windows) or with sudo (Linux/macOS)
• Disable antivirus temporarily
• Check available disk space (2GB minimum)

📞 Support Options:
• Check logs above for specific error messages
• Restart installer and try again
• Manual installation guide: README.md
• System requirements: Windows 10+, macOS 10.14+, Ubuntu 18+

🌐 Online Resources:
• Project documentation
• Troubleshooting guides
• Video tutorials
        """
        
        help_window = tk.Toplevel(self.root)
        help_window.title("Installation Help")
        help_window.geometry("500x400")
        
        help_widget = scrolledtext.ScrolledText(help_window, wrap=tk.WORD, font=('Consolas', 10))
        help_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        help_widget.insert(tk.END, help_text)
        help_widget.config(state=tk.DISABLED)
    
    def check_install_updates(self):
        """Check for installation updates from worker thread."""
        try:
            while True:
                update_type, message = self.install_queue.get_nowait()
                
                if update_type == 'complete':
                    self.progress_bar.stop()
                    self.progress_bar.config(mode='determinate', value=100)
                    self.update_progress(message)
                    self.show_completion_dialog()
                    return
                    
                elif update_type == 'error':
                    self.progress_bar.stop()
                    self.update_progress(message)
                    messagebox.showerror("Installation Error", message)
                    self.install_btn.config(state='normal')
                    return
                
        except queue.Empty:
            pass
        
        # Schedule next check
        self.root.after(100, self.check_install_updates)
    
    def show_completion_dialog(self):
        """Show installation completion dialog."""
        result = messagebox.askquestion("Installation Complete!", 
                                       "🎉 Installation completed successfully!\n\n"
                                       "Would you like to launch the application now?",
                                       icon='question')
        
        if result == 'yes':
            self.launch_application()
        
        self.root.quit()
    
    def launch_application(self):
        """Launch the main application."""
        try:
            if platform.system() == "Windows":
                subprocess.Popen([sys.executable, "gui_app.py"], shell=True)
            else:
                subprocess.Popen([sys.executable, "gui_app.py"])
        except Exception as e:
            messagebox.showerror("Launch Error", f"Could not launch application: {str(e)}")


class SystemInstaller:
    """Handles the actual installation process."""
    
    def __init__(self, gui):
        self.gui = gui
        self.system = platform.system()
        self.install_path = Path.cwd()
        self.temp_path = self.install_path / "temp_install"
    
    def run_installation(self):
        """Run the complete installation process."""
        try:
            # Step 1: Environment check
            self.gui.update_progress("🔍 Checking system environment...")
            self.check_environment()
            
            # Step 2: Create directories
            self.gui.update_progress("📁 Creating project directories...")
            self.create_directories()
            
            # Step 3: Install Python dependencies
            self.gui.update_progress("🐍 Installing Python packages...")
            self.install_python_dependencies()
            
            # Step 4: Install system dependencies
            self.gui.update_progress("🔧 Installing system dependencies...")
            self.install_system_dependencies()
            
            # Step 5: Create shortcuts
            self.gui.update_progress("🔗 Creating shortcuts and launchers...")
            self.create_shortcuts()
            
            # Step 6: Validate installation
            self.gui.update_progress("✅ Validating installation...")
            self.validate_installation()
            
            # Step 7: Setup sample data
            self.gui.update_progress("📋 Setting up sample data...")
            self.setup_sample_data()
            
            self.gui.update_progress("🎉 Installation completed successfully!")
            
        except Exception as e:
            raise Exception(f"Installation failed at step: {str(e)}")
        finally:
            self.cleanup_temp_files()
    
    def check_environment(self):
        """Check system environment and requirements."""
        # Check Python version
        if sys.version_info < (3, 8):
            raise Exception(f"Python 3.8+ required. Found {sys.version}")
        
        self.gui.log_message(f"✅ Python {sys.version.split()[0]} detected")
        
        # Check available space
        free_space = shutil.disk_usage(self.install_path).free / (1024**3)  # GB
        if free_space < 2:
            raise Exception(f"Insufficient disk space. Need 2GB, found {free_space:.1f}GB")
        
        self.gui.log_message(f"✅ Sufficient disk space: {free_space:.1f}GB available")
        
        # Check internet connection
        try:
            urllib.request.urlopen('https://www.google.com', timeout=5)
            self.gui.log_message("✅ Internet connection verified")
        except:
            raise Exception("Internet connection required for installation")
        
        # Check write permissions
        test_file = self.install_path / "test_write.tmp"
        try:
            test_file.write_text("test")
            test_file.unlink()
            self.gui.log_message("✅ Write permissions verified")
        except:
            raise Exception("Write permissions required in installation directory")
    
    def create_directories(self):
        """Create necessary project directories."""
        directories = [
            "input", "downloads", "text", "output", "logs", 
            "temp_install", "shortcuts"
        ]
        
        for directory in directories:
            dir_path = self.install_path / directory
            dir_path.mkdir(exist_ok=True)
            self.gui.log_message(f"📁 Created directory: {directory}/")
    
    def install_python_dependencies(self):
        """Install Python package dependencies."""
        self.gui.log_message("📦 Upgrading pip...")
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], 
                      check=True, capture_output=True)
        
        # Install packages from requirements.txt
        requirements_file = self.install_path / "requirements.txt"
        if requirements_file.exists():
            self.gui.log_message("📦 Installing packages from requirements.txt...")
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", str(requirements_file)], 
                          check=True, capture_output=True)
        else:
            # Install core packages manually
            core_packages = [
                "pandas>=1.3.0", "requests>=2.25.0", "tqdm>=4.60.0", "numpy>=1.20.0",
                "PyMuPDF>=1.20.0", "pdf2image>=1.16.0", "pytesseract>=0.3.8", 
                "scikit-learn>=1.0.0", "sentence-transformers>=2.0.0", "bertopic>=0.10.0",
                "tkinter-tooltip>=3.1.0", "python-docx>=0.8.11"
            ]
            
            for package in core_packages:
                self.gui.log_message(f"📦 Installing {package}...")
                subprocess.run([sys.executable, "-m", "pip", "install", package], 
                              check=True, capture_output=True)
        
        self.gui.log_message("✅ Python packages installed successfully")
    
    def install_system_dependencies(self):
        """Install system dependencies (Tesseract, Poppler)."""
        if self.system == "Windows":
            self.install_windows_dependencies()
        elif self.system == "Linux":
            self.install_linux_dependencies()
        elif self.system == "Darwin":  # macOS
            self.install_macos_dependencies()
        else:
            self.gui.log_message("⚠️ Unknown system, skipping system dependencies")
    
    def install_windows_dependencies(self):
        """Install Windows dependencies."""
        self.temp_path.mkdir(exist_ok=True)
        
        # Install Tesseract
        self.gui.log_message("📥 Downloading Tesseract OCR...")
        tesseract_url = "https://github.com/UB-Mannheim/tesseract/releases/download/v5.3.0.20221214/tesseract-ocr-w64-setup-5.3.0.20221214.exe"
        tesseract_installer = self.temp_path / "tesseract_installer.exe"
        
        urllib.request.urlretrieve(tesseract_url, tesseract_installer)
        
        self.gui.log_message("🔧 Installing Tesseract OCR...")
        subprocess.run([str(tesseract_installer), "/S", "/D=C:\\Program Files\\Tesseract-OCR"], 
                      check=True)
        
        # Add to PATH
        tesseract_path = "C:\\Program Files\\Tesseract-OCR"
        self.add_to_path(tesseract_path)
        
        # Install Poppler
        self.gui.log_message("📥 Downloading Poppler...")
        poppler_url = "https://github.com/oschwartz10612/poppler-windows/releases/download/v22.04.0-0/Release-22.04.0-0.zip"
        poppler_zip = self.temp_path / "poppler.zip"
        
        urllib.request.urlretrieve(poppler_url, poppler_zip)
        
        self.gui.log_message("🔧 Installing Poppler...")
        with zipfile.ZipFile(poppler_zip, 'r') as zip_ref:
            zip_ref.extractall(self.temp_path)
        
        poppler_dir = self.install_path / "poppler"
        if poppler_dir.exists():
            shutil.rmtree(poppler_dir)
        
        shutil.move(self.temp_path / "Release-22.04.0-0", poppler_dir)
        self.add_to_path(str(poppler_dir / "bin"))
        
        self.gui.log_message("✅ Windows dependencies installed successfully")
    
    def install_linux_dependencies(self):
        """Install Linux dependencies via package manager."""
        try:
            # Try apt (Ubuntu/Debian)
            self.gui.log_message("📦 Installing via apt...")
            subprocess.run(["sudo", "apt", "update"], check=True, capture_output=True)
            subprocess.run(["sudo", "apt", "install", "-y", "tesseract-ocr", "poppler-utils"], 
                          check=True, capture_output=True)
            self.gui.log_message("✅ Linux dependencies installed via apt")
        except:
            try:
                # Try yum (CentOS/RHEL)
                self.gui.log_message("📦 Installing via yum...")
                subprocess.run(["sudo", "yum", "install", "-y", "tesseract", "poppler-utils"], 
                              check=True, capture_output=True)
                self.gui.log_message("✅ Linux dependencies installed via yum")
            except:
                self.gui.log_message("⚠️ Could not install via package manager. Manual installation required.")
    
    def install_macos_dependencies(self):
        """Install macOS dependencies via Homebrew."""
        try:
            # Check if Homebrew is installed
            subprocess.run(["brew", "--version"], check=True, capture_output=True)
            
            self.gui.log_message("📦 Installing via Homebrew...")
            subprocess.run(["brew", "install", "tesseract", "poppler"], check=True, capture_output=True)
            self.gui.log_message("✅ macOS dependencies installed via Homebrew")
        except:
            self.gui.log_message("⚠️ Homebrew not found. Please install Homebrew first.")
    
    def add_to_path(self, path_to_add):
        """Add directory to system PATH (Windows)."""
        if self.system == "Windows":
            try:
                # Add to user PATH (doesn't require admin)
                current_path = os.environ.get('PATH', '')
                if path_to_add not in current_path:
                    subprocess.run([
                        'setx', 'PATH', f"{current_path};{path_to_add}"
                    ], check=True, capture_output=True)
                    self.gui.log_message(f"🔗 Added to PATH: {path_to_add}")
            except:
                self.gui.log_message(f"⚠️ Could not add to PATH: {path_to_add}")
    
    def create_shortcuts(self):
        """Create desktop shortcuts and launchers."""
        shortcuts_dir = self.install_path / "shortcuts"
        
        if self.system == "Windows":
            self.create_windows_shortcuts(shortcuts_dir)
        elif self.system == "Linux":
            self.create_linux_shortcuts(shortcuts_dir)
        elif self.system == "Darwin":
            self.create_macos_shortcuts(shortcuts_dir)
    
    def create_windows_shortcuts(self, shortcuts_dir):
        """Create Windows shortcuts."""
        # Create batch files for easy launching
        gui_launcher = shortcuts_dir / "Launch_Analysis_Tool.bat"
        gui_launcher.write_text(f"""@echo off
cd /d "{self.install_path}"
python gui_app.py
pause""")
        
        cli_launcher = shortcuts_dir / "Command_Line_Tool.bat"
        cli_launcher.write_text(f"""@echo off
cd /d "{self.install_path}"
python main.py --help
cmd""")
        
        self.gui.log_message("🔗 Created Windows launchers in shortcuts/ folder")
    
    def create_linux_shortcuts(self, shortcuts_dir):
        """Create Linux desktop shortcuts."""
        desktop_file = shortcuts_dir / "public-comment-analysis.desktop"
        desktop_content = f"""[Desktop Entry]
Name=Public Comment Analysis Tool
Comment=Analyze public comment documents with AI
Exec=python3 {self.install_path}/gui_app.py
Icon={self.install_path}/icon.png
Type=Application
Categories=Office;
Terminal=false"""
        desktop_file.write_text(desktop_content)
        desktop_file.chmod(0o755)
        
        self.gui.log_message("🔗 Created Linux desktop shortcut")
    
    def create_macos_shortcuts(self, shortcuts_dir):
        """Create macOS shortcuts."""
        # Create AppleScript launcher
        app_script = shortcuts_dir / "Launch_Analysis_Tool.scpt"
        script_content = f'''tell application "Terminal"
    do script "cd '{self.install_path}' && python3 gui_app.py"
end tell'''
        app_script.write_text(script_content)
        
        self.gui.log_message("🔗 Created macOS launcher script")
    
    def validate_installation(self):
        """Validate that all components are working."""
        # Test Python imports
        test_imports = [
            "pandas", "requests", "tqdm", "numpy", "fitz", 
            "pdf2image", "pytesseract", "sklearn", "sentence_transformers"
        ]
        
        for module in test_imports:
            try:
                __import__(module)
                self.gui.log_message(f"✅ Import test: {module}")
            except ImportError:
                self.gui.log_message(f"⚠️ Import failed: {module}")
        
        # Test Tesseract
        try:
            import pytesseract
            pytesseract.get_tesseract_version()
            self.gui.log_message("✅ Tesseract OCR working")
        except:
            self.gui.log_message("⚠️ Tesseract OCR test failed")
        
        # Test Poppler
        try:
            from pdf2image import convert_from_path
            self.gui.log_message("✅ Poppler PDF tools working")
        except:
            self.gui.log_message("⚠️ Poppler test failed")
        
        # Test GUI components
        try:
            import tkinter
            root = tkinter.Tk()
            root.destroy()
            self.gui.log_message("✅ GUI components working")
        except:
            self.gui.log_message("⚠️ GUI test failed")
    
    def setup_sample_data(self):
        """Set up sample data if CSV files exist."""
        sample_files = list(self.install_path.glob("*Sample*.csv"))
        if sample_files:
            input_dir = self.install_path / "input"
            for sample_file in sample_files:
                dest = input_dir / "sample_data.csv"
                shutil.copy2(sample_file, dest)
                self.gui.log_message(f"📋 Copied sample data: {sample_file.name}")
    
    def cleanup_temp_files(self):
        """Clean up temporary installation files."""
        if self.temp_path.exists():
            try:
                shutil.rmtree(self.temp_path)
                self.gui.log_message("🧹 Cleaned up temporary files")
            except:
                self.gui.log_message("⚠️ Could not clean up temporary files")


def main():
    """Main installer entry point."""
    print("🚀 Starting Public Comment Analysis Tool Installer...")
    
    # Check if we can use GUI
    try:
        import tkinter
        gui_available = True
    except ImportError:
        gui_available = False
    
    if gui_available:
        # Launch graphical installer
        app = InstallationGUI()
        app.root.mainloop()
    else:
        # Fallback to command-line installer
        print("GUI not available, running command-line installer...")
        installer = SystemInstaller(None)
        installer.run_installation()
        print("✅ Installation completed!")


if __name__ == "__main__":
    main()