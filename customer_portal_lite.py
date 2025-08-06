#!/usr/bin/env python3
"""
Customer Data Portal - Lite Version
Minimal dependencies version that works even if pandas/numpy installation fails.
"""

import os
import secrets
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from functools import wraps
import logging
import json

from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash, send_file
from werkzeug.security import generate_password_hash, check_password_hash

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
            return render_template('enhanced_login.html')
        
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
    
    return render_template('enhanced_login.html')

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
    
    return render_template('enhanced_dashboard.html', 
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
    
    return render_template('enhanced_project.html', 
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
            # Export as CSV using basic Python (no pandas required)
            export_file = PORTAL_DATA_DIR / f"{project_name}_export.csv"
            
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT filename, document_id, source_url, organization, 
                       category, file_type, character_count, extraction_method
                FROM document_metadata
                ORDER BY filename
            ''')
            
            rows = cursor.fetchall()
            conn.close()
            
            # Write CSV manually (no pandas dependency)
            with open(export_file, 'w', encoding='utf-8', newline='') as f:
                # Write header
                f.write('filename,document_id,source_url,organization,category,file_type,character_count,extraction_method\n')
                
                # Write data rows
                for row in rows:
                    # Escape commas and quotes in CSV
                    escaped_row = []
                    for field in row:
                        if field is None:
                            field = ''
                        field_str = str(field)
                        if ',' in field_str or '"' in field_str or '\n' in field_str:
                            field_str = '"' + field_str.replace('"', '""') + '"'
                        escaped_row.append(field_str)
                    f.write(','.join(escaped_row) + '\n')
            
            return send_file(export_file, as_attachment=True,
                           download_name=f"{project_name}_metadata.csv")
        
        else:
            flash('Unsupported export format.', 'error')
            return redirect(url_for('view_project', project_id=project_id))
            
    except Exception as e:
        logger.error(f"Export error: {e}")
        flash('Export failed.', 'error')
        return redirect(url_for('view_project', project_id=project_id))

@app.route('/api/document/<project_id>/<document_id>')
@login_required
def api_get_document(project_id, document_id):
    """Get document content and metadata with optional search highlighting."""
    # Get search query from request args for highlighting
    search_query = request.args.get('q', '').strip()
    
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
        # Get document info from project database
        db_file = CUSTOMER_DATABASES_DIR / database_filename
        
        if not db_file.exists():
            return jsonify({'error': 'Database not found'}), 404
        
        conn = sqlite3.connect(db_file)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get document metadata
        cursor.execute('''
            SELECT * FROM document_metadata 
            WHERE document_id = ?
        ''', (document_id,))
        
        doc_result = cursor.fetchone()
        if not doc_result:
            return jsonify({'error': 'Document not found'}), 404
        
        document = dict(doc_result)
        
        # Get full text content
        cursor.execute('''
            SELECT content FROM document_fts 
            WHERE document_id = ?
        ''', (document_id,))
        
        text_result = cursor.fetchone()
        extracted_text = text_result['content'] if text_result else ""
        
        # Generate highlighted snippets if search query provided
        highlighted_snippets = []
        if search_query and extracted_text:
            highlighted_snippets = generate_highlighted_snippets(extracted_text, search_query)
        
        conn.close()
        
        return jsonify({
            'document': document,
            'extracted_text': extracted_text,
            'highlighted_snippets': highlighted_snippets,
            'search_query': search_query,
            'has_original': bool(document.get('source_url')),
            'file_type': document.get('file_type', '').lower(),
            'extraction_method': document.get('extraction_method', 'unknown'),
            'is_ocr_document': document.get('extraction_method', '').lower() in ['ocr', 'gpu_ocr', 'cpu_ocr', 'tesseract'],
            'character_count': document.get('character_count', 0)
        })
        
    except Exception as e:
        logger.error(f"Document fetch error: {e}")
        return jsonify({'error': 'Failed to fetch document'}), 500

def generate_highlighted_snippets(text, query, snippet_length=200, max_snippets=5):
    """Generate text snippets with highlighted search terms."""
    import re
    
    snippets = []
    if not query or not text:
        return snippets
    
    # Split query into individual terms
    query_terms = [term.strip().lower() for term in query.split() if term.strip()]
    if not query_terms:
        return snippets
    
    # Create regex pattern for all terms (case insensitive)
    pattern = '|'.join(re.escape(term) for term in query_terms)
    
    # Find all matches with their positions
    matches = list(re.finditer(pattern, text, re.IGNORECASE))
    
    if not matches:
        # No matches found, return beginning of document
        snippet_text = text[:snippet_length] + "..." if len(text) > snippet_length else text
        return [{
            'text': snippet_text,
            'highlighted': False,
            'position': 0
        }]
    
    # Group nearby matches to avoid overlapping snippets
    snippet_positions = []
    for match in matches:
        start = max(0, match.start() - snippet_length // 2)
        end = min(len(text), match.end() + snippet_length // 2)
        
        # Check if this overlaps with existing snippets
        overlaps = False
        for existing_start, existing_end in snippet_positions:
            if not (end < existing_start or start > existing_end):
                overlaps = True
                break
        
        if not overlaps:
            snippet_positions.append((start, end))
            if len(snippet_positions) >= max_snippets:
                break
    
    # Generate snippets with highlighting
    for start, end in snippet_positions:
        snippet_text = text[start:end]
        
        # Add ellipsis if not at document boundaries
        prefix = "..." if start > 0 else ""
        suffix = "..." if end < len(text) else ""
        
        # Highlight search terms in this snippet
        highlighted_text = snippet_text
        for term in query_terms:
            highlighted_text = re.sub(
                f'({re.escape(term)})',
                r'<mark class="search-highlight">\1</mark>',
                highlighted_text,
                flags=re.IGNORECASE
            )
        
        snippets.append({
            'text': prefix + highlighted_text + suffix,
            'highlighted': True,
            'position': start,
            'match_count': len(re.findall(pattern, snippet_text, re.IGNORECASE))
        })
    
    # Sort by match count (most relevant first)
    snippets.sort(key=lambda x: x.get('match_count', 0), reverse=True)
    
    return snippets

@app.route('/api/document/<project_id>/<document_id>/original')
@login_required
def api_get_original_document(project_id, document_id):
    """Serve original document file if available."""
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
    
    # Check if original file exists in downloads directory
    # This would need to be implemented based on your file storage strategy
    # For now, redirect to source URL if available
    
    try:
        database_filename = result[0]
        db_file = CUSTOMER_DATABASES_DIR / database_filename
        
        if not db_file.exists():
            return jsonify({'error': 'Database not found'}), 404
        
        conn = sqlite3.connect(db_file)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT source_url FROM document_metadata 
            WHERE document_id = ?
        ''', (document_id,))
        
        doc_result = cursor.fetchone()
        conn.close()
        
        if doc_result and doc_result['source_url']:
            return redirect(doc_result['source_url'])
        else:
            return jsonify({'error': 'Original document not available'}), 404
            
    except Exception as e:
        logger.error(f"Original document fetch error: {e}")
        return jsonify({'error': 'Failed to fetch original document'}), 500

@app.route('/health')
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'customer-portal-lite',
        'timestamp': datetime.now().isoformat()
    })

