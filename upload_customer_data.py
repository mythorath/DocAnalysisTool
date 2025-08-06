#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Customer Data Upload Utility
Tool for uploading processed customer databases to the online portal.
"""

import os
import sys
import sqlite3
import uuid
import shutil
from datetime import datetime
from pathlib import Path
import argparse
from werkzeug.security import generate_password_hash

# Windows console emoji compatibility
def safe_print(text):
    """Print text with emoji fallbacks for Windows console."""
    if os.name == 'nt':
        # Replace problematic emojis with ASCII equivalents
        text = (text.replace('✅', '[OK]')
                   .replace('❌', '[ERROR]')
                   .replace('⚠️', '[WARNING]')
                   .replace('📊', '[DATA]')
                   .replace('👤', '[USER]')
                   .replace('📄', '[DOCS]')
                   .replace('💾', '[DB]')
                   .replace('🔐', '[SECURE]')
                   .replace('📋', '[LIST]')
                   .replace('🗑️', '[DELETE]'))
    try:
        print(text)
    except UnicodeEncodeError:
        # Final fallback - remove all non-ASCII characters
        print(text.encode('ascii', 'ignore').decode('ascii'))

class CustomerDataUploader:
    """Handles uploading customer databases to the portal."""
    
    def __init__(self, portal_data_dir="portal_data"):
        self.portal_data_dir = Path(portal_data_dir)
        self.databases_dir = self.portal_data_dir / "databases"
        self.admin_dir = self.portal_data_dir / "admin"
        
        # Ensure directories exist
        for directory in [self.portal_data_dir, self.databases_dir, self.admin_dir]:
            directory.mkdir(parents=True, exist_ok=True)
        
        # Initialize portal database if needed
        self.init_portal_db()
    
    def init_portal_db(self):
        """Initialize portal customer database."""
        db_path = self.admin_dir / 'customers.db'
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Customers table
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
        
        # Customer databases table
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
    
    def create_customer(self, email, name, password, organization=""):
        """Create a new customer account."""
        db_path = self.admin_dir / 'customers.db'
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        customer_id = str(uuid.uuid4())
        password_hash = generate_password_hash(password)
        
        try:
            cursor.execute('''
                INSERT INTO customers (id, email, password_hash, name, organization)
                VALUES (?, ?, ?, ?, ?)
            ''', (customer_id, email.lower(), password_hash, name, organization))
            
            conn.commit()
            conn.close()
            
            safe_print(f"✅ Created customer: {email}")
            safe_print(f"🔐 Password: {password}")
            print(f"🆔 Customer ID: {customer_id}")
            
            return customer_id
            
        except sqlite3.IntegrityError:
            conn.close()
            safe_print(f"❌ Customer with email {email} already exists")
            return None
    
    def list_customers(self):
        """List all customers."""
        db_path = self.admin_dir / 'customers.db'
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM customers ORDER BY created_at DESC')
        customers = cursor.fetchall()
        conn.close()
        
        if not customers:
            print("📭 No customers found")
            return []
        
        print("\n👥 Customers:")
        print("=" * 80)
        
        customer_list = []
        for customer in customers:
            print(f"📧 {customer['email']}")
            print(f"   Name: {customer['name']}")
            print(f"   Organization: {customer['organization'] or 'None'}")
            print(f"   Created: {customer['created_at'][:10]}")
            print(f"   ID: {customer['id']}")
            print()
            
            customer_list.append(dict(customer))
        
        return customer_list
    
    def upload_database(self, database_path, customer_email, project_name, description=""):
        """Upload a processed database for a customer."""
        
        # Verify database exists
        if not os.path.exists(database_path):
            safe_print(f"❌ Database not found: {database_path}")
            return False
        
        # Get customer info
        db_path = self.admin_dir / 'customers.db'
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM customers WHERE email = ?', (customer_email.lower(),))
        customer = cursor.fetchone()
        
        if not customer:
            conn.close()
            safe_print(f"❌ Customer not found: {customer_email}")
            print("   Use 'create-customer' command to create them first")
            return False
        
        customer = dict(customer)
        
        # Count documents in database
        try:
            db_conn = sqlite3.connect(database_path)
            db_cursor = db_conn.cursor()
            db_cursor.execute('SELECT COUNT(*) FROM document_metadata')
            document_count = db_cursor.fetchone()[0]
            db_conn.close()
        except Exception as e:
            safe_print(f"⚠️ Could not count documents: {e}")
            document_count = 0
        
        # Generate unique filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_project_name = "".join(c for c in project_name if c.isalnum() or c in (' ', '-', '_')).strip()
        safe_project_name = safe_project_name.replace(' ', '_')
        database_filename = f"{customer['id']}_{timestamp}_{safe_project_name}.db"
        
        # Copy database to portal
        destination = self.databases_dir / database_filename
        shutil.copy2(database_path, destination)
        
        # Add to portal database
        project_id = str(uuid.uuid4())
        
        cursor.execute('''
            INSERT INTO customer_databases (id, customer_id, project_name, database_filename, document_count, description)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (project_id, customer['id'], project_name, database_filename, document_count, description))
        
        conn.commit()
        conn.close()
        
        safe_print(f"✅ Database uploaded successfully!")
        safe_print(f"👤 Customer: {customer['name']} ({customer_email})")
        safe_print(f"📊 Project: {project_name}")
        safe_print(f"📄 Documents: {document_count}")
        safe_print(f"💾 Database: {database_filename}")
        print(f"🆔 Project ID: {project_id}")
        
        return True
    
    def list_customer_projects(self, customer_email=None):
        """List projects for a customer or all customers."""
        db_path = self.admin_dir / 'customers.db'
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if customer_email:
            cursor.execute('''
                SELECT cd.*, c.name, c.email 
                FROM customer_databases cd
                JOIN customers c ON cd.customer_id = c.id
                WHERE c.email = ?
                ORDER BY cd.uploaded_at DESC
            ''', (customer_email.lower(),))
        else:
            cursor.execute('''
                SELECT cd.*, c.name, c.email 
                FROM customer_databases cd
                JOIN customers c ON cd.customer_id = c.id
                ORDER BY cd.uploaded_at DESC
            ''')
        
        projects = cursor.fetchall()
        conn.close()
        
        if not projects:
            print("📭 No projects found")
            return
        
        safe_print("\n📊 Customer Projects:")
        print("=" * 80)
        
        for project in projects:
            print(f"📧 {project['email']} - {project['name']}")
            print(f"   Project: {project['project_name']}")
            print(f"   Documents: {project['document_count']}")
            print(f"   Uploaded: {project['uploaded_at'][:19]}")
            print(f"   Database: {project['database_filename']}")
            if project['description']:
                print(f"   Description: {project['description']}")
            print()

def main():
    """Main CLI interface."""
    parser = argparse.ArgumentParser(description="Customer Data Upload Utility")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Create customer command
    create_parser = subparsers.add_parser('create-customer', help='Create a new customer account')
    create_parser.add_argument('email', help='Customer email address')
    create_parser.add_argument('name', help='Customer full name')
    create_parser.add_argument('password', help='Customer password')
    create_parser.add_argument('--organization', help='Customer organization')
    
    # List customers command
    list_parser = subparsers.add_parser('list-customers', help='List all customers')
    
    # Upload database command
    upload_parser = subparsers.add_parser('upload', help='Upload processed database for customer')
    upload_parser.add_argument('database_path', help='Path to processed database file')
    upload_parser.add_argument('customer_email', help='Customer email address')
    upload_parser.add_argument('project_name', help='Project name')
    upload_parser.add_argument('--description', help='Project description')
    
    # List projects command
    projects_parser = subparsers.add_parser('list-projects', help='List customer projects')
    projects_parser.add_argument('--customer', help='List projects for specific customer email')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    uploader = CustomerDataUploader()
    
    if args.command == 'create-customer':
        uploader.create_customer(
            args.email, 
            args.name, 
            args.password, 
            args.organization or ""
        )
    
    elif args.command == 'list-customers':
        uploader.list_customers()
    
    elif args.command == 'upload':
        uploader.upload_database(
            args.database_path,
            args.customer_email,
            args.project_name,
            args.description or ""
        )
    
    elif args.command == 'list-projects':
        uploader.list_customer_projects(args.customer)

if __name__ == "__main__":
    main()

