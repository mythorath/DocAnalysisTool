#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Local Document Processing Tool - Lite Version
Simplified processor that works with minimal dependencies.
"""

import os
import sys
import json
import uuid
import sqlite3
from datetime import datetime
from pathlib import Path
import argparse
import logging

# Try to import OpenAI analyzer
try:
    from openai_document_analyzer import OpenAIDocumentAnalyzer
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

# Windows console emoji compatibility
def safe_print(text):
    """Print text with emoji fallbacks for Windows console."""
    if os.name == 'nt':
        # Replace problematic emojis with ASCII equivalents
        text = (text.replace('🚀', '[GPU]')
                   .replace('✅', '[OK]')
                   .replace('❌', '[ERROR]')
                   .replace('⚠️', '[WARNING]')
                   .replace('📄', '[DOCS]')
                   .replace('📊', '[DATA]')
                   .replace('🔧', '[TOOL]')
                   .replace('💡', '[TIP]')
                   .replace('📁', '[FILES]')
                   .replace('🗂️', '[FOLDER]')
                   .replace('📋', '[LIST]')
                   .replace('📦', '[DEPS]')
                   .replace('🔥', '[PROCESS]')
                   .replace('💾', '[DB]')
                   .replace('🎉', '[COMPLETE]')
                   .replace('🔍', '[SEARCH]')
                   .replace('📎', '[LINK]')
                   .replace('📥', '[DOWNLOAD]')
                   .replace('📝', '[EXTRACT]')
                   .replace('📈', '[COUNT]')
                   .replace('👤', '[USER]')
                   .replace('🤖', '[AI]')
                   .replace('✨', '[ENHANCE]')
                   .replace('🎯', '[TARGET]'))
    try:
        print(text)
    except UnicodeEncodeError:
        # Final fallback - remove all non-ASCII characters
        print(text.encode('ascii', 'ignore').decode('ascii'))

# Try to import pandas, fallback to basic CSV handling
try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    import csv
    HAS_PANDAS = False

# Try to import requests for downloads
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

class SimpleDownloader:
    """Simple document downloader without heavy dependencies."""
    
    def __init__(self, downloads_dir="downloads", logs_dir="logs"):
        self.downloads_dir = Path(downloads_dir)
        self.logs_dir = Path(logs_dir)
        self.downloads_dir.mkdir(exist_ok=True)
        self.logs_dir.mkdir(exist_ok=True)
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.logs_dir / 'downloader.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def download_file(self, url, filename):
        """Download a single file."""
        if not HAS_REQUESTS:
            self.logger.warning("Requests not available - cannot download files")
            return False
            
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            filepath = self.downloads_dir / filename
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            self.logger.info(f"Downloaded: {filename}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to download {url}: {e}")
            return False
    
    def download_from_csv(self, csv_file):
        """Download files listed in CSV."""
        successful = 0
        failed = 0
        
        # Determine URL column name
        url_column = 'URL'  # default
        if HAS_PANDAS:
            df = pd.read_csv(csv_file)
            for col in df.columns:
                if col.lower() in ['url', 'attachment files', 'attachment_files', 'attachments']:
                    url_column = col
                    break
            
            for idx, row in df.iterrows():
                doc_id = str(row.get('Document ID', ''))
                urls_field = str(row.get(url_column, ''))
                
                # Auto-generate Document ID if missing
                if not doc_id or doc_id == 'nan' or doc_id == '':
                    if urls_field and urls_field != 'nan':
                        # Extract from URL pattern (e.g., CMS-2025-0028-0002 from URL)
                        import re
                        url_match = re.search(r'([A-Z0-9-]+(?:-\d+){3,})', urls_field)
                        if url_match:
                            doc_id = url_match.group(1)
                        else:
                            # Fallback: use row index
                            doc_id = f"DOC-{idx+1:04d}"
                
                if urls_field and urls_field != 'nan':
                    # Handle multiple URLs separated by commas
                    urls = [url.strip() for url in urls_field.split(',') if url.strip()]
                    
                    for i, url in enumerate(urls):
                        # Extract file extension from URL
                        import urllib.parse
                        parsed_url = urllib.parse.urlparse(url)
                        url_path = parsed_url.path
                        if url_path.endswith('.pdf'):
                            extension = '.pdf'
                        elif url_path.endswith('.docx'):
                            extension = '.docx'
                        elif url_path.endswith('.doc'):
                            extension = '.doc'
                        else:
                            extension = '.pdf'  # default
                        
                        if i == 0:
                            filename = f"{doc_id}{extension}"  # Main file
                        else:
                            filename = f"{doc_id}_attachment_{i+1}{extension}"  # Additional files
                        
                        if self.download_file(url, filename):
                            successful += 1
                        else:
                            failed += 1
        else:
            # Basic CSV reading without pandas
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                headers = reader.fieldnames
                
                # Find URL column
                for col in headers:
                    if col.lower() in ['url', 'attachment files', 'attachment_files', 'attachments']:
                        url_column = col
                        break
                
                for idx, row in enumerate(reader):
                    doc_id = row.get('Document ID', '')
                    urls_field = row.get(url_column, '')
                    
                    # Auto-generate Document ID if missing
                    if not doc_id:
                        if urls_field:
                            # Extract from URL pattern (e.g., CMS-2025-0028-0002 from URL)
                            import re
                            url_match = re.search(r'([A-Z0-9-]+(?:-\d+){3,})', urls_field)
                            if url_match:
                                doc_id = url_match.group(1)
                            else:
                                # Fallback: use row index
                                doc_id = f"DOC-{idx+1:04d}"
                    
                    if urls_field:
                        urls = [url.strip() for url in urls_field.split(',') if url.strip()]
                        
                        for i, url in enumerate(urls):
                            # Extract file extension from URL
                            import urllib.parse
                            parsed_url = urllib.parse.urlparse(url)
                            url_path = parsed_url.path
                            if url_path.endswith('.pdf'):
                                extension = '.pdf'
                            elif url_path.endswith('.docx'):
                                extension = '.docx'
                            elif url_path.endswith('.doc'):
                                extension = '.doc'
                            else:
                                extension = '.pdf'  # default
                            
                            if i == 0:
                                filename = f"{doc_id}{extension}"
                            else:
                                filename = f"{doc_id}_attachment_{i+1}{extension}"
                            
                            if self.download_file(url, filename):
                                successful += 1
                            else:
                                failed += 1
        
        return {'successful': successful, 'failed': failed}

class SimpleTextExtractor:
    """Simple text extractor with fallback methods and optional GPU acceleration."""
    
    def __init__(self, use_gpu=False):
        self.logger = logging.getLogger(__name__)
        self.use_gpu = use_gpu
        
        # Check available extraction methods
        self.has_pymupdf = False
        self.has_docx = False
        
        try:
            import fitz
            self.has_pymupdf = True
        except ImportError:
            pass
            
        try:
            from docx import Document
            self.has_docx = True
        except ImportError:
            pass
        
        # Try to initialize GPU extractor if requested
        self.gpu_extractor = None
        if use_gpu:
            try:
                from gpu_enhanced_processor import GPUEnhancedExtractor
                self.gpu_extractor = GPUEnhancedExtractor(use_gpu=True)
                self.logger.info("🚀 GPU-enhanced extraction initialized")
            except ImportError as e:
                self.logger.warning(f"⚠️ GPU extraction not available: {e}")
                self.logger.info("💡 Install requirements_gpu.txt for GPU acceleration")
            except Exception as e:
                self.logger.warning(f"⚠️ GPU extraction failed to initialize: {e}")
                self.gpu_extractor = None
    
    def extract_pdf_text(self, pdf_path):
        """Extract text from PDF."""
        if not self.has_pymupdf:
            self.logger.warning("PyMuPDF not available - cannot extract PDF text")
            return ""
            
        try:
            import fitz
            doc = fitz.open(pdf_path)
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()
            return text
        except Exception as e:
            self.logger.error(f"PDF extraction failed: {e}")
            return ""
    
    def extract_docx_text(self, docx_path):
        """Extract text from DOCX."""
        if not self.has_docx:
            self.logger.warning("python-docx not available - cannot extract DOCX text")
            return ""
            
        try:
            from docx import Document
            doc = Document(docx_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except Exception as e:
            self.logger.error(f"DOCX extraction failed: {e}")
            return ""
    
    def extract_text(self, file_path, output_dir):
        """Extract text from any supported file, using GPU acceleration when available."""
        file_path = Path(file_path)
        output_dir = Path(output_dir)
        output_dir.mkdir(exist_ok=True)
        
        filename = file_path.name
        output_file = output_dir / f"{file_path.stem}.txt"
        
        text = ""
        file_type = file_path.suffix.lower()
        extraction_method = "none"
        
        # Try GPU extraction first if available
        if self.gpu_extractor:
            try:
                text, gpu_method = self.gpu_extractor.extract_from_file(file_path)
                if text and gpu_method not in ['error', 'unsupported']:
                    extraction_method = gpu_method
                    self.logger.info(f"✅ GPU extraction successful ({gpu_method}): {filename}")
                elif gpu_method == 'error':
                    self.logger.warning(f"⚠️ GPU extraction failed for {filename}, trying fallback methods")
                elif gpu_method == 'unsupported':
                    self.logger.info(f"📄 GPU extraction doesn't support {file_type}, using standard methods")
            except Exception as e:
                self.logger.warning(f"⚠️ GPU extraction error for {filename}: {e}")
        
        # Standard extraction methods as fallback
        if not text:
            if file_type == '.pdf':
                text = self.extract_pdf_text(file_path)
                extraction_method = "pymupdf" if text else "failed"
            elif file_type == '.docx':
                text = self.extract_docx_text(file_path)
                extraction_method = "python-docx" if text else "failed"
            elif file_type in ['.png', '.jpg', '.jpeg', '.tiff', '.bmp']:
                if self.gpu_extractor:
                    # Already tried GPU extraction above
                    self.logger.warning(f"⚠️ OCR failed for image: {filename}")
                else:
                    self.logger.warning(f"📷 Image file detected but no OCR available: {filename}")
                extraction_method = "ocr_not_available"
            else:
                self.logger.warning(f"Unsupported file type: {file_type}")
        
        if text:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(text)
            
            metadata = {
                'filename': filename,
                'file_type': file_type,
                'character_count': len(text),
                'extraction_method': extraction_method
            }
            
            return True, str(output_file), metadata
        
        return False, "", {}

class SimpleIndexer:
    """Simple database indexer using SQLite FTS."""
    
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()
    
    def _create_tables(self):
        """Create database tables."""
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS document_metadata (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                document_id TEXT NOT NULL,
                source_url TEXT,
                organization TEXT,
                category TEXT,
                file_type TEXT,
                character_count INTEGER,
                extraction_method TEXT,
                indexed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                -- OpenAI enhanced fields
                ai_summary TEXT,
                document_type TEXT,
                subject_area TEXT,
                key_topics TEXT,
                date_references TEXT,
                ai_enhanced BOOLEAN DEFAULT 0
            )
        ''')
        
        self.conn.execute('''
            CREATE VIRTUAL TABLE IF NOT EXISTS document_fts USING fts5(
                filename,
                document_id,
                content,
                content=''
            )
        ''')
        
        self.conn.commit()
    
    def add_document(self, filename, document_id, content, **metadata):
        """Add document to index."""
        # Convert key_topics list to JSON string if present
        key_topics_json = ''
        if metadata.get('key_topics'):
            import json
            key_topics_json = json.dumps(metadata['key_topics'])
        
        # Insert metadata
        cursor = self.conn.execute('''
            INSERT INTO document_metadata (
                filename, document_id, source_url, organization, 
                category, file_type, character_count, extraction_method,
                ai_summary, document_type, subject_area, key_topics, 
                date_references, ai_enhanced
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            filename,
            document_id,
            metadata.get('source_url', ''),
            metadata.get('organization', ''),
            metadata.get('category', ''),
            metadata.get('file_type', ''),
            metadata.get('character_count', 0),
            metadata.get('extraction_method', ''),
            metadata.get('ai_summary', ''),
            metadata.get('document_type', ''),
            metadata.get('subject_area', ''),
            key_topics_json,
            metadata.get('date_references', ''),
            1 if metadata.get('ai_enhanced') else 0
        ))
        
        doc_pk = cursor.lastrowid
        
        # Insert into FTS
        self.conn.execute('''
            INSERT INTO document_fts (rowid, filename, document_id, content)
            VALUES (?, ?, ?, ?)
        ''', (doc_pk, filename, document_id, content))
        
        self.conn.commit()
    
    def search_documents(self, query, limit=20):
        """Search documents."""
        cursor = self.conn.execute('''
            SELECT m.*, 
                   snippet(document_fts, 2, '<mark>', '</mark>', '...', 32) as snippet,
                   bm25(document_fts) as rank
            FROM document_fts 
            JOIN document_metadata m ON document_fts.rowid = m.id
            WHERE document_fts MATCH ?
            ORDER BY rank
            LIMIT ?
        ''', (query, limit))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'filename': row['filename'],
                'document_id': row['document_id'],
                'organization': row['organization'],
                'category': row['category'],
                'snippet': row['snippet'],
                'rank': row['rank']
            })
        
        return results
    
    def close(self):
        """Close database connection."""
        self.conn.close()

class LocalProcessorLite:
    """Simplified local processor that works with minimal dependencies."""
    
    def __init__(self, workspace_dir="workspace", use_gpu=False):
        self.workspace = Path(workspace_dir)
        self.workspace.mkdir(exist_ok=True)
        self.use_gpu = use_gpu
        
        # Setup directories
        self.downloads_dir = self.workspace / "downloads"
        self.text_dir = self.workspace / "text"
        self.output_dir = self.workspace / "output"
        self.logs_dir = self.workspace / "logs"
        
        for directory in [self.downloads_dir, self.text_dir, self.output_dir, self.logs_dir]:
            directory.mkdir(exist_ok=True)
        
        # Initialize OpenAI analyzer if available
        self.openai_analyzer = None
        if HAS_OPENAI:
            try:
                self.openai_analyzer = OpenAIDocumentAnalyzer()
                if self.openai_analyzer.is_available():
                    safe_print("🤖 OpenAI document analysis enabled")
                else:
                    safe_print("⚠️ OpenAI API key not configured - using standard processing")
                    self.openai_analyzer = None
            except Exception as e:
                safe_print(f"⚠️ OpenAI initialization failed: {e}")
                self.openai_analyzer = None
        else:
            safe_print("💡 OpenAI not available - install with: pip install openai")
        
        # Setup logging with emoji handling for Windows console
        class SafeFormatter(logging.Formatter):
            def format(self, record):
                # Apply emoji replacement to log messages on Windows
                if os.name == 'nt':
                    record.msg = str(record.msg).replace('🚀', '[GPU]').replace('✅', '[OK]').replace('❌', '[ERROR]').replace('⚠️', '[WARNING]').replace('🔧', '[TOOL]').replace('💡', '[TIP]').replace('📄', '[DOCS]').replace('📊', '[DATA]').replace('📁', '[FILES]').replace('🗂️', '[FOLDER]').replace('📋', '[LIST]').replace('📦', '[DEPS]').replace('🔥', '[PROCESS]').replace('💾', '[DB]').replace('🎉', '[COMPLETE]').replace('🔍', '[SEARCH]').replace('📎', '[LINK]').replace('📥', '[DOWNLOAD]').replace('📝', '[EXTRACT]').replace('📈', '[COUNT]').replace('👤', '[USER]')
                return super().format(record)
        
        formatter = SafeFormatter('%(asctime)s - %(levelname)s - %(message)s')
        
        # File handler with UTF-8 encoding
        file_handler = logging.FileHandler(self.logs_dir / 'processor.log', encoding='utf-8')
        file_handler.setFormatter(formatter)
        
        # Console handler with safe formatter
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        
        logging.basicConfig(
            level=logging.INFO,
            handlers=[file_handler, console_handler]
        )
        self.logger = logging.getLogger(__name__)
        
        safe_print(f"📁 Workspace: {self.workspace.absolute()}")
        safe_print(f"📦 Dependencies: pandas={HAS_PANDAS}, requests={HAS_REQUESTS}")
    
    def process_customer_batch(self, csv_file, customer_name, project_name):
        """Process a complete customer batch from CSV to searchable database."""
        
        safe_print(f"\n🔥 Processing batch for {customer_name}")
        safe_print(f"📊 Project: {project_name}")
        safe_print(f"📄 CSV: {csv_file}")
        print("=" * 60)
        
        # Validate CSV
        try:
            if HAS_PANDAS:
                df = pd.read_csv(csv_file)
                
                # Check for URL column (flexible naming)
                url_column = None
                for col in df.columns:
                    if col.lower() in ['url', 'attachment files', 'attachment_files', 'attachments']:
                        url_column = col
                        break
                
                if url_column is None:
                    safe_print("❌ CSV must have a URL/Attachment column (URL, Attachment Files, etc.)")
                    return None
                
                safe_print(f"📎 Using '{url_column}' column for document URLs")
                
                # Check if Document ID column exists
                has_doc_id = 'Document ID' in df.columns
                if has_doc_id:
                    safe_print("📋 Found 'Document ID' column")
                else:
                    safe_print("📋 No 'Document ID' column - will auto-generate from URLs")
                total_docs = len(df)
            else:
                # Basic validation without pandas
                with open(csv_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    headers = reader.fieldnames
                    
                    url_column = None
                    for col in headers:
                        if col.lower() in ['url', 'attachment files', 'attachment_files', 'attachments']:
                            url_column = col
                            break
                    
                    if url_column is None:
                        safe_print("❌ CSV must have a URL/Attachment column")
                        return None
                    
                    safe_print(f"📎 Using '{url_column}' column for document URLs")
                    
                    # Check if Document ID column exists
                    has_doc_id = 'Document ID' in headers
                    if has_doc_id:
                        safe_print("📋 Found 'Document ID' column")
                    else:
                        safe_print("📋 No 'Document ID' column - will auto-generate from URLs")
                    
                    total_docs = sum(1 for _ in reader)
            
            safe_print(f"📈 Found {total_docs} documents to process")
            
        except Exception as e:
            safe_print(f"❌ CSV Error: {e}")
            return None
        
        # Create customer-specific directories
        customer_id = customer_name.lower().replace(" ", "_")
        project_id = f"{customer_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        project_dir = self.workspace / "customers" / customer_id / project_id
        project_downloads = project_dir / "downloads"
        project_text = project_dir / "text"
        project_output = project_dir / "output"
        
        for directory in [project_dir, project_downloads, project_text, project_output]:
            directory.mkdir(parents=True, exist_ok=True)
        
        safe_print(f"📁 Project directory: {project_dir}")
        
        # Step 1: Download documents (if requests available)
        download_results = {'successful': 0, 'failed': 0}
        if HAS_REQUESTS:
            safe_print("\n📥 Step 1: Downloading documents...")
            downloader = SimpleDownloader(
                downloads_dir=str(project_downloads),
                logs_dir=str(self.logs_dir)
            )
            
            download_results = downloader.download_from_csv(csv_file)
            safe_print(f"✅ Downloaded: {download_results['successful']}/{total_docs}")
            
            if download_results['failed'] > 0:
                safe_print(f"⚠️ Failed: {download_results['failed']} documents")
        else:
            safe_print("\n⚠️ Step 1: Skipping downloads (requests not available)")
            print("   Place PDF files manually in:", project_downloads)
        
        # Step 2: Extract text
        safe_print("\n📝 Step 2: Extracting text...")
        extractor = SimpleTextExtractor(use_gpu=self.use_gpu)
        extracted_files = []
        
        for file_path in project_downloads.glob('*'):
            if file_path.is_file() and file_path.suffix.lower() in ['.pdf', '.docx']:
                success, output_path, metadata = extractor.extract_text(
                    str(file_path), 
                    str(project_text)
                )
                if success:
                    extracted_files.append({
                        'input_file': str(file_path),
                        'output_file': output_path,
                        'metadata': metadata
                    })
        
        safe_print(f"✅ Extracted: {len(extracted_files)} documents")
        
        # Step 3: Build searchable database
        safe_print("\n🔍 Step 3: Building search database...")
        db_path = project_output / f"{project_id}.db"
        indexer = SimpleIndexer(str(db_path))
        
        # Create metadata map from CSV
        metadata_map = {}
        if HAS_PANDAS:
            df = pd.read_csv(csv_file)
            
            # Find URL column
            url_column = 'URL'
            for col in df.columns:
                if col.lower() in ['url', 'attachment files', 'attachment_files', 'attachments']:
                    url_column = col
                    break
            
            for idx, row in df.iterrows():
                doc_id = str(row.get('Document ID', ''))
                urls_field = str(row.get(url_column, ''))
                
                # Auto-generate Document ID if missing (same logic as download)
                if not doc_id or doc_id == 'nan' or doc_id == '':
                    if urls_field and urls_field != 'nan':
                        # Extract from URL pattern (e.g., CMS-2025-0028-0002 from URL)
                        import re
                        url_match = re.search(r'([A-Z0-9-]+(?:-\d+){3,})', urls_field)
                        if url_match:
                            doc_id = url_match.group(1)
                        else:
                            # Fallback: use row index
                            doc_id = f"DOC-{idx+1:04d}"
                
                metadata_map[doc_id] = {
                    'source_url': row.get(url_column, ''),
                    'organization': row.get('Organization Name', row.get('Organization', '')),
                    'category': row.get('Category', ''),
                    'comment': row.get('Comment', ''),
                    'submitter': row.get('Submitter Representative', ''),
                }
        else:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                headers = reader.fieldnames
                
                # Find URL column
                url_column = 'URL'
                for col in headers:
                    if col.lower() in ['url', 'attachment files', 'attachment_files', 'attachments']:
                        url_column = col
                        break
                
                for idx, row in enumerate(reader):
                    doc_id = row.get('Document ID', '')
                    urls_field = row.get(url_column, '')
                    
                    # Auto-generate Document ID if missing (same logic as download)
                    if not doc_id:
                        if urls_field:
                            # Extract from URL pattern (e.g., CMS-2025-0028-0002 from URL)
                            import re
                            url_match = re.search(r'([A-Z0-9-]+(?:-\d+){3,})', urls_field)
                            if url_match:
                                doc_id = url_match.group(1)
                            else:
                                # Fallback: use row index
                                doc_id = f"DOC-{idx+1:04d}"
                    
                    metadata_map[doc_id] = {
                        'source_url': row.get(url_column, ''),
                        'organization': row.get('Organization Name', row.get('Organization', '')),
                        'category': row.get('Category', ''),
                        'comment': row.get('Comment', ''),
                        'submitter': row.get('Submitter Representative', ''),
                    }
        
        # Index all documents with OpenAI enhancement
        indexed_count = 0
        for item in extracted_files:
            if os.path.exists(item['output_file']):
                with open(item['output_file'], 'r', encoding='utf-8') as f:
                    content = f.read()
                
                filename = os.path.basename(item['input_file'])
                doc_id = os.path.splitext(filename)[0]
                doc_metadata = metadata_map.get(doc_id, {})
                
                # Prepare basic document data
                document_data = {
                    'filename': filename,
                    'document_id': doc_id,
                    'content': content,
                    'source_url': doc_metadata.get('source_url', ''),
                    'organization': doc_metadata.get('organization', ''),
                    'category': doc_metadata.get('category', ''),
                    'file_type': item['metadata'].get('file_type', ''),
                    'character_count': item['metadata'].get('character_count', 0),
                    'extraction_method': item['metadata'].get('extraction_method', '')
                }
                
                # Enhance with OpenAI if available
                if self.openai_analyzer:
                    try:
                        safe_print(f"🤖 Analyzing '{filename}' with OpenAI...")
                        enhanced_data = self.openai_analyzer.enhance_document_data(content, document_data)
                        # Use enhanced title as filename for better display
                        if enhanced_data.get('title'):
                            enhanced_data['filename'] = enhanced_data['title']
                            safe_print(f"✨ Enhanced title: '{enhanced_data['title']}'")
                        if enhanced_data.get('ai_summary'):
                            safe_print(f"📄 Summary: {enhanced_data['ai_summary'][:100]}...")
                        if enhanced_data.get('document_type'):
                            safe_print(f"📋 Type: {enhanced_data['document_type']}")
                        document_data = enhanced_data
                    except Exception as e:
                        safe_print(f"⚠️ OpenAI enhancement failed for {filename}: {e}")
                else:
                    safe_print(f"📄 Processing '{filename}' (standard mode)")
                
                # Add document to index with enhanced metadata
                safe_print(f"💾 Indexing document: {doc_id}")
                indexer.add_document(
                    filename=document_data.get('filename', filename),
                    document_id=doc_id,
                    content=content,
                    source_url=document_data.get('source_url', ''),
                    organization=document_data.get('organization', ''),
                    category=document_data.get('category', ''),
                    file_type=document_data.get('file_type', ''),
                    character_count=document_data.get('character_count', 0),
                    extraction_method=document_data.get('extraction_method', ''),
                    # Add OpenAI enhanced fields if available
                    **{k: v for k, v in document_data.items() 
                       if k.startswith('ai_') or k in ['document_type', 'subject_area', 'key_topics']}
                )
                indexed_count += 1
                safe_print(f"✅ Indexed: {indexed_count}/{len(extracted_files)}")
        
        indexer.close()
        safe_print(f"✅ Indexed: {indexed_count} documents")
        
        # Step 4: Create summary
        summary = {
            'customer_name': customer_name,
            'project_name': project_name,
            'project_id': project_id,
            'processed_date': datetime.now().isoformat(),
            'total_documents': total_docs,
            'downloaded_documents': download_results['successful'],
            'extracted_documents': len(extracted_files),
            'indexed_documents': indexed_count,
            'database_path': str(db_path),
            'project_directory': str(project_dir)
        }
        
        summary_path = project_output / 'summary.json'
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2)
        
        print("\n" + "=" * 60)
        safe_print(f"🎉 Processing Complete!")
        safe_print(f"📊 Summary: {indexed_count}/{total_docs} documents processed")
        safe_print(f"💾 Database: {db_path}")
        safe_print(f"📋 Summary: {summary_path}")
        safe_print(f"📁 All files: {project_dir}")
        
        return {
            'success': True,
            'database_path': str(db_path),
            'summary': summary,
            'project_directory': str(project_dir)
        }
    
    def list_customer_projects(self):
        """List all processed customer projects."""
        customers_dir = self.workspace / "customers"
        
        if not customers_dir.exists():
            print("📭 No customer projects found")
            return
        
        safe_print("\n📋 Customer Projects:")
        print("=" * 60)
        
        for customer_dir in customers_dir.iterdir():
            if customer_dir.is_dir():
                customer_name = customer_dir.name.replace("_", " ").title()
                safe_print(f"\n👤 {customer_name}")
                
                for project_dir in customer_dir.iterdir():
                    if project_dir.is_dir():
                        summary_file = project_dir / "output" / "summary.json"
                        if summary_file.exists():
                            try:
                                with open(summary_file, 'r') as f:
                                    summary = json.load(f)
                                
                                safe_print(f"  📊 {summary['project_name']}")
                                print(f"      Date: {summary['processed_date'][:10]}")
                                print(f"      Documents: {summary['indexed_documents']}")
                                print(f"      Database: {summary['database_path']}")
                            except:
                                safe_print(f"  📁 {project_dir.name}")
    
    def test_search(self, database_path, query):
        """Test search functionality on a database."""
        if not os.path.exists(database_path):
            safe_print(f"❌ Database not found: {database_path}")
            return
        
        safe_print(f"\n🔍 Testing search: '{query}'")
        safe_print(f"💾 Database: {database_path}")
        
        try:
            indexer = SimpleIndexer(database_path)
            results = indexer.search_documents(query, limit=5)
            
            if results:
                safe_print(f"\n✅ Found {len(results)} results:")
                for i, result in enumerate(results, 1):
                    print(f"\n{i}. {result.get('filename', 'Unknown')}")
                    if result.get('organization'):
                        print(f"   Organization: {result['organization']}")
                    if result.get('snippet'):
                        print(f"   Snippet: {result['snippet'][:200]}...")
            else:
                print("📭 No results found")
            
            indexer.close()
                
        except Exception as e:
            safe_print(f"❌ Search error: {e}")

def main():
    """Main CLI interface."""
    parser = argparse.ArgumentParser(description="Local Document Processing Tool (Lite)")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Process command
    process_parser = subparsers.add_parser('process', help='Process customer documents')
    process_parser.add_argument('csv_file', help='CSV file with document URLs')
    process_parser.add_argument('--customer', required=True, help='Customer name')
    process_parser.add_argument('--project', required=True, help='Project name')
    process_parser.add_argument('--gpu', action='store_true', help='Enable GPU acceleration for OCR (requires RTX/GTX GPU)')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List customer projects')
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Test search on database')
    search_parser.add_argument('database', help='Path to database file')
    search_parser.add_argument('query', help='Search query')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Initialize processor with GPU option if provided
    use_gpu = hasattr(args, 'gpu') and args.gpu
    if use_gpu:
        safe_print("🚀 GPU acceleration enabled")
    processor = LocalProcessorLite(use_gpu=use_gpu)
    
    if args.command == 'process':
        result = processor.process_customer_batch(
            args.csv_file, 
            args.customer, 
            args.project
        )
        
        if result and result['success']:
            safe_print(f"\n🚀 Next step: Upload {result['database_path']} to customer's online access")
            print(f"   Command: python upload_customer_data.py upload \"{result['database_path']}\" customer@email.com \"Project Name\"")
    
    elif args.command == 'list':
        processor.list_customer_projects()
    
    elif args.command == 'search':
        processor.test_search(args.database, args.query)

if __name__ == "__main__":
    main()
