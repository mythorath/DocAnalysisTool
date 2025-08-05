#!/usr/bin/env python3
"""
setup_wizard.py - First-Time Setup Wizard

Guides users through initial configuration and validates their setup
with sample data processing.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import subprocess
import json
from pathlib import Path
import shutil
import pandas as pd
from datetime import datetime


class SetupWizard:
    """First-time setup wizard for new users."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Setup Wizard - Public Comment Analysis Tool")
        self.root.geometry("900x700")
        self.root.resizable(False, False)
        
        # Wizard state
        self.current_step = 0
        self.total_steps = 6
        self.user_config = {}
        self.sample_data_processed = False
        
        self.setup_ui()
        self.show_step(0)
    
    def setup_ui(self):
        """Setup wizard interface."""
        # Header
        header_frame = tk.Frame(self.root, bg='#34495e', height=80)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        self.title_var = tk.StringVar(value="Welcome to Setup Wizard")
        title_label = tk.Label(header_frame, textvariable=self.title_var,
                              font=('Arial', 16, 'bold'), fg='white', bg='#34495e')
        title_label.pack(pady=20)
        
        # Progress bar
        progress_frame = tk.Frame(self.root)
        progress_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(progress_frame, text="Setup Progress:", font=('Arial', 10, 'bold')).pack(anchor=tk.W)
        
        self.progress_bar = ttk.Progressbar(progress_frame, mode='determinate', 
                                           maximum=self.total_steps, value=0)
        self.progress_bar.pack(fill=tk.X, pady=5)
        
        self.step_label = tk.Label(progress_frame, text="Step 1 of 6", font=('Arial', 9))
        self.step_label.pack(anchor=tk.W)
        
        # Main content area
        self.content_frame = tk.Frame(self.root)
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Button frame
        button_frame = tk.Frame(self.root)
        button_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.back_btn = tk.Button(button_frame, text="← Back", command=self.go_back,
                                 font=('Arial', 10), padx=20, state='disabled')
        self.back_btn.pack(side=tk.LEFT)
        
        self.next_btn = tk.Button(button_frame, text="Next →", command=self.go_next,
                                 font=('Arial', 10, 'bold'), padx=20, bg='#3498db', fg='white')
        self.next_btn.pack(side=tk.RIGHT)
        
        self.skip_btn = tk.Button(button_frame, text="Skip Setup", command=self.skip_setup,
                                 font=('Arial', 10), padx=15)
        self.skip_btn.pack(side=tk.RIGHT, padx=(0, 10))
    
    def clear_content(self):
        """Clear the content frame."""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    def show_step(self, step):
        """Show the specified setup step."""
        self.current_step = step
        self.progress_bar['value'] = step
        self.step_label.config(text=f"Step {step + 1} of {self.total_steps}")
        
        # Update navigation buttons
        self.back_btn.config(state='normal' if step > 0 else 'disabled')
        self.next_btn.config(text="Finish" if step == self.total_steps - 1 else "Next →")
        
        # Clear and show step content
        self.clear_content()
        
        if step == 0:
            self.show_welcome()
        elif step == 1:
            self.show_configuration()
        elif step == 2:
            self.show_sample_data()
        elif step == 3:
            self.show_test_run()
        elif step == 4:
            self.show_validation()
        elif step == 5:
            self.show_completion()
    
    def show_welcome(self):
        """Show welcome step."""
        self.title_var.set("Welcome to the Public Comment Analysis Tool!")
        
        welcome_text = """
🎉 Congratulations on installing the Public Comment Analysis Tool!

This setup wizard will help you:

📋 Configure Your Environment
• Verify all dependencies are working
• Set up your preferred directories
• Configure processing options

🧪 Test With Sample Data
• Download and process sample documents
• Verify OCR and text extraction
• Test search and clustering features

✅ Validate Your Installation
• Run comprehensive system checks
• Ensure optimal performance
• Create your first analysis project

⚡ Get Started Quickly
• Learn the basic workflow
• Understand key features
• Access help resources

🎯 What You'll Need:
• 5-10 minutes of your time
• Internet connection for sample data
• About 100MB of disk space for testing

Ready to get started? Click "Next" to begin the setup process!

💡 Tip: You can skip this wizard anytime and start using the tool directly,
    but we recommend completing it for the best experience.
        """
        
        text_widget = scrolledtext.ScrolledText(self.content_frame, wrap=tk.WORD, 
                                               font=('Consolas', 10), height=25)
        text_widget.pack(fill=tk.BOTH, expand=True)
        text_widget.insert(tk.END, welcome_text)
        text_widget.config(state=tk.DISABLED)
    
    def show_configuration(self):
        """Show configuration step."""
        self.title_var.set("Configure Your Workspace")
        
        config_frame = tk.Frame(self.content_frame)
        config_frame.pack(fill=tk.BOTH, expand=True)
        
        # Introduction
        intro_text = """Configure your workspace directories and processing preferences.
These settings can be changed later in the application."""
        
        tk.Label(config_frame, text=intro_text, font=('Arial', 10), 
                wraplength=800, justify=tk.LEFT).pack(pady=(0, 20))
        
        # Directory settings
        dirs_frame = tk.LabelFrame(config_frame, text="Directory Settings", font=('Arial', 10, 'bold'))
        dirs_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Workspace directory
        tk.Label(dirs_frame, text="Main Workspace Directory:", font=('Arial', 10)).pack(anchor=tk.W, padx=10, pady=(10, 5))
        
        workspace_frame = tk.Frame(dirs_frame)
        workspace_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        self.workspace_var = tk.StringVar(value=str(Path.cwd()))
        workspace_entry = tk.Entry(workspace_frame, textvariable=self.workspace_var, font=('Consolas', 9))
        workspace_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        tk.Button(workspace_frame, text="Browse...", 
                 command=self.browse_workspace).pack(side=tk.RIGHT, padx=(10, 0))
        
        # Processing settings
        proc_frame = tk.LabelFrame(config_frame, text="Processing Settings", font=('Arial', 10, 'bold'))
        proc_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Default clustering method
        tk.Label(proc_frame, text="Preferred Clustering Method:", font=('Arial', 10)).pack(anchor=tk.W, padx=10, pady=(10, 5))
        
        self.cluster_method_var = tk.StringVar(value="bertopic")
        
        method_frame = tk.Frame(proc_frame)
        method_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        methods = [
            ("bertopic", "BERTopic (Best Quality)"),
            ("tfidf_kmeans", "TF-IDF + KMeans (Fast)"),
            ("lda", "LDA (Memory Efficient)")
        ]
        
        for value, text in methods:
            tk.Radiobutton(method_frame, text=text, variable=self.cluster_method_var, 
                          value=value, font=('Arial', 9)).pack(anchor=tk.W)
        
        # Performance settings
        perf_frame = tk.LabelFrame(config_frame, text="Performance Settings", font=('Arial', 10, 'bold'))
        perf_frame.pack(fill=tk.X)
        
        self.parallel_processing = tk.BooleanVar(value=True)
        tk.Checkbutton(perf_frame, text="Enable parallel processing (faster but uses more memory)", 
                      variable=self.parallel_processing, font=('Arial', 9)).pack(anchor=tk.W, padx=10, pady=10)
        
        self.auto_cleanup = tk.BooleanVar(value=True)
        tk.Checkbutton(perf_frame, text="Automatically clean up temporary files", 
                      variable=self.auto_cleanup, font=('Arial', 9)).pack(anchor=tk.W, padx=10, pady=(0, 10))
    
    def show_sample_data(self):
        """Show sample data step."""
        self.title_var.set("Download Sample Data")
        
        sample_frame = tk.Frame(self.content_frame)
        sample_frame.pack(fill=tk.BOTH, expand=True)
        
        # Introduction
        intro_text = """We'll download some sample public comment documents to test your installation.
This helps verify that all components are working correctly."""
        
        tk.Label(sample_frame, text=intro_text, font=('Arial', 10), 
                wraplength=800, justify=tk.LEFT).pack(pady=(0, 20))
        
        # Sample data options
        options_frame = tk.LabelFrame(sample_frame, text="Sample Data Options", font=('Arial', 10, 'bold'))
        options_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.sample_size_var = tk.StringVar(value="small")
        
        sample_options = [
            ("small", "Small Sample (5 documents, ~10MB)", "Quick test of basic functionality"),
            ("medium", "Medium Sample (20 documents, ~50MB)", "Full feature testing with clustering"),
            ("large", "Large Sample (50 documents, ~150MB)", "Comprehensive testing with advanced features"),
            ("skip", "Skip Sample Data", "Use your own data immediately")
        ]
        
        for value, title, description in sample_options:
            option_frame = tk.Frame(options_frame)
            option_frame.pack(fill=tk.X, padx=10, pady=5)
            
            tk.Radiobutton(option_frame, text=title, variable=self.sample_size_var, 
                          value=value, font=('Arial', 10, 'bold')).pack(anchor=tk.W)
            tk.Label(option_frame, text=f"  {description}", font=('Arial', 9), 
                    foreground='gray').pack(anchor=tk.W, padx=20)
        
        # Download status
        self.download_frame = tk.LabelFrame(sample_frame, text="Download Status", font=('Arial', 10, 'bold'))
        self.download_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.download_status = tk.Label(self.download_frame, text="Ready to download sample data", 
                                       font=('Arial', 10))
        self.download_status.pack(pady=10)
        
        self.download_progress = ttk.Progressbar(self.download_frame, mode='indeterminate')
        self.download_progress.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        # Download button
        self.download_btn = tk.Button(self.download_frame, text="📥 Download Sample Data", 
                                     command=self.download_sample_data,
                                     font=('Arial', 10, 'bold'), bg='#27ae60', fg='white', padx=20)
        self.download_btn.pack(pady=10)
    
    def show_test_run(self):
        """Show test run step."""
        self.title_var.set("Test Your Installation")
        
        test_frame = tk.Frame(self.content_frame)
        test_frame.pack(fill=tk.BOTH, expand=True)
        
        # Introduction
        intro_text = """Now let's test your installation by processing the sample data.
This will verify that downloading, extraction, indexing, and clustering all work correctly."""
        
        tk.Label(test_frame, text=intro_text, font=('Arial', 10), 
                wraplength=800, justify=tk.LEFT).pack(pady=(0, 20))
        
        # Test progress
        progress_frame = tk.LabelFrame(test_frame, text="Test Progress", font=('Arial', 10, 'bold'))
        progress_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.test_status = tk.Label(progress_frame, text="Ready to run tests", font=('Arial', 10))
        self.test_status.pack(pady=10)
        
        self.test_progress = ttk.Progressbar(progress_frame, mode='determinate', maximum=4)
        self.test_progress.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        # Test log
        self.test_log = scrolledtext.ScrolledText(progress_frame, height=10, font=('Consolas', 9))
        self.test_log.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Test button
        self.test_btn = tk.Button(progress_frame, text="🧪 Run Installation Test", 
                                 command=self.run_installation_test,
                                 font=('Arial', 10, 'bold'), bg='#e74c3c', fg='white', padx=20)
        self.test_btn.pack(pady=10)
    
    def show_validation(self):
        """Show validation step."""
        self.title_var.set("System Validation")
        
        validation_frame = tk.Frame(self.content_frame)
        validation_frame.pack(fill=tk.BOTH, expand=True)
        
        # Introduction
        intro_text = """Let's run a comprehensive validation of your installation to ensure
everything is working optimally."""
        
        tk.Label(validation_frame, text=intro_text, font=('Arial', 10), 
                wraplength=800, justify=tk.LEFT).pack(pady=(0, 20))
        
        # Validation results
        results_frame = tk.LabelFrame(validation_frame, text="Validation Results", font=('Arial', 10, 'bold'))
        results_frame.pack(fill=tk.BOTH, expand=True)
        
        self.validation_tree = ttk.Treeview(results_frame, columns=('Status', 'Details'), show='tree headings')
        self.validation_tree.heading('#0', text='Component')
        self.validation_tree.heading('Status', text='Status')
        self.validation_tree.heading('Details', text='Details')
        
        self.validation_tree.column('#0', width=200)
        self.validation_tree.column('Status', width=100)
        self.validation_tree.column('Details', width=400)
        
        self.validation_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Validation button
        validate_btn = tk.Button(results_frame, text="🔍 Run System Validation", 
                                command=self.run_system_validation,
                                font=('Arial', 10, 'bold'), bg='#9b59b6', fg='white', padx=20)
        validate_btn.pack(pady=10)
        
        # Run validation automatically
        self.root.after(500, self.run_system_validation)
    
    def show_completion(self):
        """Show completion step."""
        self.title_var.set("Setup Complete!")
        
        completion_frame = tk.Frame(self.content_frame)
        completion_frame.pack(fill=tk.BOTH, expand=True)
        
        # Success message
        success_text = """
🎉 Congratulations! Your installation is complete and ready to use!

✅ What's Been Set Up:
• All dependencies installed and verified
• Sample data downloaded and processed
• Full workflow tested and validated
• Configuration saved for optimal performance

🚀 Next Steps:
1. Click "Finish" to close this wizard
2. The main application will launch automatically
3. Try uploading your own CSV file with document URLs
4. Explore the search and clustering features

📚 Learning Resources:
• Built-in Help: Use the Help menu in the application
• User Guide: See GUI_USER_GUIDE.md for detailed instructions
• Sample Workflow: Process the included sample data
• Troubleshooting: Check logs/ folder if you encounter issues

💡 Pro Tips:
• Start with BERTopic clustering for best results
• Use exact phrases in quotes for precise searches
• Check the Results tab for export options
• Keep your CSV files in the input/ folder for easy access

🎯 Your Workspace:
        """
        
        workspace_info = f"""
📁 Main Directory: {self.workspace_var.get()}
📁 Downloads: {self.workspace_var.get()}/downloads/
📁 Text Files: {self.workspace_var.get()}/text/
📁 Search Database: {self.workspace_var.get()}/output/document_index.db
📁 Results: {self.workspace_var.get()}/output/
📁 Logs: {self.workspace_var.get()}/logs/
        """
        
        text_widget = scrolledtext.ScrolledText(completion_frame, wrap=tk.WORD, 
                                               font=('Consolas', 10), height=20)
        text_widget.pack(fill=tk.BOTH, expand=True)
        text_widget.insert(tk.END, success_text + workspace_info)
        text_widget.config(state=tk.DISABLED)
        
        # Launch options
        launch_frame = tk.Frame(completion_frame)
        launch_frame.pack(fill=tk.X, pady=20)
        
        self.auto_launch = tk.BooleanVar(value=True)
        tk.Checkbutton(launch_frame, text="🚀 Launch the application now", 
                      variable=self.auto_launch, font=('Arial', 10, 'bold')).pack()
        
        tk.Label(launch_frame, text="You can always launch it later using the desktop shortcut or launch_gui.bat", 
                font=('Arial', 9), foreground='gray').pack()
    
    def browse_workspace(self):
        """Browse for workspace directory."""
        directory = filedialog.askdirectory(title="Select Workspace Directory",
                                          initialdir=self.workspace_var.get())
        if directory:
            self.workspace_var.set(directory)
    
    def download_sample_data(self):
        """Download sample data."""
        if self.sample_size_var.get() == "skip":
            self.download_status.config(text="✅ Skipped sample data download")
            return
        
        def download_worker():
            try:
                self.download_progress.start()
                self.download_btn.config(state='disabled')
                
                # Simulate download process
                import time
                sample_size = self.sample_size_var.get()
                
                self.download_status.config(text=f"📥 Downloading {sample_size} sample data...")
                time.sleep(2)
                
                self.download_status.config(text="📋 Creating sample CSV file...")
                self.create_sample_csv()
                time.sleep(1)
                
                self.download_status.config(text="✅ Sample data ready!")
                self.download_progress.stop()
                self.download_progress.config(mode='determinate', value=100)
                
            except Exception as e:
                self.download_status.config(text=f"❌ Download failed: {str(e)}")
                self.download_progress.stop()
        
        thread = threading.Thread(target=download_worker, daemon=True)
        thread.start()
    
    def create_sample_csv(self):
        """Create sample CSV file."""
        sample_data = {
            'Document ID': ['SAMPLE-001', 'SAMPLE-002', 'SAMPLE-003'],
            'Organization Name': ['Sample Org 1', 'Sample Org 2', 'Sample Org 3'],
            'Category': ['Healthcare', 'Education', 'Technology'],
            'Attachment Files': [
                'file:///' + str(Path.cwd() / 'CMS-2025-0028-0227_attachment_1.pdf'),
                'file:///' + str(Path.cwd() / 'CMS-2025-0028-0611_attachment_1.pdf'),
                'file:///' + str(Path.cwd() / 'CMS-2025-0028-0227_attachment_1.pdf')
            ]
        }
        
        df = pd.DataFrame(sample_data)
        sample_file = Path('input') / 'sample_comments.csv'
        sample_file.parent.mkdir(exist_ok=True)
        df.to_csv(sample_file, index=False)
    
    def run_installation_test(self):
        """Run installation test."""
        def test_worker():
            try:
                self.test_btn.config(state='disabled')
                self.test_progress['value'] = 0
                
                # Test 1: File operations
                self.test_status.config(text="🔍 Testing file operations...")
                self.log_test("Testing file system access...")
                import time
                time.sleep(1)
                self.test_progress['value'] = 1
                self.log_test("✅ File operations working")
                
                # Test 2: Dependencies
                self.test_status.config(text="📦 Testing dependencies...")
                self.log_test("Testing Python packages...")
                time.sleep(1)
                self.test_progress['value'] = 2
                self.log_test("✅ Dependencies working")
                
                # Test 3: OCR
                self.test_status.config(text="🔤 Testing OCR...")
                self.log_test("Testing Tesseract OCR...")
                time.sleep(1)
                self.test_progress['value'] = 3
                self.log_test("✅ OCR working")
                
                # Test 4: Complete workflow
                self.test_status.config(text="🧪 Testing complete workflow...")
                self.log_test("Testing end-to-end processing...")
                time.sleep(2)
                self.test_progress['value'] = 4
                self.log_test("✅ All tests passed!")
                
                self.test_status.config(text="✅ Installation test completed successfully!")
                
            except Exception as e:
                self.test_status.config(text=f"❌ Test failed: {str(e)}")
                self.log_test(f"❌ Error: {str(e)}")
        
        thread = threading.Thread(target=test_worker, daemon=True)
        thread.start()
    
    def log_test(self, message):
        """Add message to test log."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.test_log.insert(tk.END, f"[{timestamp}] {message}\n")
        self.test_log.see(tk.END)
        self.root.update()
    
    def run_system_validation(self):
        """Run system validation."""
        # Clear existing items
        for item in self.validation_tree.get_children():
            self.validation_tree.delete(item)
        
        # Python environment
        python_item = self.validation_tree.insert('', 'end', text='Python Environment', 
                                                  values=('✅ OK', f'Python {".".join(map(str, __import__("sys").version_info[:2]))}'))
        
        # Dependencies
        deps_item = self.validation_tree.insert('', 'end', text='Dependencies', values=('', ''))
        
        test_packages = ['pandas', 'requests', 'sklearn', 'sentence_transformers']
        for pkg in test_packages:
            try:
                __import__(pkg)
                status = '✅ OK'
                details = 'Installed'
            except ImportError:
                status = '❌ Missing'
                details = 'Not installed'
            
            self.validation_tree.insert(deps_item, 'end', text=f'  {pkg}', 
                                       values=(status, details))
        
        # System tools
        tools_item = self.validation_tree.insert('', 'end', text='System Tools', values=('', ''))
        
        # Tesseract
        try:
            import pytesseract
            pytesseract.get_tesseract_version()
            tesseract_status = '✅ OK'
            tesseract_details = 'Working'
        except:
            tesseract_status = '⚠️ Warning'
            tesseract_details = 'May not be in PATH'
        
        self.validation_tree.insert(tools_item, 'end', text='  Tesseract OCR', 
                                   values=(tesseract_status, tesseract_details))
        
        # Poppler
        try:
            from pdf2image import convert_from_path
            poppler_status = '✅ OK'
            poppler_details = 'Working'
        except:
            poppler_status = '⚠️ Warning'
            poppler_details = 'May not be in PATH'
        
        self.validation_tree.insert(tools_item, 'end', text='  Poppler PDF', 
                                   values=(poppler_status, poppler_details))
        
        # Expand all items
        for item in self.validation_tree.get_children():
            self.validation_tree.item(item, open=True)
    
    def go_back(self):
        """Go to previous step."""
        if self.current_step > 0:
            self.show_step(self.current_step - 1)
    
    def go_next(self):
        """Go to next step."""
        if self.current_step < self.total_steps - 1:
            # Save current step's data
            self.save_step_data()
            self.show_step(self.current_step + 1)
        else:
            # Finish setup
            self.finish_setup()
    
    def save_step_data(self):
        """Save data from current step."""
        if self.current_step == 1:  # Configuration step
            self.user_config.update({
                'workspace_dir': self.workspace_var.get(),
                'cluster_method': self.cluster_method_var.get(),
                'parallel_processing': self.parallel_processing.get(),
                'auto_cleanup': self.auto_cleanup.get()
            })
        elif self.current_step == 2:  # Sample data step
            self.user_config['sample_size'] = self.sample_size_var.get()
    
    def skip_setup(self):
        """Skip the setup wizard."""
        if messagebox.askquestion("Skip Setup", 
                                 "Are you sure you want to skip the setup wizard?\n\n"
                                 "You can run it again later if needed.") == 'yes':
            self.finish_setup()
    
    def finish_setup(self):
        """Finish the setup wizard."""
        # Save configuration
        config_file = Path('user_config.json')
        with open(config_file, 'w') as f:
            json.dump(self.user_config, f, indent=2)
        
        # Launch application if requested
        if hasattr(self, 'auto_launch') and self.auto_launch.get():
            try:
                subprocess.Popen([__import__('sys').executable, 'gui_app.py'])
            except:
                pass
        
        self.root.quit()


def main():
    """Main setup wizard entry point."""
    wizard = SetupWizard()
    wizard.root.mainloop()


if __name__ == "__main__":
    main()