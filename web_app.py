#!/usr/bin/env python3
"""
Web interface for Public Comment Analysis Tool
Converts the GUI application to a web-based interface for cloud hosting.
"""

import os
import json
import uuid
import tempfile
from pathlib import Path
from datetime import datetime
import threading
import time

from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for, flash
from werkzeug.utils import secure_filename
import pandas as pd

# Import our analysis modules
from downloader import DocumentDownloader
from extractor import extract_document_text, setup_logging as setup_extractor_logging
from indexer import IndexerDB
from grouper import Grouper

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max file size

# Configuration
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'output'
DOWNLOADS_FOLDER = 'downloads'
TEXT_FOLDER = 'text'
LOGS_FOLDER = 'logs'

# Ensure directories exist
for folder in [UPLOAD_FOLDER, OUTPUT_FOLDER, DOWNLOADS_FOLDER, TEXT_FOLDER, LOGS_FOLDER]:
    os.makedirs(folder, exist_ok=True)

# Setup logging
setup_extractor_logging(LOGS_FOLDER)

# Global variables for tracking jobs
active_jobs = {}
job_results = {}

class AnalysisJob:
    """Represents a running analysis job."""
    
    def __init__(self, job_id: str, job_type: str, csv_file: str = None):
        self.job_id = job_id
        self.job_type = job_type
        self.csv_file = csv_file
        self.status = "starting"
        self.progress = 0
        self.message = "Initializing..."
        self.start_time = datetime.now()
        self.results = {}
        self.thread = None
    
    def update_status(self, status: str, progress: int, message: str):
        self.status = status
        self.progress = progress
        self.message = message
    
    def to_dict(self):
        return {
            'job_id': self.job_id,
            'job_type': self.job_type,
            'status': self.status,
            'progress': self.progress,
            'message': self.message,
            'start_time': self.start_time.isoformat(),
            'results': self.results
        }

@app.route('/')
def index():
    """Main page."""
    return render_template('index.html')

