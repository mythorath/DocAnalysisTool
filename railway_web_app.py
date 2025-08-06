#!/usr/bin/env python3
"""
Railway-optimized web application for Document Analysis Tool
Lightweight version designed to fit within 4GB Railway free tier limit
"""

import os
import sys
import logging
from pathlib import Path
from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
import tempfile
import shutil

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'railway-comment-analyzer-2024')

# Create necessary directories
for dir_name in ['downloads', 'text', 'output', 'logs']:
    Path(dir_name).mkdir(exist_ok=True)

@app.route('/')
def index():
    """Main page with upload and processing options."""
    return render_template('railway_index.html')

@app.route('/process', methods=['POST'])
def process_documents():
    """Process uploaded CSV file with document URLs."""
    try:
        if 'csv_file' not in request.files:
            flash('No CSV file uploaded', 'error')
            return redirect(url_for('index'))
        
        file = request.files['csv_file']
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(url_for('index'))
        
        if not file.filename.endswith('.csv'):
            flash('Please upload a CSV file', 'error')
            return redirect(url_for('index'))
        
        # Save uploaded file
        csv_path = Path('input') / 'uploaded_links.csv'
        file.save(csv_path)
        
        # Process the documents
        try:
            # Import here to avoid startup delays
            from downloader import download_documents
            from extractor import extract_all_text
            from indexer import build_search_index
            
            # Download documents
            logger.info("Starting document download...")
            download_documents(str(csv_path), 'downloads', 'logs')
            
            # Extract text
            logger.info("Starting text extraction...")
            extract_all_text('downloads', 'text', 'logs')
            
            # Build search index
            logger.info("Building search index...")
            build_search_index('text', 'output/document_index.db', str(csv_path))
            
            flash('Documents processed successfully! You can now search them.', 'success')
            return redirect(url_for('search'))
            
        except Exception as e:
            logger.error(f"Processing error: {str(e)}")
            flash(f'Error processing documents: {str(e)}', 'error')
            return redirect(url_for('index'))
            
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        flash(f'Error uploading file: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/search')
def search():
    """Search page."""
    return render_template('railway_search.html')

@app.route('/api/search', methods=['POST'])
def api_search():
    """API endpoint for searching documents."""
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        limit = data.get('limit', 10)
        
        if not query:
            return jsonify({'error': 'No search query provided'}), 400
        
        # Import here to avoid startup delays
        from indexer import search_documents
        
        # Check if index exists
        index_path = Path('output/document_index.db')
        if not index_path.exists():
            return jsonify({
                'error': 'No documents indexed yet. Please upload and process documents first.',
                'results': []
            }), 404
        
        # Perform search
        results = search_documents(str(index_path), query, limit)
        
        return jsonify({
            'query': query,
            'total_results': len(results),
            'results': results
        })
        
    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        return jsonify({'error': f'Search failed: {str(e)}'}), 500

@app.route('/api/status')
def api_status():
    """API endpoint to check system status."""
    try:
        # Check if documents exist
        downloads_path = Path('downloads')
        text_path = Path('text')
        index_path = Path('output/document_index.db')
        
        download_count = len([f for f in downloads_path.glob('*') if f.is_file() and f.name != '.gitkeep'])
        text_count = len([f for f in text_path.glob('*') if f.is_file() and f.name != '.gitkeep'])
        index_exists = index_path.exists()
        
        return jsonify({
            'status': 'healthy',
            'documents_downloaded': download_count,
            'documents_processed': text_count,
            'search_index_ready': index_exists,
            'ready_for_search': index_exists and text_count > 0
        })
        
    except Exception as e:
        logger.error(f"Status check error: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/health')
def health_check():
    """Health check endpoint for Railway."""
    return jsonify({'status': 'healthy', 'service': 'comment-analyzer'})

@app.errorhandler(404)
def not_found(error):
    return render_template('error.html', 
                         error_title="Page Not Found",
                         error_message="The page you're looking for doesn't exist."), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('error.html',
                         error_title="Internal Server Error", 
                         error_message="Something went wrong. Please try again."), 500

if __name__ == '__main__':
    # Railway provides PORT environment variable
    port = int(os.environ.get('PORT', 5000))
    host = '0.0.0.0'  # Required for Railway
    
    logger.info(f"Starting Railway Comment Analyzer on {host}:{port}")
    app.run(host=host, port=port, debug=False)