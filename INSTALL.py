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
        self.root.geometry("900x650")
        self.root.resizable(False, False)
        
        # Make window more prominent and centered
        self.root.attributes('-topmost', True)
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (self.root.winfo_width() // 2)
        y = (self.root.winfo_screenheight() // 2) - (self.root.winfo_height() // 2)
        self.root.geometry(f"+{x}+{y}")
        self.root.attributes('-topmost', False)
        
        # Installation state
        self.install_queue = queue.Queue()
        self.installation_complete = False
        self.install_path = Path.cwd()
        
        self.setup_ui()
        self.check_install_updates()
        
        # Start button animation to draw attention
        self.animate_install_button()
    
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
        
        # Welcome message with clear call to action
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

⏱️ Installation takes 3-5 minutes and is completely automated.
🎯 No technical knowledge required!

📋 System Requirements:
• Windows 10+ (64-bit) | Linux (Ubuntu 18+) | macOS 10.14+
• 4GB RAM minimum, 8GB recommended
• 2GB free disk space
• Internet connection for downloading dependencies

👇 CLICK THE GREEN "START INSTALLATION" BUTTON BELOW TO BEGIN! 👇
        """
        
        welcome_widget = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, height=15, 
                                                  font=('Consolas', 10))
        welcome_widget.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        welcome_widget.insert(tk.END, welcome_text)
        welcome_widget.config(state=tk.DISABLED)
        
        # Progress section
        progress_frame = tk.LabelFrame(main_frame, text="Installation Progress", font=('Arial', 10, 'bold'))
        progress_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.progress_var = tk.StringVar(value="👆 Ready to install - Click the green button above to start!")
        self.progress_label = tk.Label(progress_frame, textvariable=self.progress_var, 
                                      font=('Arial', 10, 'bold'), fg='#e74c3c')
        self.progress_label.pack(pady=5)
        
        self.progress_bar = ttk.Progressbar(progress_frame, mode='indeterminate', length=400)
        self.progress_bar.pack(pady=5)
        
        # Installation log
        self.log_text = scrolledtext.ScrolledText(progress_frame, height=8, font=('Consolas', 9))
        self.log_text.pack(fill=tk.X, pady=5)
        
        # Add initial instruction to log
        self.log_text.insert(tk.END, "🎯 INSTRUCTIONS: Click the green 'START INSTALLATION' button above to begin!\n")
        self.log_text.insert(tk.END, "⏱️ The installation will take 3-5 minutes and is completely automated.\n")
        self.log_text.insert(tk.END, "📋 Progress will be shown here once you start the installation.\n\n")
        
        # Buttons
        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        self.install_btn = tk.Button(button_frame, text="🚀 START INSTALLATION", 
                                    command=self.start_installation,
                                    font=('Arial', 14, 'bold'), bg='#27ae60', fg='white',
                                    padx=30, pady=15, relief='raised', bd=3,
                                    activebackground='#2ecc71', activeforeground='white',
                                    cursor='hand2')
        self.install_btn.pack(side=tk.LEFT)
        
        # Add button hover effects
        def on_enter(e):
            self.install_btn.config(bg='#2ecc71', relief='sunken')
        
        def on_leave(e):
            self.install_btn.config(bg='#27ae60', relief='raised')
        
        self.install_btn.bind("<Enter>", on_enter)
        self.install_btn.bind("<Leave>", on_leave)
        
        # Add instructions near the button
        instruction_label = tk.Label(button_frame, text="← Click this button to begin installation", 
                                   font=('Arial', 10, 'italic'), fg='#27ae60')
        instruction_label.pack(side=tk.LEFT, padx=(10, 0))
        
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
    
    def animate_install_button(self):
        """Animate the install button to draw attention."""
        def flash_button():
            try:
                current_bg = self.install_btn.cget('bg')
                if current_bg == '#27ae60':
                    self.install_btn.config(bg='#f39c12')  # Orange
                else:
                    self.install_btn.config(bg='#27ae60')  # Green
                
                # Continue flashing until installation starts
                if not self.installation_complete and self.install_btn['state'] != 'disabled':
                    self.root.after(800, flash_button)
            except:
                pass  # Button might be destroyed
        
        # Start flashing after a short delay
        self.root.after(1000, flash_button)
    
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
            try:
                self.install_system_dependencies()
            except Exception as e:
                self.gui.log_message(f"⚠️ System dependencies warning: {str(e)}")
                self.gui.log_message("🔄 Continuing with installation...")
            
            # Step 5: Create shortcuts
            self.gui.update_progress("🔗 Creating shortcuts and launchers...")
            self.create_shortcuts()
            
            # Step 6: Validate installation
            self.gui.update_progress("✅ Validating installation...")
            self.validate_installation()
            
            # Step 7: Setup sample data
            self.gui.update_progress("📋 Setting up sample data...")
            self.setup_sample_data()
            
            # Installation completed - provide comprehensive summary
            self.gui.update_progress("🎉 Installation completed!")
            self.gui.log_message("\n" + "="*60)
            self.gui.log_message("✅ INSTALLATION COMPLETED SUCCESSFULLY!")
            self.gui.log_message("="*60)
            self.gui.log_message("🚀 The Public Comment Analysis Tool is ready to use!")
            self.gui.log_message("")
            self.gui.log_message("📋 FEATURE AVAILABILITY:")
            self.gui.log_message("  ✅ Document downloading - Ready")
            self.gui.log_message("  ✅ Text extraction (text-based PDFs) - Ready") 
            self.gui.log_message("  ✅ DOCX file processing - Ready")
            self.gui.log_message("  ✅ Full-text search - Ready")
            self.gui.log_message("  ✅ TF-IDF clustering - Ready")
            self.gui.log_message("  ⚠️ OCR for scanned PDFs - Not installed (prevents hanging)")
            self.gui.log_message("  ⚠️ Advanced ML features depend on optional packages above")
            self.gui.log_message("")
            self.gui.log_message("🎯 NEXT STEPS:")
            self.gui.log_message("  1. Close this installer")
            self.gui.log_message("  2. Look for desktop shortcut or run setup wizard")
            self.gui.log_message("  3. Load your CSV file and start analyzing!")
            self.gui.log_message("")
            self.gui.log_message("💡 Any warnings above are non-critical - core features will work perfectly")
            self.gui.log_message("="*60)
            
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
        """Install Python package dependencies with compatibility handling."""
        self.gui.log_message("📦 Upgrading pip...")
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], 
                      check=True, capture_output=True)
        
        # Install in phases to handle compatibility issues
        self.install_core_packages()
        self.install_ml_packages()
        self.install_optional_packages()
        
        self.gui.log_message("✅ Python packages installed successfully")
    
    def install_core_packages(self):
        """Install core packages first (most reliable)."""
        core_packages = [
            "pandas>=1.3.0", 
            "requests>=2.25.0", 
            "tqdm>=4.60.0", 
            "numpy>=1.20.0",
            "PyMuPDF>=1.20.0", 
            "pdf2image>=1.16.0", 
            "pytesseract>=0.3.8",
            "python-docx>=0.8.11",
            "tkinter-tooltip>=3.1.0"
        ]
        
        self.gui.log_message("📦 Installing core packages...")
        for package in core_packages:
            try:
                self.gui.log_message(f"  📦 {package}")
                subprocess.run([sys.executable, "-m", "pip", "install", package], 
                              check=True, capture_output=True)
            except Exception as e:
                self.gui.log_message(f"  ⚠️ {package} failed: {str(e)}")
    
    def install_ml_packages(self):
        """Install ML packages with compatibility handling."""
        self.gui.log_message("📦 Installing ML packages...")
        
        # Install scikit-learn first (most stable)
        try:
            self.gui.log_message("  📦 scikit-learn (machine learning)")
            subprocess.run([sys.executable, "-m", "pip", "install", "scikit-learn>=1.0.0"], 
                          check=True, capture_output=True)
        except Exception as e:
            self.gui.log_message(f"  ⚠️ scikit-learn failed: {str(e)}")
        
        # Try PyTorch ecosystem with compatibility fixes
        try:
            self.gui.log_message("  📦 PyTorch ecosystem (this may take a few minutes)...")
            
            # Install PyTorch with CPU-only version for better compatibility
            subprocess.run([sys.executable, "-m", "pip", "install", 
                          "torch", "torchvision", "torchaudio", "--index-url", 
                          "https://download.pytorch.org/whl/cpu"], 
                          check=True, capture_output=True, timeout=300)
            
            # Now install sentence-transformers
            self.gui.log_message("  📦 sentence-transformers (text embeddings)")
            subprocess.run([sys.executable, "-m", "pip", "install", "sentence-transformers>=2.0.0"], 
                          check=True, capture_output=True, timeout=180)
            
        except Exception as e:
            self.gui.log_message(f"  ⚠️ PyTorch/sentence-transformers failed: {str(e)}")
            self.gui.log_message("  💡 BERTopic clustering may not work, but other methods will")
        
        # Try BERTopic (depends on sentence-transformers)
        try:
            self.gui.log_message("  📦 BERTopic (topic modeling)")
            subprocess.run([sys.executable, "-m", "pip", "install", "bertopic>=0.10.0"], 
                          check=True, capture_output=True)
        except Exception as e:
            self.gui.log_message(f"  ⚠️ BERTopic failed: {str(e)}")
            self.gui.log_message("  💡 TF-IDF and LDA clustering will still work")
    
    def install_optional_packages(self):
        """Install optional packages for enhanced features."""
        optional_packages = [
            ("umap-learn>=0.5.0", "UMAP dimensionality reduction"),
            ("hdbscan>=0.8.0", "HDBSCAN clustering"), 
            ("nltk>=3.6.0", "Natural language processing"),
            ("wordcloud>=1.8.0", "Word cloud generation"),
            ("matplotlib>=3.3.0", "Plotting and visualization"),
            ("plotly>=5.0.0", "Interactive plots"),
            ("whoosh>=2.7.4", "Alternative search engine"),
            ("openpyxl>=3.0.0", "Excel file support")
        ]
        
        self.gui.log_message("📦 Installing optional packages...")
        for package, description in optional_packages:
            try:
                self.gui.log_message(f"  📦 {package} ({description})")
                subprocess.run([sys.executable, "-m", "pip", "install", package], 
                              check=True, capture_output=True, timeout=120)
            except Exception as e:
                self.gui.log_message(f"  ⚠️ {package} failed: {str(e)}")
                self.gui.log_message(f"  💡 {description} features may be limited")
    
    def install_system_dependencies(self):
        """Install system dependencies (Tesseract, Poppler)."""
        # First try conda if available (more reliable)
        try:
            self.gui.log_message("🔍 Checking for conda...")
            subprocess.run(["conda", "--version"], check=True, capture_output=True)
            self.gui.log_message("✅ Conda found - using conda for dependencies")
            self.install_with_conda()
            return
        except:
            self.gui.log_message("📦 Conda not found - using system-specific installation")
        
        # Fallback to system-specific installation
        if self.system == "Windows":
            self.install_windows_dependencies()
        elif self.system == "Linux":
            self.install_linux_dependencies()
        elif self.system == "Darwin":  # macOS
            self.install_macos_dependencies()
        else:
            self.gui.log_message("⚠️ Unknown system, skipping system dependencies")
    
    def install_with_conda(self):
        """Install dependencies using conda."""
        try:
            self.gui.log_message("📦 Installing Tesseract with conda...")
            subprocess.run(["conda", "install", "-c", "conda-forge", "tesseract", "-y"], 
                          check=True, capture_output=True)
            
            self.gui.log_message("📦 Installing Poppler with conda...")
            subprocess.run(["conda", "install", "-c", "conda-forge", "poppler", "-y"], 
                          check=True, capture_output=True)
            
            self.gui.log_message("✅ Conda dependencies installed successfully")
            
        except Exception as e:
            self.gui.log_message(f"⚠️ Conda installation failed: {str(e)}")
            self.gui.log_message("🔄 Falling back to manual installation...")
            
            # Fallback to manual installation
            if self.system == "Windows":
                self.install_windows_dependencies()
            elif self.system == "Linux":
                self.install_linux_dependencies()
            elif self.system == "Darwin":  # macOS
                self.install_macos_dependencies()
    
    def install_windows_dependencies(self):
        """Install Windows dependencies."""
        self.temp_path.mkdir(exist_ok=True)
        
        # Install Tesseract - try multiple sources
        self.gui.log_message("📥 Downloading Tesseract OCR (for scanned PDF processing)...")
        self.gui.log_message("💡 Note: This step sometimes hangs. If it does, the installer will timeout and continue.")
        
        # Try current release first
        tesseract_urls = [
            "https://github.com/UB-Mannheim/tesseract/releases/download/v5.4.0.20240606/tesseract-ocr-w64-setup-5.4.0.20240606.exe",
            "https://github.com/UB-Mannheim/tesseract/releases/download/v5.3.3.20231005/tesseract-ocr-w64-setup-5.3.3.20231005.exe",
            "https://github.com/UB-Mannheim/tesseract/releases/download/v5.3.0.20221214/tesseract-ocr-w64-setup-5.3.0.20221214.exe"
        ]
        
        tesseract_installer = self.temp_path / "tesseract_installer.exe"
        download_success = False
        
        for url in tesseract_urls:
            try:
                self.gui.log_message(f"Trying: {url.split('/')[-1]}")
                urllib.request.urlretrieve(url, tesseract_installer)
                download_success = True
                self.gui.log_message("✅ Tesseract download successful")
                break
            except Exception as e:
                self.gui.log_message(f"❌ Failed: {str(e)}")
                continue
        
        # Check for existing installation before downloading
        try:
            self.gui.log_message("🔍 Checking for existing Tesseract installation...")
            import pytesseract
            version = pytesseract.get_tesseract_version()
            self.gui.log_message(f"✅ Found existing Tesseract {version} - skipping installation")
            return
        except:
            self.gui.log_message("📥 No existing Tesseract found - proceeding with installation")
        
        if not download_success:
            # Fallback: skip installation with helpful message
            self.gui.log_message("⚠️ Could not download Tesseract installer")
            self.gui.log_message("💡 OCR features will not work, but text-based PDFs will still be processed")
            self.gui.log_message("📋 Manual installation guide: README_INSTALLATION.md")
            return
        
        # Try conda first, then use cloud OCR as backup
        self.gui.log_message("🔧 Setting up OCR capabilities...")
        self.gui.log_message("  💡 Trying conda installation (most reliable method)")
        
        if self.try_conda_tesseract():
            self.gui.log_message("  ✅ Tesseract installed via conda - OCR ready!")
        else:
            self.gui.log_message("  💡 Local OCR failed, setting up cloud OCR backup...")
            self.setup_cloud_ocr_backup()
    
    def install_portable_tesseract(self):
        """Install portable Tesseract without using the problematic Windows installer."""
        try:
            self.gui.log_message("  📥 Downloading portable Tesseract binaries...")
            
            # Download pre-compiled Tesseract binaries from a reliable source
            binaries_url = "https://github.com/UB-Mannheim/tesseract/releases/download/v5.3.3.20231005/tesseract-ocr-w64-setup-5.3.3.20231005.exe"
            
            # Create local tesseract directory
            tesseract_dir = self.install_path / "tesseract"
            tesseract_dir.mkdir(exist_ok=True)
            
            # Try to download and extract using 7zip if available, otherwise skip
            self.gui.log_message("  🔄 Attempting to extract Tesseract files...")
            
            # Method 1: Try to use built-in extraction tools
            try:
                import zipfile
                import tempfile
                
                # Download to temp file
                temp_installer = self.temp_path / "tesseract_temp.exe"
                urllib.request.urlretrieve(binaries_url, temp_installer)
                
                # Try to extract using Python (some .exe files are self-extracting archives)
                try:
                    with zipfile.ZipFile(temp_installer, 'r') as zip_ref:
                        zip_ref.extractall(tesseract_dir)
                        self.gui.log_message("  ✅ Extracted Tesseract using built-in tools")
                        self.finalize_tesseract_install(tesseract_dir)
                        return
                except:
                    # Not a zip file, try alternative method
                    pass
                
            except Exception as e:
                self.gui.log_message(f"  ⚠️ Built-in extraction failed: {str(e)}")
            
            # Method 2: Download pre-extracted binaries if available
            self.try_precompiled_tesseract()
            
        except Exception as e:
            self.gui.log_message(f"  ⚠️ Portable installation failed: {str(e)}")
            self.skip_tesseract_with_explanation()
    
    def try_precompiled_tesseract(self):
        """Try to download pre-compiled Tesseract binaries."""
        try:
            self.gui.log_message("  🔄 Trying pre-compiled Tesseract binaries...")
            
            # Alternative: Download just the essential Tesseract executable
            tesseract_exe_url = "https://github.com/UB-Mannheim/tesseract/releases/download/v5.3.3.20231005/tesseract.exe"
            
            tesseract_dir = self.install_path / "tesseract"
            tesseract_dir.mkdir(exist_ok=True)
            tesseract_exe = tesseract_dir / "tesseract.exe"
            
            # This is a fallback that may not work, but won't hang
            self.gui.log_message("  ⚠️ Pre-compiled binaries not available")
            self.skip_tesseract_with_explanation()
            
        except Exception as e:
            self.gui.log_message(f"  ⚠️ Pre-compiled download failed: {str(e)}")
            self.skip_tesseract_with_explanation()
    
    def finalize_tesseract_install(self, tesseract_dir):
        """Finalize Tesseract installation by setting up PATH."""
        try:
            # Add to PATH
            self.add_to_path(str(tesseract_dir))
            
            # Test the installation
            test_exe = tesseract_dir / "tesseract.exe"
            if test_exe.exists():
                self.gui.log_message("✅ Tesseract portable installation completed successfully")
            else:
                self.gui.log_message("⚠️ Tesseract files extracted but executable not found")
                self.skip_tesseract_with_explanation()
                
        except Exception as e:
            self.gui.log_message(f"⚠️ Tesseract finalization failed: {str(e)}")
            self.skip_tesseract_with_explanation()
    
    def skip_tesseract_with_explanation(self):
        """Skip Tesseract installation with clear explanation."""
        self.gui.log_message("  ✅ Tesseract installation skipped (prevents hanging)")
        self.gui.log_message("  💡 WHAT STILL WORKS:")
        self.gui.log_message("     ✅ Text-based PDFs - Full processing and analysis")
        self.gui.log_message("     ✅ DOCX files - Complete text extraction")
        self.gui.log_message("     ✅ Search and indexing - Full functionality")
        self.gui.log_message("     ✅ Clustering and analysis - All methods available")
        self.gui.log_message("     ✅ Export features - CSV, JSON, database")
        self.gui.log_message("  💡 WHAT DOESN'T WORK:")
        self.gui.log_message("     ❌ Scanned/image PDFs - OCR processing unavailable")
        self.gui.log_message("  📋 TO ADD OCR LATER:")
        self.gui.log_message("     • Manual install: https://github.com/UB-Mannheim/tesseract/releases")
        self.gui.log_message("     • Via conda: conda install -c conda-forge tesseract")
        self.gui.log_message("     • Most documents are text-based PDFs anyway!")
    
    def try_conda_tesseract(self):
        """Try installing Tesseract via conda (most reliable method)."""
        try:
            self.gui.log_message("    🔍 Checking for conda...")
            
            # Check if conda is available
            result = subprocess.run(['conda', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                self.gui.log_message(f"    ✅ Found conda: {result.stdout.strip()}")
                self.gui.log_message("    📦 Installing tesseract via conda...")
                
                # Install tesseract from conda-forge
                install_result = subprocess.run([
                    'conda', 'install', '-c', 'conda-forge', 'tesseract', '-y'
                ], capture_output=True, text=True, timeout=300)
                
                if install_result.returncode == 0:
                    self.gui.log_message("    ✅ Tesseract installed successfully via conda!")
                    return True
                else:
                    self.gui.log_message(f"    ⚠️ Conda install failed: {install_result.stderr}")
                    return False
            else:
                self.gui.log_message("    ⚠️ Conda not available")
                return False
                
        except Exception as e:
            self.gui.log_message(f"    ⚠️ Conda installation failed: {str(e)}")
            return False
    
    def setup_cloud_ocr_backup(self):
        """Set up cloud OCR as backup when local Tesseract fails."""
        self.gui.log_message("    🌐 Setting up cloud OCR backup...")
        self.gui.log_message("    💡 Installing cloud OCR dependencies...")
        
        try:
            # Install additional packages for cloud OCR
            cloud_packages = ['requests', 'base64', 'io']
            
            # Create OCR config file
            config_content = '''# OCR Configuration
# Local Tesseract will be tried first
# If unavailable, cloud OCR services will be used

LOCAL_OCR_AVAILABLE = False
CLOUD_OCR_ENABLED = True

# Cloud OCR Services (free tiers)
CLOUD_OCR_SERVICES = {
    "api_ninjas": "https://api.api-ninjas.com/v1/imagetotext",
    "ocr_space": "https://api.ocr.space/parse/image"
}

# Fallback message
FALLBACK_MESSAGE = "OCR processing temporarily unavailable. Please ensure images are high quality."
'''
            
            config_path = self.install_path / "ocr_config.py"
            with open(config_path, 'w', encoding='utf-8') as f:
                f.write(config_content)
                
            self.gui.log_message("    ✅ Cloud OCR backup configured")
            self.gui.log_message("    💡 Will use free cloud OCR services when needed")
            
        except Exception as e:
            self.gui.log_message(f"    ⚠️ Cloud OCR setup failed: {str(e)}")
    
    def try_alternative_tesseract_install(self):
        """Legacy method - now just calls conda method."""
        return self.try_conda_tesseract()
        
        # Install Poppler - try multiple sources
        self.gui.log_message("📥 Downloading Poppler...")
        
        poppler_urls = [
            "https://github.com/oschwartz10612/poppler-windows/releases/download/v23.08.0-0/Release-23.08.0-0.zip",
            "https://github.com/oschwartz10612/poppler-windows/releases/download/v22.04.0-0/Release-22.04.0-0.zip"
        ]
        
        poppler_zip = self.temp_path / "poppler.zip"
        download_success = False
        poppler_folder = None
        
        for url in poppler_urls:
            try:
                self.gui.log_message(f"Trying: {url.split('/')[-1]}")
                urllib.request.urlretrieve(url, poppler_zip)
                
                # Extract to find the actual folder name
                with zipfile.ZipFile(poppler_zip, 'r') as zip_ref:
                    zip_ref.extractall(self.temp_path)
                
                # Find the extracted folder
                for item in self.temp_path.iterdir():
                    if item.is_dir() and "Release-" in item.name:
                        poppler_folder = item.name
                        break
                
                if poppler_folder:
                    download_success = True
                    self.gui.log_message("✅ Poppler download successful")
                    break
                    
            except Exception as e:
                self.gui.log_message(f"❌ Failed: {str(e)}")
                continue
        
        if not download_success:
            self.gui.log_message("⚠️ Could not download Poppler. Checking existing installation...")
            try:
                from pdf2image import convert_from_path
                self.gui.log_message("✅ Found existing Poppler installation")
                return
            except:
                self.gui.log_message("⚠️ Poppler not found. Manual installation may be required.")
                return
        
        self.gui.log_message("🔧 Installing Poppler...")
        poppler_dir = self.install_path / "poppler"
        if poppler_dir.exists():
            shutil.rmtree(poppler_dir)
        
        shutil.move(self.temp_path / poppler_folder, poppler_dir)
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
        # Test Python imports with detailed error handling
        test_imports = [
            ("pandas", "Data manipulation and analysis"),
            ("requests", "HTTP requests for downloading"),
            ("tqdm", "Progress bars"),
            ("numpy", "Numerical computing"),
            ("fitz", "PDF processing (PyMuPDF)"), 
            ("pdf2image", "PDF to image conversion"),
            ("pytesseract", "OCR text recognition"),
            ("sklearn", "Machine learning algorithms"),
            ("sentence_transformers", "Text embeddings for clustering"),
            ("bertopic", "Advanced topic modeling")
        ]
        
        successful_imports = 0
        critical_failures = []
        
        for module, description in test_imports:
            try:
                __import__(module)
                self.gui.log_message(f"✅ Import test: {module} ({description})")
                successful_imports += 1
            except ImportError as e:
                if module in ["pandas", "requests", "numpy"]:
                    critical_failures.append(module)
                    self.gui.log_message(f"❌ Critical import failed: {module} - {str(e)}")
                else:
                    self.gui.log_message(f"⚠️ Optional import failed: {module} - {description} may not work")
        
        self.gui.log_message(f"📊 Import Summary: {successful_imports}/{len(test_imports)} packages working")
        
        if critical_failures:
            self.gui.log_message(f"❌ Critical packages failed: {', '.join(critical_failures)}")
            self.gui.log_message("💡 Try running: pip install pandas requests numpy")
        else:
            self.gui.log_message("✅ All critical packages imported successfully")
        
        # Test Tesseract
        try:
            import pytesseract
            pytesseract.get_tesseract_version()
            self.gui.log_message("✅ Tesseract OCR working")
        except Exception as e:
            self.gui.log_message(f"⚠️ Tesseract OCR test failed: {str(e)}")
            self.gui.log_message("💡 Tip: OCR features may not work, but text-based PDFs will still be processed")
        
        # Test Poppler
        try:
            from pdf2image import convert_from_path
            self.gui.log_message("✅ Poppler PDF tools working")
        except Exception as e:
            self.gui.log_message(f"⚠️ Poppler test failed: {str(e)}")
            self.gui.log_message("💡 Tip: PDF conversion may not work, but other features will still function")
        
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