@app.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle CSV file upload."""
    if 'csv_file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['csv_file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file and file.filename.lower().endswith('.csv'):
        # Generate unique filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{secure_filename(file.filename)}"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        # Validate CSV format
        try:
            df = pd.read_csv(filepath)
            required_columns = ['Document ID', 'URL']
            
            if not all(col in df.columns for col in required_columns):
                return jsonify({
                    'error': f'CSV must contain columns: {", ".join(required_columns)}',
                    'found_columns': list(df.columns)
                }), 400
            
            return jsonify({
                'success': True,
                'filename': filename,
                'filepath': filepath,
                'document_count': len(df),
                'columns': list(df.columns)
            })
            
        except Exception as e:
            return jsonify({'error': f'Invalid CSV file: {str(e)}'}), 400
    
    return jsonify({'error': 'Please upload a CSV file'}), 400

@app.route('/start_analysis', methods=['POST'])
def start_analysis():
    """Start the full analysis pipeline."""
    data = request.get_json()
    csv_file = data.get('csv_file')
    
    if not csv_file or not os.path.exists(os.path.join(UPLOAD_FOLDER, csv_file)):
        return jsonify({'error': 'CSV file not found'}), 400
    
    # Create new job
    job_id = str(uuid.uuid4())
    job = AnalysisJob(job_id, 'full_analysis', csv_file)
    active_jobs[job_id] = job
    
    # Start analysis in background thread
    job.thread = threading.Thread(target=run_full_analysis, args=(job,))
    job.thread.start()
    
    return jsonify({'job_id': job_id, 'status': 'started'})

@app.route('/job_status/<job_id>')
def job_status(job_id):
    """Get job status."""
    if job_id in active_jobs:
        return jsonify(active_jobs[job_id].to_dict())
    elif job_id in job_results:
        return jsonify(job_results[job_id])
    else:
        return jsonify({'error': 'Job not found'}), 404

@app.route('/download_results/<job_id>')
def download_results(job_id):
    """Download analysis results."""
    if job_id not in job_results:
        return jsonify({'error': 'Results not available'}), 404
    
    results = job_results[job_id]
    if 'output_file' in results:
        return send_file(results['output_file'], as_attachment=True)
    
    return jsonify({'error': 'No output file available'}), 404

@app.route('/search', methods=['GET', 'POST'])
def search():
    """Search interface."""
    if request.method == 'POST':
        query = request.form.get('query', '').strip()
        limit = int(request.form.get('limit', 10))
        
        if not query:
            flash('Please enter a search query')
            return redirect(url_for('search'))
        
        try:
            # Use the most recent database
            db_files = list(Path(OUTPUT_FOLDER).glob('*.db'))
            if not db_files:
                flash('No database found. Please run analysis first.')
                return redirect(url_for('search'))
            
            latest_db = max(db_files, key=lambda x: x.stat().st_mtime)
            
            # Perform search
            indexer = IndexerDB(str(latest_db))
            results = indexer.search_documents(query, limit=limit)
            
            return render_template('search_results.html', 
                                 query=query, 
                                 results=results, 
                                 total=len(results))
        
        except Exception as e:
            flash(f'Search error: {str(e)}')
            return redirect(url_for('search'))
    
    return render_template('search.html')

def run_full_analysis(job: AnalysisJob):
    """Run the complete analysis pipeline."""
    try:
        csv_path = os.path.join(UPLOAD_FOLDER, job.csv_file)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Step 1: Download documents
        job.update_status("downloading", 10, "Downloading documents...")
        
        downloader = DocumentDownloader(
            downloads_dir=DOWNLOADS_FOLDER,
            logs_dir=LOGS_FOLDER
        )
        
        download_results = downloader.download_from_csv(csv_path)
        
        # Step 2: Extract text
        job.update_status("extracting", 30, "Extracting text from documents...")
        
        extracted_files = []
        download_dir = Path(DOWNLOADS_FOLDER)
        
        for file_path in download_dir.glob('*'):
            if file_path.is_file() and file_path.suffix.lower() in ['.pdf', '.docx']:
                success, output_path, metadata = extract_document_text(
                    str(file_path), 
                    TEXT_FOLDER
                )
                if success:
                    extracted_files.append({
                        'input_file': str(file_path),
                        'output_file': output_path,
                        'metadata': metadata
                    })
        
        # Step 3: Build search index
        job.update_status("indexing", 60, "Building search index...")
        
        db_path = os.path.join(OUTPUT_FOLDER, f'documents_{timestamp}.db')
        indexer = IndexerDB(db_path)
        
        for item in extracted_files:
            if os.path.exists(item['output_file']):
                with open(item['output_file'], 'r', encoding='utf-8') as f:
                    content = f.read()
                
                indexer.add_document(
                    filename=os.path.basename(item['input_file']),
                    document_id=os.path.splitext(os.path.basename(item['input_file']))[0],
                    content=content,
                    source_url='',  # TODO: get from CSV
                    organization='',
                    category='',
                    file_type=item['metadata'].get('file_type', ''),
                    character_count=item['metadata'].get('character_count', 0),
                    extraction_method=item['metadata'].get('extraction_method', '')
                )
        
        # Step 4: Clustering analysis
        job.update_status("clustering", 80, "Performing clustering analysis...")
        
        grouper = Grouper()
        
        # Get all text files for clustering
        text_files = list(Path(TEXT_FOLDER).glob('*.txt'))
        
        if text_files:
            # Prepare data for clustering
            documents = []
            filenames = []
            
            for text_file in text_files:
                try:
                    with open(text_file, 'r', encoding='utf-8') as f:
                        content = f.read().strip()
                        if content:
                            documents.append(content)
                            filenames.append(text_file.stem)
                except Exception as e:
                    continue
            
            if documents:
                # Run clustering
                clustering_results = grouper.cluster_documents(
                    documents, 
                    filenames,
                    method='tfidf'  # Start with fastest method
                )
                
                # Save clustering results
                results_path = os.path.join(OUTPUT_FOLDER, f'clustering_results_{timestamp}.json')
                with open(results_path, 'w', encoding='utf-8') as f:
                    json.dump(clustering_results, f, indent=2, ensure_ascii=False)
        
        # Step 5: Generate summary report
        job.update_status("finalizing", 95, "Generating summary report...")
        
        summary = {
            'analysis_date': datetime.now().isoformat(),
            'total_documents': len(extracted_files),
            'successful_extractions': len([x for x in extracted_files if x['metadata']['success']]),
            'database_path': db_path,
            'text_files_processed': len(text_files) if text_files else 0
        }
        
        summary_path = os.path.join(OUTPUT_FOLDER, f'analysis_summary_{timestamp}.json')
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2)
        
        # Complete job
        job.update_status("completed", 100, "Analysis completed successfully!")
        job.results = {
            'summary': summary,
            'database_path': db_path,
            'summary_file': summary_path,
            'output_folder': OUTPUT_FOLDER
        }
        
        # Move to completed jobs
        job_results[job.job_id] = job.to_dict()
        del active_jobs[job.job_id]
        
    except Exception as e:
        job.update_status("failed", 0, f"Analysis failed: {str(e)}")
        job_results[job.job_id] = job.to_dict()
        if job.job_id in active_jobs:
            del active_jobs[job.job_id]

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)