#!/usr/bin/env python3
"""
gui_app.py - User-Friendly GUI for Public Comment Analysis Tool

This module provides a modern, intuitive graphical interface for the complete
document analysis workflow with on-screen instructions and progress tracking.
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from tkinter.font import Font
import threading
import queue
import json
from pathlib import Path
from datetime import datetime
import webbrowser

# Try to import tooltip (fallback if not available)
try:
    from tkinter_tooltip import ToolTip
    TOOLTIPS_AVAILABLE = True
except ImportError:
    TOOLTIPS_AVAILABLE = False
    
    # Simple fallback tooltip class
    class ToolTip:
        def __init__(self, widget, text, delay=500):
            self.widget = widget
            self.text = text
            self.widget.bind('<Enter>', self.on_enter)
            self.widget.bind('<Leave>', self.on_leave)
            
        def on_enter(self, event=None):
            pass  # Simple fallback - no tooltip display
            
        def on_leave(self, event=None):
            pass

# Import our modules
try:
    import downloader
    import extractor
    import indexer
    import grouper
    MODULES_AVAILABLE = True
except ImportError as e:
    MODULES_AVAILABLE = False
    import_error = str(e)


class StatusUpdater:
    """Thread-safe status update handler."""
    
    def __init__(self, status_queue):
        self.queue = status_queue
    
    def update(self, message, progress=None):
        """Update status message and optional progress."""
        self.queue.put({'type': 'status', 'message': message, 'progress': progress})
    
    def log(self, message):
        """Add log message."""
        self.queue.put({'type': 'log', 'message': message})
    
    def error(self, message):
        """Add error message."""
        self.queue.put({'type': 'error', 'message': message})
    
    def complete(self, message):
        """Mark operation as complete."""
        self.queue.put({'type': 'complete', 'message': message})


class DocumentAnalysisGUI:
    """Main GUI application for document analysis."""
    
    def __init__(self, root):
        """Initialize the GUI application."""
        self.root = root
        self.root.title("Public Comment Analysis Tool - GUI")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        
        # Configure style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Status queue for thread communication
        self.status_queue = queue.Queue()
        self.status_updater = StatusUpdater(self.status_queue)
        
        # Application state
        self.current_csv_file = None
        self.downloads_complete = False
        self.extraction_complete = False
        self.indexing_complete = False
        self.clustering_complete = False
        
        # Setup UI
        self.setup_ui()
        self.setup_menu()
        
        # Start status update checker
        self.check_status_updates()
        
        # Check module availability
        if not MODULES_AVAILABLE:
            self.show_error(f"Module import error: {import_error}")
    
    def setup_ui(self):
        """Setup the main user interface."""
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title and instructions
        self.setup_header(main_frame)
        
        # Notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # Create tabs
        self.setup_welcome_tab()
        self.setup_download_tab()
        self.setup_extract_tab()
        self.setup_search_tab()
        self.setup_cluster_tab()
        self.setup_results_tab()
        
        # Status bar
        self.setup_status_bar(main_frame)
    
    def setup_header(self, parent):
        """Setup application header with title and instructions."""
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Title
        title_font = Font(size=16, weight='bold')
        title_label = ttk.Label(header_frame, text="📄 Public Comment Analysis Tool", font=title_font)
        title_label.pack()
        
        # Subtitle
        subtitle_label = ttk.Label(header_frame, 
                                  text="Download → Extract → Search → Analyze documents with AI-powered clustering")
        subtitle_label.pack(pady=(5, 0))
        
        # Progress indicator
        self.progress_frame = ttk.Frame(header_frame)
        self.progress_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Step indicators
        steps = ["📁 Load CSV", "⬇️ Download", "📝 Extract", "🔍 Index", "🎯 Cluster", "📊 Results"]
        self.step_labels = []
        
        for i, step in enumerate(steps):
            label = ttk.Label(self.progress_frame, text=step, foreground='gray')
            label.pack(side=tk.LEFT, padx=10)
            self.step_labels.append(label)
    
    def setup_menu(self):
        """Setup application menu bar."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open CSV...", command=self.load_csv_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Install Dependencies", command=self.install_dependencies)
        tools_menu.add_command(label="Open Output Folder", command=self.open_output_folder)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="User Guide", command=self.show_help)
        help_menu.add_command(label="About", command=self.show_about)
    
    def setup_welcome_tab(self):
        """Setup welcome/getting started tab."""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="🏠 Welcome")
        
        # Welcome content
        welcome_frame = ttk.Frame(tab)
        welcome_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Welcome title
        welcome_font = Font(size=14, weight='bold')
        ttk.Label(welcome_frame, text="Welcome to the Public Comment Analysis Tool!", 
                 font=welcome_font).pack(pady=(0, 20))
        
        # Instructions
        instructions = """
🚀 Getting Started:

1. 📁 Prepare Your Data
   • Create a CSV file with document URLs
   • Required column: "Attachment Files" (URLs to PDF/DOCX files)
   • Optional: "Document ID", "Organization Name", "Category"

2. ⬇️ Download Documents
   • Load your CSV file in the Download tab
   • Click "Start Download" to fetch all documents
   • Progress will be shown with retry for failed downloads

3. 📝 Extract Text
   • Automatically processes PDFs and DOCX files
   • Uses OCR for scanned documents
   • Direct text extraction for text-based files

4. 🔍 Build Search Index
   • Creates searchable database
   • Enables fast keyword and phrase searches
   • Supports boolean operators and wildcards

5. 🎯 Cluster Documents
   • Groups similar documents automatically
   • Multiple AI methods: BERTopic, TF-IDF, LDA
   • Identifies topics and themes

6. 📊 View Results
   • Browse clustered documents
   • Search and filter results
   • Export comprehensive reports

📋 Sample CSV Format:
Document ID,Organization Name,Category,Attachment Files
DOC-001,Example Org,Healthcare,https://example.com/doc1.pdf
DOC-002,Another Org,Education,https://example.com/doc2.pdf
        """
        
        text_widget = scrolledtext.ScrolledText(welcome_frame, wrap=tk.WORD, height=25, width=80)
        text_widget.pack(fill=tk.BOTH, expand=True)
        text_widget.insert(tk.END, instructions)
        text_widget.config(state=tk.DISABLED)
        
        # Quick start buttons
        button_frame = ttk.Frame(welcome_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(button_frame, text="📁 Load CSV File", 
                  command=self.load_csv_file).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="🔧 Install Dependencies", 
                  command=self.install_dependencies).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="📖 Open User Guide", 
                  command=self.show_help).pack(side=tk.LEFT)
    
    def setup_download_tab(self):
        """Setup document download tab."""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="⬇️ Download")
        
        # Main container
        main_container = ttk.Frame(tab)
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Instructions
        ttk.Label(main_container, text="📁 Document Download", 
                 font=Font(size=12, weight='bold')).pack(anchor=tk.W)
        ttk.Label(main_container, 
                 text="Load a CSV file containing document URLs and download all linked files.").pack(anchor=tk.W, pady=(5, 20))
        
        # File selection
        file_frame = ttk.LabelFrame(main_container, text="CSV File Selection", padding=15)
        file_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.csv_file_var = tk.StringVar()
        ttk.Label(file_frame, text="CSV File:").pack(anchor=tk.W)
        
        csv_entry_frame = ttk.Frame(file_frame)
        csv_entry_frame.pack(fill=tk.X, pady=(5, 10))
        
        self.csv_entry = ttk.Entry(csv_entry_frame, textvariable=self.csv_file_var, state='readonly')
        self.csv_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        browse_btn = ttk.Button(csv_entry_frame, text="Browse...", command=self.load_csv_file)
        browse_btn.pack(side=tk.RIGHT, padx=(10, 0))
        
        if TOOLTIPS_AVAILABLE:
            ToolTip(browse_btn, "Select a CSV file with document URLs in 'Attachment Files' column")
        
        # Download options
        options_frame = ttk.LabelFrame(main_container, text="Download Options", padding=15)
        options_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.download_dir_var = tk.StringVar(value="downloads")
        ttk.Label(options_frame, text="Download Directory:").pack(anchor=tk.W)
        dir_entry_frame = ttk.Frame(options_frame)
        dir_entry_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Entry(dir_entry_frame, textvariable=self.download_dir_var).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(dir_entry_frame, text="📁", command=self.select_download_dir).pack(side=tk.RIGHT, padx=(10, 0))
        
        # Progress and controls
        progress_frame = ttk.LabelFrame(main_container, text="Download Progress", padding=15)
        progress_frame.pack(fill=tk.BOTH, expand=True)
        
        self.download_progress = ttk.Progressbar(progress_frame, mode='determinate')
        self.download_progress.pack(fill=tk.X, pady=(0, 10))
        
        self.download_status_var = tk.StringVar(value="Ready to download")
        ttk.Label(progress_frame, textvariable=self.download_status_var).pack(anchor=tk.W)
        
        # Download log
        self.download_log = scrolledtext.ScrolledText(progress_frame, height=8)
        self.download_log.pack(fill=tk.BOTH, expand=True, pady=(10, 10))
        
        # Control buttons
        control_frame = ttk.Frame(progress_frame)
        control_frame.pack(fill=tk.X)
        
        self.download_btn = ttk.Button(control_frame, text="🚀 Start Download", 
                                      command=self.start_download, state='disabled')
        self.download_btn.pack(side=tk.LEFT)
        
        if TOOLTIPS_AVAILABLE:
            ToolTip(self.download_btn, "Download all documents from the CSV file with automatic retry")
    
    def setup_extract_tab(self):
        """Setup text extraction tab."""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="📝 Extract")
        
        # Main container
        main_container = ttk.Frame(tab)
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Instructions
        ttk.Label(main_container, text="📝 Text Extraction", 
                 font=Font(size=12, weight='bold')).pack(anchor=tk.W)
        ttk.Label(main_container, 
                 text="Extract text from downloaded PDFs and DOCX files using OCR when needed.").pack(anchor=tk.W, pady=(5, 20))
        
        # Settings
        settings_frame = ttk.LabelFrame(main_container, text="Extraction Settings", padding=15)
        settings_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.input_dir_var = tk.StringVar(value="downloads")
        ttk.Label(settings_frame, text="Input Directory:").pack(anchor=tk.W)
        input_entry_frame = ttk.Frame(settings_frame)
        input_entry_frame.pack(fill=tk.X, pady=(5, 10))
        
        ttk.Entry(input_entry_frame, textvariable=self.input_dir_var).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(input_entry_frame, text="📁", command=self.select_input_dir).pack(side=tk.RIGHT, padx=(10, 0))
        
        self.output_dir_var = tk.StringVar(value="text")
        ttk.Label(settings_frame, text="Output Directory:").pack(anchor=tk.W)
        output_entry_frame = ttk.Frame(settings_frame)
        output_entry_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Entry(output_entry_frame, textvariable=self.output_dir_var).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(output_entry_frame, text="📁", command=self.select_output_dir).pack(side=tk.RIGHT, padx=(10, 0))
        
        # Progress and controls
        progress_frame = ttk.LabelFrame(main_container, text="Extraction Progress", padding=15)
        progress_frame.pack(fill=tk.BOTH, expand=True)
        
        self.extract_progress = ttk.Progressbar(progress_frame, mode='determinate')
        self.extract_progress.pack(fill=tk.X, pady=(0, 10))
        
        self.extract_status_var = tk.StringVar(value="Ready to extract text")
        ttk.Label(progress_frame, textvariable=self.extract_status_var).pack(anchor=tk.W)
        
        # Extraction log
        self.extract_log = scrolledtext.ScrolledText(progress_frame, height=8)
        self.extract_log.pack(fill=tk.BOTH, expand=True, pady=(10, 10))
        
        # Control buttons
        control_frame = ttk.Frame(progress_frame)
        control_frame.pack(fill=tk.X)
        
        self.extract_btn = ttk.Button(control_frame, text="🔤 Start Extraction", 
                                     command=self.start_extraction)
        self.extract_btn.pack(side=tk.LEFT)
        
        if TOOLTIPS_AVAILABLE:
            ToolTip(self.extract_btn, "Extract text from PDFs (with OCR) and DOCX files")
    
    def setup_search_tab(self):
        """Setup search and indexing tab."""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="🔍 Search")
        
        # Main container with paned window
        paned = ttk.PanedWindow(tab, orient=tk.VERTICAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Top frame - indexing
        top_frame = ttk.Frame(paned)
        paned.add(top_frame, weight=1)
        
        # Instructions
        ttk.Label(top_frame, text="🔍 Search Index", 
                 font=Font(size=12, weight='bold')).pack(anchor=tk.W)
        ttk.Label(top_frame, 
                 text="Build a searchable index and search through your documents.").pack(anchor=tk.W, pady=(5, 20))
        
        # Index building
        index_frame = ttk.LabelFrame(top_frame, text="Build Search Index", padding=15)
        index_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.text_dir_var = tk.StringVar(value="text")
        ttk.Label(index_frame, text="Text Directory:").pack(anchor=tk.W)
        text_entry_frame = ttk.Frame(index_frame)
        text_entry_frame.pack(fill=tk.X, pady=(5, 10))
        
        ttk.Entry(text_entry_frame, textvariable=self.text_dir_var).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(text_entry_frame, text="📁", command=self.select_text_dir).pack(side=tk.RIGHT, padx=(10, 0))
        
        # Index progress
        self.index_progress = ttk.Progressbar(index_frame, mode='indeterminate')
        self.index_progress.pack(fill=tk.X, pady=(0, 10))
        
        self.index_status_var = tk.StringVar(value="Ready to build index")
        ttk.Label(index_frame, textvariable=self.index_status_var).pack(anchor=tk.W)
        
        # Index button
        self.index_btn = ttk.Button(index_frame, text="🏗️ Build Index", command=self.start_indexing)
        self.index_btn.pack(pady=(10, 0))
        
        # Bottom frame - searching
        bottom_frame = ttk.Frame(paned)
        paned.add(bottom_frame, weight=2)
        
        # Search interface
        search_frame = ttk.LabelFrame(bottom_frame, text="Search Documents", padding=15)
        search_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # Search entry
        search_entry_frame = ttk.Frame(search_frame)
        search_entry_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(search_entry_frame, text="Search Query:").pack(anchor=tk.W)
        query_frame = ttk.Frame(search_entry_frame)
        query_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(query_frame, textvariable=self.search_var)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.search_entry.bind('<Return>', lambda e: self.perform_search())
        
        self.search_btn = ttk.Button(query_frame, text="🔍 Search", command=self.perform_search)
        self.search_btn.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Search options
        options_frame = ttk.Frame(search_frame)
        options_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(options_frame, text="Limit:").pack(side=tk.LEFT)
        self.search_limit_var = tk.StringVar(value="20")
        limit_spinbox = ttk.Spinbox(options_frame, from_=1, to=100, width=5, textvariable=self.search_limit_var)
        limit_spinbox.pack(side=tk.LEFT, padx=(5, 20))
        
        # Search help
        help_text = "💡 Tips: Use quotes for phrases \"exact phrase\", OR/AND for boolean, * for wildcards"
        ttk.Label(options_frame, text=help_text, foreground='blue').pack(side=tk.LEFT)
        
        # Search results
        self.search_results = scrolledtext.ScrolledText(search_frame, height=12)
        self.search_results.pack(fill=tk.BOTH, expand=True)
    
    def setup_cluster_tab(self):
        """Setup document clustering tab."""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="🎯 Cluster")
        
        # Main container
        main_container = ttk.Frame(tab)
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Instructions
        ttk.Label(main_container, text="🎯 Document Clustering", 
                 font=Font(size=12, weight='bold')).pack(anchor=tk.W)
        ttk.Label(main_container, 
                 text="Group similar documents using AI-powered clustering methods.").pack(anchor=tk.W, pady=(5, 20))
        
        # Method selection
        method_frame = ttk.LabelFrame(main_container, text="Clustering Method", padding=15)
        method_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.cluster_method_var = tk.StringVar(value="bertopic")
        
        methods = [
            ("bertopic", "🧠 BERTopic (Recommended)", "Advanced topic modeling with BERT embeddings - Best quality"),
            ("tfidf_kmeans", "⚡ TF-IDF + KMeans", "Fast classical clustering - Good performance"),
            ("lda", "📊 LDA Topic Modeling", "Statistical topic modeling - Memory efficient")
        ]
        
        for value, text, description in methods:
            frame = ttk.Frame(method_frame)
            frame.pack(fill=tk.X, pady=2)
            
            radio = ttk.Radiobutton(frame, text=text, variable=self.cluster_method_var, value=value)
            radio.pack(side=tk.LEFT)
            
            desc_label = ttk.Label(frame, text=f" - {description}", foreground='gray')
            desc_label.pack(side=tk.LEFT)
        
        # Clustering options
        options_frame = ttk.LabelFrame(main_container, text="Clustering Options", padding=15)
        options_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Number of clusters (for non-BERTopic methods)
        clusters_frame = ttk.Frame(options_frame)
        clusters_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(clusters_frame, text="Number of Clusters:").pack(side=tk.LEFT)
        self.clusters_var = tk.StringVar(value="auto")
        clusters_combo = ttk.Combobox(clusters_frame, textvariable=self.clusters_var, 
                                     values=["auto", "3", "4", "5", "6", "7", "8", "10"], width=10)
        clusters_combo.pack(side=tk.LEFT, padx=(10, 20))
        
        ttk.Label(clusters_frame, text="(auto-detection recommended)", foreground='gray').pack(side=tk.LEFT)
        
        # Progress and controls
        progress_frame = ttk.LabelFrame(main_container, text="Clustering Progress", padding=15)
        progress_frame.pack(fill=tk.BOTH, expand=True)
        
        self.cluster_progress = ttk.Progressbar(progress_frame, mode='indeterminate')
        self.cluster_progress.pack(fill=tk.X, pady=(0, 10))
        
        self.cluster_status_var = tk.StringVar(value="Ready to cluster documents")
        ttk.Label(progress_frame, textvariable=self.cluster_status_var).pack(anchor=tk.W)
        
        # Clustering log
        self.cluster_log = scrolledtext.ScrolledText(progress_frame, height=8)
        self.cluster_log.pack(fill=tk.BOTH, expand=True, pady=(10, 10))
        
        # Control buttons
        control_frame = ttk.Frame(progress_frame)
        control_frame.pack(fill=tk.X)
        
        self.cluster_btn = ttk.Button(control_frame, text="🚀 Start Clustering", 
                                     command=self.start_clustering)
        self.cluster_btn.pack(side=tk.LEFT)
        
        if TOOLTIPS_AVAILABLE:
            ToolTip(self.cluster_btn, "Group documents by topic and theme using machine learning")
    
    def setup_results_tab(self):
        """Setup results viewing tab."""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="📊 Results")
        
        # Main container
        main_container = ttk.Frame(tab)
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Instructions
        ttk.Label(main_container, text="📊 Analysis Results", 
                 font=Font(size=12, weight='bold')).pack(anchor=tk.W)
        ttk.Label(main_container, 
                 text="View clustering results, export reports, and explore your document collection.").pack(anchor=tk.W, pady=(5, 20))
        
        # Results summary
        summary_frame = ttk.LabelFrame(main_container, text="Processing Summary", padding=15)
        summary_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.summary_text = tk.Text(summary_frame, height=4, wrap=tk.WORD)
        self.summary_text.pack(fill=tk.X)
        self.summary_text.config(state=tk.DISABLED)
        
        # Export options
        export_frame = ttk.LabelFrame(main_container, text="Export Results", padding=15)
        export_frame.pack(fill=tk.X, pady=(0, 20))
        
        export_buttons_frame = ttk.Frame(export_frame)
        export_buttons_frame.pack(fill=tk.X)
        
        ttk.Button(export_buttons_frame, text="📂 Open Output Folder", 
                  command=self.open_output_folder).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(export_buttons_frame, text="📊 View Clustering CSV", 
                  command=self.view_clustering_csv).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(export_buttons_frame, text="🔍 Open Search Database", 
                  command=self.open_search_database).pack(side=tk.LEFT)
        
        # Recent results viewer
        results_frame = ttk.LabelFrame(main_container, text="Recent Results", padding=15)
        results_frame.pack(fill=tk.BOTH, expand=True)
        
        # Results tree view
        columns = ("File", "Cluster", "Organization", "Keywords")
        self.results_tree = ttk.Treeview(results_frame, columns=columns, show='headings', height=12)
        
        for col in columns:
            self.results_tree.heading(col, text=col)
            self.results_tree.column(col, width=200)
        
        # Scrollbar for tree
        tree_scroll = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.results_tree.yview)
        self.results_tree.configure(yscrollcommand=tree_scroll.set)
        
        # Pack tree and scrollbar
        self.results_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Refresh button
        ttk.Button(results_frame, text="🔄 Refresh Results", 
                  command=self.refresh_results).pack(pady=(10, 0))
    
    def setup_status_bar(self, parent):
        """Setup status bar at bottom."""
        status_frame = ttk.Frame(parent)
        status_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Status label
        self.status_var = tk.StringVar(value="Ready - Load a CSV file to begin")
        status_label = ttk.Label(status_frame, textvariable=self.status_var)
        status_label.pack(side=tk.LEFT)
        
        # Progress bar
        self.main_progress = ttk.Progressbar(status_frame, mode='determinate', length=200)
        self.main_progress.pack(side=tk.RIGHT, padx=(10, 0))
    
    def check_status_updates(self):
        """Check for status updates from worker threads."""
        try:
            while True:
                update = self.status_queue.get_nowait()
                self.handle_status_update(update)
        except queue.Empty:
            pass
        
        # Schedule next check
        self.root.after(100, self.check_status_updates)
    
    def handle_status_update(self, update):
        """Handle a status update from worker thread."""
        update_type = update['type']
        message = update['message']
        
        if update_type == 'status':
            self.status_var.set(message)
            if 'progress' in update and update['progress'] is not None:
                progress = update['progress']
                if isinstance(progress, tuple):
                    current, total = progress
                    if total > 0:
                        self.main_progress['value'] = (current / total) * 100
                else:
                    self.main_progress['value'] = progress
        
        elif update_type == 'log':
            # Add to appropriate log based on current operation
            current_tab = self.notebook.select()
            tab_text = self.notebook.tab(current_tab, "text")
            
            timestamp = datetime.now().strftime("%H:%M:%S")
            log_message = f"[{timestamp}] {message}\n"
            
            if "Download" in tab_text:
                self.download_log.insert(tk.END, log_message)
                self.download_log.see(tk.END)
            elif "Extract" in tab_text:
                self.extract_log.insert(tk.END, log_message)
                self.extract_log.see(tk.END)
            elif "Cluster" in tab_text:
                self.cluster_log.insert(tk.END, log_message)
                self.cluster_log.see(tk.END)
        
        elif update_type == 'error':
            self.show_error(message)
        
        elif update_type == 'complete':
            self.status_var.set(message)
            self.main_progress['value'] = 100
            messagebox.showinfo("Complete", message)
    
    def load_csv_file(self):
        """Load CSV file for processing."""
        filename = filedialog.askopenfilename(
            title="Select CSV File",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if filename:
            self.current_csv_file = filename
            self.csv_file_var.set(filename)
            self.download_btn.config(state='normal')
            self.step_labels[0].config(foreground='green')
            self.status_var.set(f"Loaded: {Path(filename).name}")
            
            # Try to load and preview CSV
            try:
                import pandas as pd
                df = pd.read_csv(filename)
                rows = len(df)
                self.status_updater.log(f"CSV loaded: {rows} rows found")
                
                # Check for required columns
                if 'Attachment Files' in df.columns:
                    urls_with_data = df['Attachment Files'].dropna()
                    self.status_updater.log(f"Found {len(urls_with_data)} rows with URLs")
                else:
                    self.show_error("Warning: 'Attachment Files' column not found in CSV")
                    
            except Exception as e:
                self.show_error(f"Error reading CSV: {str(e)}")
    
    def select_download_dir(self):
        """Select download directory."""
        directory = filedialog.askdirectory(title="Select Download Directory")
        if directory:
            self.download_dir_var.set(directory)
    
    def select_input_dir(self):
        """Select input directory for extraction."""
        directory = filedialog.askdirectory(title="Select Input Directory")
        if directory:
            self.input_dir_var.set(directory)
    
    def select_output_dir(self):
        """Select output directory for extraction."""
        directory = filedialog.askdirectory(title="Select Output Directory")
        if directory:
            self.output_dir_var.set(directory)
    
    def select_text_dir(self):
        """Select text directory for indexing."""
        directory = filedialog.askdirectory(title="Select Text Directory")
        if directory:
            self.text_dir_var.set(directory)
    
    def start_download(self):
        """Start document download process."""
        if not self.current_csv_file:
            self.show_error("Please select a CSV file first")
            return
        
        def download_worker():
            try:
                self.status_updater.update("Starting download...")
                self.download_progress.config(mode='indeterminate')
                self.download_progress.start()
                
                # Import and run downloader
                successful, failed = downloader.download_documents(
                    self.current_csv_file,
                    self.download_dir_var.get()
                )
                
                self.download_progress.stop()
                self.download_progress.config(mode='determinate', value=100)
                
                self.downloads_complete = True
                self.step_labels[1].config(foreground='green')
                
                message = f"Download complete: {successful} successful, {failed} failed"
                self.status_updater.complete(message)
                self.status_updater.log(message)
                
            except Exception as e:
                self.download_progress.stop()
                self.status_updater.error(f"Download failed: {str(e)}")
        
        # Start download in background thread
        self.download_btn.config(state='disabled')
        thread = threading.Thread(target=download_worker, daemon=True)
        thread.start()
    
    def start_extraction(self):
        """Start text extraction process."""
        def extract_worker():
            try:
                self.status_updater.update("Starting text extraction...")
                self.extract_progress.config(mode='indeterminate')
                self.extract_progress.start()
                
                # Import and run extractor
                stats = extractor.process_documents(
                    self.input_dir_var.get(),
                    self.output_dir_var.get()
                )
                
                self.extract_progress.stop()
                self.extract_progress.config(mode='determinate', value=100)
                
                self.extraction_complete = True
                self.step_labels[2].config(foreground='green')
                
                message = f"Extraction complete: {stats['successful']}/{stats['total_files']} files processed"
                self.status_updater.complete(message)
                self.status_updater.log(message)
                
            except Exception as e:
                self.extract_progress.stop()
                self.status_updater.error(f"Extraction failed: {str(e)}")
        
        # Start extraction in background thread
        self.extract_btn.config(state='disabled')
        thread = threading.Thread(target=extract_worker, daemon=True)
        thread.start()
    
    def start_indexing(self):
        """Start search index building."""
        def index_worker():
            try:
                self.status_updater.update("Building search index...")
                self.index_progress.start()
                
                # Import and run indexer
                stats = indexer.build_search_index(
                    self.text_dir_var.get(),
                    self.current_csv_file or "input/comment_links.csv"
                )
                
                self.index_progress.stop()
                
                self.indexing_complete = True
                self.step_labels[3].config(foreground='green')
                
                message = f"Index complete: {stats['indexed']} documents indexed"
                self.status_updater.complete(message)
                self.status_updater.log(message)
                
                # Enable search
                self.search_btn.config(state='normal')
                
            except Exception as e:
                self.index_progress.stop()
                self.status_updater.error(f"Indexing failed: {str(e)}")
        
        # Start indexing in background thread
        self.index_btn.config(state='disabled')
        thread = threading.Thread(target=index_worker, daemon=True)
        thread.start()
    
    def perform_search(self):
        """Perform document search."""
        query = self.search_var.get().strip()
        if not query:
            return
        
        try:
            limit = int(self.search_limit_var.get())
            results = indexer.search_documents(query, limit=limit)
            
            # Clear previous results
            self.search_results.delete(1.0, tk.END)
            
            if results:
                self.search_results.insert(tk.END, f"Search Results for: '{query}'\n")
                self.search_results.insert(tk.END, "=" * 60 + "\n\n")
                
                for i, result in enumerate(results, 1):
                    self.search_results.insert(tk.END, f"{i}. {result['filename']}\n")
                    
                    if result['organization']:
                        self.search_results.insert(tk.END, f"   Organization: {result['organization']}\n")
                    
                    self.search_results.insert(tk.END, f"   Document ID: {result['document_id']}\n")
                    self.search_results.insert(tk.END, f"   Size: {result['character_count']:,} characters\n")
                    
                    if result['snippet']:
                        # Remove HTML tags for display
                        import re
                        clean_snippet = re.sub(r'<[^>]+>', '**', result['snippet'])
                        self.search_results.insert(tk.END, f"   Snippet: {clean_snippet}\n")
                    
                    self.search_results.insert(tk.END, f"   Relevance: {result['rank']:.4f}\n\n")
                
                self.search_results.insert(tk.END, f"Found {len(results)} matching documents.\n")
            else:
                self.search_results.insert(tk.END, f"No results found for: '{query}'\n")
                
        except Exception as e:
            self.show_error(f"Search error: {str(e)}")
    
    def start_clustering(self):
        """Start document clustering process."""
        def cluster_worker():
            try:
                method = self.cluster_method_var.get()
                self.status_updater.update(f"Starting clustering with {method}...")
                self.cluster_progress.start()
                
                # Prepare clustering parameters
                kwargs = {}
                if self.clusters_var.get() != "auto":
                    clusters = int(self.clusters_var.get())
                    if method == 'tfidf_kmeans':
                        kwargs['n_clusters'] = clusters
                    elif method == 'lda':
                        kwargs['n_topics'] = clusters
                
                # Import and run grouper
                output_file = grouper.group_documents(
                    text_dir=self.text_dir_var.get(),
                    csv_path=self.current_csv_file or "input/comment_links.csv",
                    method=method,
                    output_path=f"output/{method}_results.csv",
                    **kwargs
                )
                
                self.cluster_progress.stop()
                
                self.clustering_complete = True
                self.step_labels[4].config(foreground='green')
                self.step_labels[5].config(foreground='green')
                
                message = f"Clustering complete: Results saved to {output_file}"
                self.status_updater.complete(message)
                self.status_updater.log(message)
                
                # Refresh results view
                self.refresh_results()
                
            except Exception as e:
                self.cluster_progress.stop()
                self.status_updater.error(f"Clustering failed: {str(e)}")
        
        # Start clustering in background thread
        self.cluster_btn.config(state='disabled')
        thread = threading.Thread(target=cluster_worker, daemon=True)
        thread.start()
    
    def refresh_results(self):
        """Refresh results display."""
        # Clear existing items
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        
        # Load latest clustering results
        result_files = []
        output_dir = Path("output")
        
        if output_dir.exists():
            for pattern in ["*results.csv"]:
                result_files.extend(output_dir.glob(pattern))
        
        if result_files:
            # Get most recent file
            latest_file = max(result_files, key=lambda f: f.stat().st_mtime)
            
            try:
                import pandas as pd
                df = pd.read_csv(latest_file)
                
                # Add rows to tree
                for _, row in df.head(50).iterrows():  # Show first 50 results
                    values = (
                        row.get('filename', ''),
                        f"Cluster {row.get('cluster_id', 'N/A')}",
                        row.get('organization', '')[:30],  # Truncate long names
                        row.get('document_keywords_tfidf', '')[:50]  # Truncate keywords
                    )
                    self.results_tree.insert('', 'end', values=values)
                
                # Update summary
                self.update_summary(df, latest_file.name)
                
            except Exception as e:
                self.show_error(f"Error loading results: {str(e)}")
    
    def update_summary(self, df, filename):
        """Update processing summary."""
        self.summary_text.config(state=tk.NORMAL)
        self.summary_text.delete(1.0, tk.END)
        
        total_docs = len(df)
        clusters = df['cluster_id'].nunique() if 'cluster_id' in df.columns else 0
        method = df['clustering_method'].iloc[0] if 'clustering_method' in df.columns else 'Unknown'
        
        summary = f"""📊 Processing Complete - {filename}
Documents: {total_docs} | Clusters: {clusters} | Method: {method.upper()}
Latest Results: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Output Directory: ./output/ | Search Database: ./output/document_index.db"""
        
        self.summary_text.insert(tk.END, summary)
        self.summary_text.config(state=tk.DISABLED)
    
    def view_clustering_csv(self):
        """Open clustering CSV in default application."""
        output_dir = Path("output")
        if output_dir.exists():
            csv_files = list(output_dir.glob("*results.csv"))
            if csv_files:
                latest_file = max(csv_files, key=lambda f: f.stat().st_mtime)
                try:
                    import subprocess
                    subprocess.run(['start', str(latest_file)], shell=True, check=True)
                except Exception:
                    self.show_error(f"Cannot open {latest_file}. Please open manually.")
            else:
                self.show_error("No clustering results found. Run clustering first.")
        else:
            self.show_error("Output directory not found.")
    
    def open_output_folder(self):
        """Open output folder in file explorer."""
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        
        try:
            import subprocess
            subprocess.run(['explorer', str(output_dir)], check=True)
        except Exception:
            self.show_error(f"Cannot open {output_dir}. Please open manually.")
    
    def open_search_database(self):
        """Information about search database."""
        db_path = Path("output/document_index.db")
        if db_path.exists():
            messagebox.showinfo("Search Database", 
                              f"Search database location:\n{db_path.absolute()}\n\n"
                              f"Size: {db_path.stat().st_size:,} bytes\n"
                              f"Use the Search tab to query documents.")
        else:
            self.show_error("Search database not found. Build index first.")
    
    def install_dependencies(self):
        """Run dependency installer."""
        try:
            import subprocess
            subprocess.run([sys.executable, "install_windows_dependencies.py"], check=True)
            messagebox.showinfo("Dependencies", "Dependency installation completed!")
        except Exception as e:
            self.show_error(f"Dependency installation error: {str(e)}")
    
    def show_help(self):
        """Show help documentation."""
        help_window = tk.Toplevel(self.root)
        help_window.title("User Guide")
        help_window.geometry("600x500")
        
        help_text = scrolledtext.ScrolledText(help_window, wrap=tk.WORD)
        help_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        help_content = """
PUBLIC COMMENT ANALYSIS TOOL - USER GUIDE

🚀 QUICK START:
1. Prepare CSV file with document URLs
2. Load CSV in Download tab
3. Download all documents
4. Extract text from documents  
5. Build search index
6. Cluster documents by topic
7. View and export results

📋 CSV FORMAT:
Required columns:
- Attachment Files: URLs to PDF/DOCX files

Optional columns:
- Document ID: Unique identifier
- Organization Name: Source organization
- Category: Document category
- Comment: Description text

🔍 SEARCH FEATURES:
- Keyword search: single words
- Phrase search: "exact phrase"
- Boolean search: word1 AND word2
- Wildcard search: hospital*
- Limit results: 1-100 documents

🎯 CLUSTERING METHODS:

BERTopic (Recommended):
+ Best quality topic discovery
+ Advanced BERT embeddings
- Slower processing time

TF-IDF + KMeans:
+ Fast and reliable
+ Good for large datasets
- Less semantic understanding

LDA Topic Modeling:
+ Memory efficient
+ Statistical approach
- May need manual tuning

📊 OUTPUT FILES:
- output/[method]_results.csv: Clustering results
- output/document_index.db: Search database
- text/*.txt: Extracted text files
- logs/*.log: Processing logs

🔧 TROUBLESHOOTING:
- Dependencies: Use Tools > Install Dependencies
- Slow OCR: Check Tesseract installation
- Search errors: Rebuild index
- Memory issues: Process smaller batches

💡 TIPS:
- Use auto cluster detection for best results
- BERTopic works best with 20+ documents
- Check logs tab for detailed progress
- Export results before closing application
        """
        
        help_text.insert(tk.END, help_content)
        help_text.config(state=tk.DISABLED)
    
    def show_about(self):
        """Show about dialog."""
        messagebox.showinfo("About", 
                          "Public Comment Analysis Tool v1.0\n\n"
                          "A comprehensive tool for downloading, processing,\n"
                          "and analyzing public comment documents.\n\n"
                          "Features:\n"
                          "• Bulk document download\n"
                          "• OCR text extraction\n" 
                          "• Full-text search\n"
                          "• AI-powered clustering\n"
                          "• Export capabilities\n\n"
                          "Built with Python, scikit-learn, BERTopic, and love.")
    
    def show_error(self, message):
        """Show error message."""
        messagebox.showerror("Error", message)


def main():
    """Main entry point for GUI application."""
    root = tk.Tk()
    
    # Set application icon (if available)
    try:
        root.iconbitmap('icon.ico')  # You can add an icon file
    except:
        pass
    
    app = DocumentAnalysisGUI(root)
    
    # Center window on screen
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    
    root.mainloop()


if __name__ == "__main__":
    main()