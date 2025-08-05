#!/usr/bin/env python3
"""
Vercel-optimized version of the Public Comment Analysis Tool
Adapted for serverless deployment on Vercel.
"""

import os
import json
import uuid
import tempfile
from pathlib import Path
from datetime import datetime
import threading
import time
from urllib.parse import urlparse

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from werkzeug.utils import secure_filename
import pandas as pd
import requests

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'vercel-secret-key-change-in-production')

# Vercel-specific configuration
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB for Vercel
app.config['UPLOAD_FOLDER'] = '/tmp/uploads'
app.config['OUTPUT_FOLDER'] = '/tmp/output'

# Ensure temp directories exist (Vercel provides /tmp)
os.makedirs('/tmp/uploads', exist_ok=True)
os.makedirs('/tmp/output', exist_ok=True)
os.makedirs('/tmp/downloads', exist_ok=True)
os.makedirs('/tmp/text', exist_ok=True)

# Simple in-memory job storage (for demo - use Redis/DB for production)
jobs = {}

@app.route('/')
def index():
    """Main page with Vercel-specific messaging."""
    return render_template('vercel_index.html')

@app.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy', 
        'platform': 'vercel',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle CSV file upload with Vercel limits."""
    if 'csv_file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['csv_file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file and file.filename.lower().endswith('.csv'):
        # Check file size (Vercel has limits)
        file.seek(0, 2)  # Seek to end
        size = file.tell()
        file.seek(0)  # Reset to beginning
        
        if size > 10 * 1024 * 1024:  # 10MB limit for CSV
            return jsonify({'error': 'CSV file too large (max 10MB for Vercel)'}), 400
        
        # Generate unique filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{secure_filename(file.filename)}"
        filepath = os.path.join('/tmp/uploads', filename)
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
            
            # Limit document count for Vercel
            if len(df) > 100:
                return jsonify({
                    'error': 'Too many documents (max 100 for Vercel demo). Use Railway/DigitalOcean for larger batches.',
                    'document_count': len(df)
                }), 400
            
            return jsonify({
                'success': True,
                'filename': filename,
                'filepath': filepath,
                'document_count': len(df),
                'columns': list(df.columns),
                'platform_note': 'Vercel demo limited to 100 documents'
            })
            
        except Exception as e:
            return jsonify({'error': f'Invalid CSV file: {str(e)}'}), 400
    
    return jsonify({'error': 'Please upload a CSV file'}), 400

@app.route('/quick_analysis', methods=['POST'])
def quick_analysis():
    """Quick analysis for Vercel demo (limited processing)."""
    data = request.get_json()
    csv_file = data.get('csv_file')
    
    if not csv_file or not os.path.exists(os.path.join('/tmp/uploads', csv_file)):
        return jsonify({'error': 'CSV file not found'}), 400
    
    try:
        # Read CSV
        csv_path = os.path.join('/tmp/uploads', csv_file)
        df = pd.read_csv(csv_path)
        
        # Limit to first 10 documents for demo
        df = df.head(10)
        
        results = []
        
        # Process each URL (download small files only)
        for idx, row in df.iterrows():
            doc_id = row['Document ID']
            url = row['URL']
            
            try:
                # Quick download attempt (small files only)
                response = requests.head(url, timeout=5)
                content_length = response.headers.get('content-length')
                
                if content_length and int(content_length) > 5 * 1024 * 1024:  # 5MB limit
                    results.append({
                        'document_id': doc_id,
                        'url': url,
                        'status': 'skipped',
                        'reason': 'File too large for Vercel demo',
                        'size': content_length
                    })
                    continue
                
                # Quick text extraction attempt
                if url.lower().endswith('.pdf'):
                    results.append({
                        'document_id': doc_id,
                        'url': url,
                        'status': 'detected',
                        'type': 'PDF',
                        'note': 'Use full cloud deployment for PDF processing'
                    })
                elif url.lower().endswith('.docx'):
                    results.append({
                        'document_id': doc_id,
                        'url': url,
                        'status': 'detected',
                        'type': 'DOCX',
                        'note': 'Use full cloud deployment for DOCX processing'
                    })
                else:
                    results.append({
                        'document_id': doc_id,
                        'url': url,
                        'status': 'detected',
                        'type': 'Unknown',
                        'note': 'File type detected, use full deployment for processing'
                    })
                    
            except Exception as e:
                results.append({
                    'document_id': doc_id,
                    'url': url,
                    'status': 'error',
                    'error': str(e)
                })
        
        # Create job result
        job_id = str(uuid.uuid4())
        jobs[job_id] = {
            'status': 'completed',
            'results': results,
            'total_documents': len(df),
            'processed_documents': len(results),
            'timestamp': datetime.now().isoformat(),
            'platform': 'vercel_demo'
        }
        
        return jsonify({
            'job_id': job_id,
            'status': 'completed',
            'message': 'Quick analysis completed',
            'results': results
        })
        
    except Exception as e:
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500

@app.route('/job_status/<job_id>')
def job_status(job_id):
    """Get job status."""
    if job_id in jobs:
        return jsonify(jobs[job_id])
    else:
        return jsonify({'error': 'Job not found'}), 404

@app.route('/deployment_guide')
def deployment_guide():
    """Show deployment guide for full functionality."""
    return render_template('deployment_guide.html')

# Vercel serverless function handler
def handler(request):
    """Vercel serverless function handler."""
    return app(request.environ, lambda *args: None)

if __name__ == '__main__':
    app.run(debug=True)