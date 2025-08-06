#!/usr/bin/env python3
"""
Customer Data Portal
Simple web interface for customers to access their processed document data.
You upload the databases, customers log in to search and browse.
"""

import os
import secrets
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from functools import wraps
import logging

from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash, send_file
from werkzeug.security import generate_password_hash, check_password_hash
import pandas as pd

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(32))
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)

# Security configurations
app.config['SESSION_COOKIE_SECURE'] = True  # Require HTTPS for cookies
app.config['SESSION_COOKIE_HTTPONLY'] = True  # Prevent XSS
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # CSRF protection

# Portal directories
PORTAL_DATA_DIR = Path('portal_data')
CUSTOMER_DATABASES_DIR = PORTAL_DATA_DIR / 'databases'
ADMIN_DATA_DIR = PORTAL_DATA_DIR / 'admin'

# Ensure directories exist
for directory in [PORTAL_DATA_DIR, CUSTOMER_DATABASES_DIR, ADMIN_DATA_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_portal_db():
    """Initialize simple customer database."""
    db_path = ADMIN_DATA_DIR / 'customers.db'
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Simple customers table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            id TEXT PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            name TEXT NOT NULL,
            organization TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP,
            is_active BOOLEAN DEFAULT 1
        )
    ''')
    
    # Customer projects/databases table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS customer_databases (
            id TEXT PRIMARY KEY,
            customer_id TEXT NOT NULL,
            project_name TEXT NOT NULL,
            database_filename TEXT NOT NULL,
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            document_count INTEGER DEFAULT 0,
            description TEXT,
            FOREIGN KEY (customer_id) REFERENCES customers (id)
        )
    ''')
    
    conn.commit()
    conn.close()

def login_required(f):
    """Decorator to require customer login."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'customer_id' not in session:
            flash('Please log in to access your data.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def get_customer_by_email(email):
    """Get customer by email address."""
    db_path = ADMIN_DATA_DIR / 'customers.db'
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM customers WHERE email = ? AND is_active = 1', (email,))
    customer = cursor.fetchone()
    conn.close()
    return dict(customer) if customer else None

def get_customer_databases(customer_id):
    """Get all databases for a customer."""
    db_path = ADMIN_DATA_DIR / 'customers.db'
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM customer_databases 
        WHERE customer_id = ? 
        ORDER BY uploaded_at DESC
    ''', (customer_id,))
    
    databases = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return databases

@app.route('/')
def index():
    """Landing page."""
    if 'customer_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('portal_index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Customer login."""
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        
        if not email or not password:
            flash('Please enter both email and password.', 'error')
            return render_template('portal_login.html')
        
        customer = get_customer_by_email(email)
        if customer and check_password_hash(customer['password_hash'], password):
            session.permanent = True
            session['customer_id'] = customer['id']
            session['customer_email'] = customer['email']
            session['customer_name'] = customer['name']
            
            # Update last login
            db_path = ADMIN_DATA_DIR / 'customers.db'
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute('UPDATE customers SET last_login = CURRENT_TIMESTAMP WHERE id = ?', (customer['id'],))
            conn.commit()
            conn.close()
            
            flash(f'Welcome back, {customer["name"]}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password.', 'error')
    
    return render_template('portal_login.html')

@app.route('/logout')
def logout():
    """Customer logout."""
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    """Customer dashboard."""
    customer_databases = get_customer_databases(session['customer_id'])
    
    # Calculate stats
    total_projects = len(customer_databases)
    total_documents = sum(db.get('document_count', 0) for db in customer_databases)
    
    stats = {
        'total_projects': total_projects,
        'total_documents': total_documents,
        'latest_upload': customer_databases[0]['uploaded_at'][:10] if customer_databases else 'None'
    }
    
    return render_template('portal_dashboard.html', 
                         databases=customer_databases,
                         stats=stats)