# Admin API endpoints for remote management
def require_admin_key(f):
    """Decorator to require admin API key for admin endpoints."""
    from functools import wraps
    
    @wraps(f)
    def admin_decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Missing or invalid authorization header'}), 401
        
        provided_key = auth_header.replace('Bearer ', '')
        expected_key = os.environ.get('ADMIN_API_KEY', 'default_admin_key_change_me')
        
        if provided_key != expected_key:
            return jsonify({'error': 'Invalid admin API key'}), 401
        
        return f(*args, **kwargs)
    return admin_decorated_function

@app.route('/admin/health')
@require_admin_key
def admin_health_check():
    """Admin health check with version info."""
    return jsonify({
        'status': 'healthy',
        'service': 'admin-api',
        'version': '2.0.0',
        'timestamp': datetime.now().isoformat(),
        'admin_access': True
    })

@app.route('/admin/customers')
@require_admin_key
def admin_list_customers_endpoint():
    """List all customers with their projects for admin."""
    try:
        db_path = ADMIN_DATA_DIR / 'customers.db'
        if not db_path.exists():
            return jsonify({'customers': [], 'total_customers': 0})
        
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get customers with projects
        cursor.execute('''
            SELECT c.id, c.email, c.name, c.organization, c.created_at,
                   cd.id as project_id, cd.project_name, cd.description, 
                   cd.database_filename, cd.uploaded_at
            FROM customers c
            LEFT JOIN customer_databases cd ON c.id = cd.customer_id
            ORDER BY c.name, cd.uploaded_at DESC
        ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        # Group by customer
        customers_dict = {}
        for row in rows:
            customer_id = row['id']
            if customer_id not in customers_dict:
                customers_dict[customer_id] = {
                    'id': customer_id,
                    'email': row['email'],
                    'name': row['name'],
                    'organization': row['organization'],
                    'created_at': row['created_at'],
                    'projects': []
                }
            
            if row['project_id']:  # Has projects
                # Get database info
                db_file = CUSTOMER_DATABASES_DIR / row['database_filename']
                doc_count = 0
                file_size = 0
                
                if db_file.exists():
                    try:
                        file_size = db_file.stat().st_size
                        conn = sqlite3.connect(db_file)
                        cursor = conn.cursor()
                        cursor.execute("SELECT COUNT(*) FROM document_metadata")
                        doc_count = cursor.fetchone()[0]
                        conn.close()
                    except:
                        pass
                
                customers_dict[customer_id]['projects'].append({
                    'id': row['project_id'],
                    'project_name': row['project_name'],
                    'description': row['description'],
                    'database_filename': row['database_filename'],
                    'uploaded_at': row['uploaded_at'],
                    'document_count': doc_count,
                    'file_size': file_size
                })
        
        return jsonify({
            'customers': list(customers_dict.values()),
            'total_customers': len(customers_dict)
        })
        
    except Exception as e:
        logger.error(f"Admin list customers error: {e}")
        return jsonify({'error': f'Failed to list customers: {str(e)}'}), 500

@app.route('/admin/upload-database', methods=['POST'])
@require_admin_key
def admin_upload_database_endpoint():
    """Upload a database via API."""
    try:
        data = request.get_json()
        
        customer_email = data.get('customer_email')
        project_name = data.get('project_name')
        description = data.get('description', '')
        database_data = data.get('database_data')  # Base64 encoded
        
        if not all([customer_email, project_name, database_data]):
            return jsonify({'error': 'Missing required fields: customer_email, project_name, database_data'}), 400
        
        # Decode database data
        import base64
        try:
            db_content = base64.b64decode(database_data)
        except Exception as e:
            return jsonify({'error': f'Invalid base64 data: {str(e)}'}), 400
        
        # Generate unique filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_name = "".join(c for c in project_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_name = safe_name.replace(' ', '_').lower()
        db_filename = f"{safe_name}_{timestamp}.db"
        
        # Save database file
        db_path = CUSTOMER_DATABASES_DIR / db_filename
        with open(db_path, 'wb') as f:
            f.write(db_content)
        
        # Get customer
        db_admin_path = ADMIN_DATA_DIR / 'customers.db'
        conn = sqlite3.connect(db_admin_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT id FROM customers WHERE email = ?", (customer_email,))
        customer = cursor.fetchone()
        
        if not customer:
            conn.close()
            return jsonify({'error': f'Customer not found: {customer_email}. Create customer first.'}), 404
        
        customer_id = customer[0]
        
        # Insert database record
        database_id = str(uuid.uuid4())
        cursor.execute('''
            INSERT INTO customer_databases 
            (id, customer_id, project_name, description, database_filename, uploaded_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (database_id, customer_id, project_name, description, db_filename, datetime.now()))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Database uploaded via API: {db_filename} for {customer_email}")
        
        return jsonify({
            'success': True,
            'database_id': database_id,
            'database_filename': db_filename,
            'message': 'Database uploaded successfully'
        })
        
    except Exception as e:
        logger.error(f"Admin upload database error: {e}")
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500

@app.route('/admin/remove-project', methods=['DELETE'])
@require_admin_key
def admin_remove_project_endpoint():
    """Remove a project via API."""
    try:
        data = request.get_json()
        customer_email = data.get('customer_email')
        project_name = data.get('project_name')
        
        if not customer_email or not project_name:
            return jsonify({'error': 'Missing customer_email or project_name'}), 400
        
        db_path = ADMIN_DATA_DIR / 'customers.db'
        if not db_path.exists():
            return jsonify({'error': 'No customer database found'}), 404
        
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Find project
        cursor.execute('''
            SELECT cd.*, c.email
            FROM customer_databases cd
            JOIN customers c ON cd.customer_id = c.id
            WHERE c.email = ? AND cd.project_name = ?
        ''', (customer_email, project_name))
        
        project = cursor.fetchone()
        if not project:
            conn.close()
            return jsonify({'error': 'Project not found'}), 404
        
        # Get file size before deletion
        db_file = CUSTOMER_DATABASES_DIR / project['database_filename']
        freed_space = db_file.stat().st_size if db_file.exists() else 0
        
        # Remove database file
        if db_file.exists():
            db_file.unlink()
        
        # Remove database record
        cursor.execute("DELETE FROM customer_databases WHERE id = ?", (project['id'],))
        conn.commit()
        conn.close()
        
        logger.info(f"Project removed via API: {project_name} for {customer_email}")
        
        return jsonify({
            'success': True,
            'freed_space': freed_space,
            'message': 'Project removed successfully'
        })
        
    except Exception as e:
        logger.error(f"Admin remove project error: {e}")
        return jsonify({'error': f'Removal failed: {str(e)}'}), 500

@app.route('/admin/remove-customer', methods=['DELETE'])
@require_admin_key
def admin_remove_customer_endpoint():
    """Remove a customer and all their data via API."""
    try:
        data = request.get_json()
        customer_email = data.get('customer_email')
        
        if not customer_email:
            return jsonify({'error': 'Missing customer_email'}), 400
        
        db_path = ADMIN_DATA_DIR / 'customers.db'
        if not db_path.exists():
            return jsonify({'error': 'No customer database found'}), 404
        
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Find customer and projects
        cursor.execute("SELECT id FROM customers WHERE email = ?", (customer_email,))
        customer = cursor.fetchone()
        
        if not customer:
            conn.close()
            return jsonify({'error': 'Customer not found'}), 404
        
        customer_id = customer['id']
        
        # Get all projects
        cursor.execute("SELECT * FROM customer_databases WHERE customer_id = ?", (customer_id,))
        projects = cursor.fetchall()
        
        # Remove database files and calculate freed space
        freed_space = 0
        for project in projects:
            db_file = CUSTOMER_DATABASES_DIR / project['database_filename']
            if db_file.exists():
                freed_space += db_file.stat().st_size
                db_file.unlink()
        
        # Remove records
        cursor.execute("DELETE FROM customer_databases WHERE customer_id = ?", (customer_id,))
        cursor.execute("DELETE FROM customers WHERE id = ?", (customer_id,))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Customer removed via API: {customer_email}")
        
        return jsonify({
            'success': True,
            'projects_removed': len(projects),
            'freed_space': freed_space,
            'message': 'Customer removed successfully'
        })
        
    except Exception as e:
        logger.error(f"Admin remove customer error: {e}")
        return jsonify({'error': f'Removal failed: {str(e)}'}), 500



if __name__ == '__main__':
    # Initialize database
    init_portal_db()
    
    port = int(os.environ.get('PORT', 5000))
    # Always bind to 0.0.0.0 for Railway deployment, localhost for local dev
    host = '0.0.0.0' if os.environ.get('RAILWAY_ENVIRONMENT') or os.environ.get('PORT') else '127.0.0.1'
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    logger.info(f"Starting Customer Portal (Lite) on {host}:{port}")
    app.run(host=host, port=port, debug=debug)
