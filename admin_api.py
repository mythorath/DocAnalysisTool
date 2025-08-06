#!/usr/bin/env python3
"""
Admin API for Remote Database Management
Separate Flask app for admin endpoints to avoid naming conflicts.
"""

import os
import sys
import sqlite3
import uuid
import json
import base64
from pathlib import Path
from datetime import datetime
from flask import Flask, request, jsonify
from functools import wraps

# Configuration
ADMIN_DATA_DIR = Path("admin_data")
CUSTOMER_DATABASES_DIR = Path("customer_databases")

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'admin_secret_key_change_me')

def require_admin_key(f):
    """Decorator to require admin API key for admin endpoints."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Missing or invalid authorization header'}), 401
        
        provided_key = auth_header.replace('Bearer ', '')
        expected_key = os.environ.get('ADMIN_API_KEY', 'default_admin_key_change_me')
        
        if provided_key != expected_key:
            return jsonify({'error': 'Invalid admin API key'}), 401
        
        return f(*args, **kwargs)
    return decorated_function

@app.route('/health')
@require_admin_key
def admin_health():
    """Admin health check with version info."""
    return jsonify({
        'status': 'healthy',
        'service': 'admin-api',
        'version': '2.0.0',
        'timestamp': datetime.now().isoformat(),
        'admin_access': True
    })

@app.route('/customers')
@require_admin_key
def list_customers():
    """List all customers with their projects for admin."""
    try:
        # Ensure directories exist
        ADMIN_DATA_DIR.mkdir(exist_ok=True)
        CUSTOMER_DATABASES_DIR.mkdir(exist_ok=True)
        
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
        return jsonify({'error': f'Failed to list customers: {str(e)}'}), 500

@app.route('/upload-database', methods=['POST'])
@require_admin_key
def upload_database():
    """Upload a database via API."""
    try:
        # Ensure directories exist
        ADMIN_DATA_DIR.mkdir(exist_ok=True)
        CUSTOMER_DATABASES_DIR.mkdir(exist_ok=True)
        
        data = request.get_json()
        
        customer_email = data.get('customer_email')
        project_name = data.get('project_name')
        description = data.get('description', '')
        database_data = data.get('database_data')  # Base64 encoded
        
        if not all([customer_email, project_name, database_data]):
            return jsonify({'error': 'Missing required fields: customer_email, project_name, database_data'}), 400
        
        # Decode database data
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
        
        # Get or create customer
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
        
        return jsonify({
            'success': True,
            'database_id': database_id,
            'database_filename': db_filename,
            'message': 'Database uploaded successfully'
        })
        
    except Exception as e:
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500

@app.route('/remove-project', methods=['DELETE'])
@require_admin_key
def remove_project():
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
        
        return jsonify({
            'success': True,
            'freed_space': freed_space,
            'message': 'Project removed successfully'
        })
        
    except Exception as e:
        return jsonify({'error': f'Removal failed: {str(e)}'}), 500

@app.route('/remove-customer', methods=['DELETE'])
@require_admin_key
def remove_customer():
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
        
        return jsonify({
            'success': True,
            'projects_removed': len(projects),
            'freed_space': freed_space,
            'message': 'Customer removed successfully'
        })
        
    except Exception as e:
        return jsonify({'error': f'Removal failed: {str(e)}'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    host = '0.0.0.0' if os.environ.get('RAILWAY_ENVIRONMENT') or os.environ.get('PORT') else '127.0.0.1'
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    print(f"Starting Admin API on {host}:{port}")
    app.run(host=host, port=port, debug=debug)