@app.route('/project/<project_id>')
@login_required
def view_project(project_id):
    """View project and search documents."""
    # Get project info
    db_path = ADMIN_DATA_DIR / 'customers.db'
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM customer_databases 
        WHERE id = ? AND customer_id = ?
    ''', (project_id, session['customer_id']))
    
    project = cursor.fetchone()
    conn.close()
    
    if not project:
        flash('Project not found.', 'error')
        return redirect(url_for('dashboard'))
    
    project = dict(project)
    
    # Check if database file exists
    db_file = CUSTOMER_DATABASES_DIR / project['database_filename']
    has_database = db_file.exists()
    
    return render_template('portal_project.html', 
                         project=project,
                         has_database=has_database)

@app.route('/api/search/<project_id>', methods=['POST'])
@login_required
def api_search(project_id):
    """Search documents within a project."""
    # Verify project belongs to customer
    db_path = ADMIN_DATA_DIR / 'customers.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT database_filename FROM customer_databases 
        WHERE id = ? AND customer_id = ?
    ''', (project_id, session['customer_id']))
    
    result = cursor.fetchone()
    conn.close()
    
    if not result:
        return jsonify({'error': 'Project not found'}), 403
    
    database_filename = result[0]
    
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        limit = min(data.get('limit', 20), 100)
        
        if not query:
            return jsonify({'error': 'No search query provided'}), 400
        
        # Search in customer's database
        db_file = CUSTOMER_DATABASES_DIR / database_filename
        
        if not db_file.exists():
            return jsonify({'error': 'Database not found'}), 404
        
        # Simple search using SQLite FTS
        conn = sqlite3.connect(db_file)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Check if FTS table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='document_fts'")
        if not cursor.fetchone():
            return jsonify({'error': 'Search index not available'}), 404
        
        # Search query
        cursor.execute('''
            SELECT m.*, 
                   snippet(document_fts, 2, '<mark>', '</mark>', '...', 32) as snippet,
                   rank
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
                'file_type': row['file_type'],
                'character_count': row['character_count'],
                'snippet': row['snippet'],
                'rank': row['rank']
            })
        
        conn.close()
        
        return jsonify({
            'query': query,
            'total_results': len(results),
            'results': results
        })
        
    except Exception as e:
        logger.error(f"Search error: {e}")
        return jsonify({'error': 'Search failed'}), 500

@app.route('/api/export/<project_id>/<format>')
@login_required
def api_export(project_id, format):
    """Export project data."""
    # Verify project belongs to customer
    db_path = ADMIN_DATA_DIR / 'customers.db'
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT project_name, database_filename FROM customer_databases 
        WHERE id = ? AND customer_id = ?
    ''', (project_id, session['customer_id']))
    
    result = cursor.fetchone()
    conn.close()
    
    if not result:
        flash('Project not found.', 'error')
        return redirect(url_for('dashboard'))
    
    project_name = result['project_name']
    database_filename = result['database_filename']
    
    try:
        db_file = CUSTOMER_DATABASES_DIR / database_filename
        
        if not db_file.exists():
            flash('Database not found.', 'error')
            return redirect(url_for('view_project', project_id=project_id))
        
        if format.lower() == 'csv':
            # Export as CSV
            export_file = PORTAL_DATA_DIR / f"{project_name}_export.csv"
            
            conn = sqlite3.connect(db_file)
            df = pd.read_sql_query('''
                SELECT filename, document_id, source_url, organization, 
                       category, file_type, character_count, extraction_method
                FROM document_metadata
                ORDER BY filename
            ''', conn)
            conn.close()
            
            df.to_csv(export_file, index=False)
            return send_file(export_file, as_attachment=True,
                           download_name=f"{project_name}_metadata.csv")
        
        else:
            flash('Unsupported export format.', 'error')
            return redirect(url_for('view_project', project_id=project_id))
            
    except Exception as e:
        logger.error(f"Export error: {e}")
        flash('Export failed.', 'error')
        return redirect(url_for('view_project', project_id=project_id))

@app.route('/health')
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'customer-portal',
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    # Initialize database
    init_portal_db()
    
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '127.0.0.1')
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    logger.info(f"Starting Customer Portal on {host}:{port}")
    app.run(host=host, port=port, debug=debug)

