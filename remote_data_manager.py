#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Remote Database Management Tool
Push customer databases to deployed portal and manage them remotely via API.
"""

import os
import sys
import requests
import sqlite3
import json
import base64
from pathlib import Path
from datetime import datetime
import argparse

# Windows console emoji compatibility
def safe_print(text):
    """Print text with emoji fallbacks for Windows console."""
    if os.name == 'nt':
        # Replace problematic emojis with ASCII equivalents
        text = (text.replace('✅', '[OK]')
                   .replace('❌', '[ERROR]')
                   .replace('📤', '[UPLOAD]')
                   .replace('📋', '[LIST]')
                   .replace('👤', '[USER]')
                   .replace('📊', '[DATA]')
                   .replace('🗑️', '[DELETE]')
                   .replace('⚠️', '[WARNING]')
                   .replace('🌐', '[REMOTE]'))
    try:
        print(text)
    except UnicodeEncodeError:
        # Final fallback - remove all non-ASCII characters
        print(text.encode('ascii', 'ignore').decode('ascii'))
from urllib.parse import urljoin

class RemoteDataManager:
    """Manages customer databases on the deployed portal via API."""
    
    def __init__(self, portal_url=None, admin_key=None):
        """
        Initialize remote data manager.
        
        Args:
            portal_url: Base URL of deployed portal (e.g., https://your-app.railway.app)
            admin_key: Admin API key for authentication
        """
        # Try to get from environment variables or config
        self.portal_url = portal_url or os.getenv('PORTAL_URL')
        self.admin_key = admin_key or os.getenv('ADMIN_API_KEY')
        
        if not self.portal_url:
            safe_safe_print("❌ Portal URL not set. Use --url or set PORTAL_URL environment variable")
            sys.exit(1)
        
        if not self.admin_key:
            safe_print("❌ Admin API key not set. Use --key or set ADMIN_API_KEY environment variable")
            sys.exit(1)
        
        # Ensure URL format
        if not self.portal_url.startswith(('http://', 'https://')):
            self.portal_url = f"https://{self.portal_url}"
        
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {self.admin_key}',
            'Content-Type': 'application/json'
        })
    
    def test_connection(self):
        """Test connection to the deployed portal."""
        try:
            url = urljoin(self.portal_url, '/admin/health')
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                safe_print(f"✅ Connected to portal: {data.get('service', 'Unknown')}")
                print(f"   URL: {self.portal_url}")
                print(f"   Version: {data.get('version', 'Unknown')}")
                return True
            else:
                safe_print(f"❌ Connection failed: HTTP {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            safe_print(f"❌ Connection error: {e}")
            return False
    
    def upload_database(self, db_path, customer_email, project_name, description=None):
        """
        Upload a customer database to the deployed portal.
        
        Args:
            db_path: Path to local database file
            customer_email: Customer email address
            project_name: Name of the project
            description: Optional project description
        """
        db_path = Path(db_path)
        
        if not db_path.exists():
            safe_print(f"❌ Database file not found: {db_path}")
            return False
        
        safe_print(f"📤 Uploading database: {db_path.name}")
        print(f"   Customer: {customer_email}")
        print(f"   Project: {project_name}")
        
        try:
            # Read and encode database file
            with open(db_path, 'rb') as f:
                db_data = base64.b64encode(f.read()).decode('utf-8')
            
            # Get database info
            db_info = self._get_db_info(db_path)
            
            # Prepare upload data
            upload_data = {
                'customer_email': customer_email,
                'project_name': project_name,
                'description': description,
                'database_data': db_data,
                'database_info': db_info,
                'upload_source': 'remote_cli'
            }
            
            # Upload to portal
            url = urljoin(self.portal_url, '/admin/upload-database')
            response = self.session.post(url, json=upload_data, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                safe_print(f"✅ Upload successful!")
                print(f"   Database ID: {result.get('database_id')}")
                print(f"   File size: {self._format_size(db_path.stat().st_size)}")
                print(f"   Documents: {db_info.get('document_count', 'Unknown')}")
                return True
            else:
                error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
                safe_print(f"❌ Upload failed: {error_data.get('error', 'Unknown error')}")
                return False
                
        except Exception as e:
            safe_print(f"❌ Upload error: {e}")
            return False
    
    def list_remote_data(self):
        """List all customer data on the deployed portal."""
        try:
            url = urljoin(self.portal_url, '/admin/customers')
            response = self.session.get(url, timeout=30)
            
            if response.status_code != 200:
                safe_print(f"❌ Failed to fetch data: HTTP {response.status_code}")
                return
            
            data = response.json()
            customers = data.get('customers', [])
            
            if not customers:
                safe_print("📋 No customers found on the portal")
                return
            
            safe_print(f"\n📋 Remote Portal Data ({len(customers)} customers)")
            print("=" * 80)
            
            total_projects = 0
            total_size = 0
            
            for customer in customers:
                safe_print(f"\n👤 {customer['name']} ({customer['email']})")
                print(f"   Organization: {customer.get('organization', 'N/A')}")
                print(f"   Created: {customer.get('created_at', 'Unknown')[:10]}")
                
                projects = customer.get('projects', [])
                total_projects += len(projects)
                
                for project in projects:
                    size = project.get('file_size', 0)
                    total_size += size
                    
                    safe_print(f"     📊 {project['project_name']}")
                    print(f"        Documents: {project.get('document_count', 'Unknown')}")
                    print(f"        Size: {self._format_size(size)}")
                    print(f"        Uploaded: {project.get('uploaded_at', 'Unknown')[:10]}")
            
            safe_print(f"\n📊 Summary:")
            print(f"   Total Customers: {len(customers)}")
            print(f"   Total Projects: {total_projects}")
            print(f"   Total Data Size: {self._format_size(total_size)}")
            
        except Exception as e:
            safe_print(f"❌ Error listing data: {e}")
    
    def remove_remote_project(self, customer_email, project_name):
        """Remove a project from the deployed portal."""
        try:
            safe_print(f"🗑️ Removing project: {project_name}")
            print(f"   Customer: {customer_email}")
            
            url = urljoin(self.portal_url, '/admin/remove-project')
            data = {
                'customer_email': customer_email,
                'project_name': project_name
            }
            
            response = self.session.delete(url, json=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                safe_print(f"✅ Project removed successfully")
                if 'freed_space' in result:
                    print(f"   Freed space: {self._format_size(result['freed_space'])}")
                return True
            else:
                error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
                safe_print(f"❌ Removal failed: {error_data.get('error', 'Unknown error')}")
                return False
                
        except Exception as e:
            safe_print(f"❌ Error removing project: {e}")
            return False
    
    def remove_remote_customer(self, customer_email):
        """Remove a customer and all their data from the deployed portal."""
        try:
            safe_print(f"🗑️ Removing customer: {customer_email}")
            safe_print("   ⚠️ This will remove ALL projects for this customer!")
            
            confirm = input("   Type 'DELETE' to confirm: ")
            if confirm != 'DELETE':
                safe_print("❌ Deletion cancelled")
                return False
            
            url = urljoin(self.portal_url, '/admin/remove-customer')
            data = {'customer_email': customer_email}
            
            response = self.session.delete(url, json=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                safe_print(f"✅ Customer removed successfully")
                print(f"   Projects removed: {result.get('projects_removed', 'Unknown')}")
                if 'freed_space' in result:
                    print(f"   Freed space: {self._format_size(result['freed_space'])}")
                return True
            else:
                error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
                safe_print(f"❌ Removal failed: {error_data.get('error', 'Unknown error')}")
                return False
                
        except Exception as e:
            safe_print(f"❌ Error removing customer: {e}")
            return False
    
    def sync_local_to_remote(self, local_db_dir="customer_databases"):
        """Sync local databases to remote portal."""
        local_dir = Path(local_db_dir)
        
        if not local_dir.exists():
            safe_print(f"❌ Local database directory not found: {local_dir}")
            return
        
        # Get local databases
        local_dbs = list(local_dir.glob("*.db"))
        if not local_dbs:
            safe_print(f"📋 No local databases found in {local_dir}")
            return
        
        safe_print(f"📤 Found {len(local_dbs)} local databases")
        
        # Get remote data for comparison
        try:
            url = urljoin(self.portal_url, '/admin/customers')
            response = self.session.get(url, timeout=30)
            remote_data = response.json() if response.status_code == 200 else {'customers': []}
            
            # Build set of remote database filenames
            remote_files = set()
            for customer in remote_data.get('customers', []):
                for project in customer.get('projects', []):
                    remote_files.add(project.get('database_filename', ''))
            
            # Find databases to upload
            to_upload = []
            for db_file in local_dbs:
                if db_file.name not in remote_files:
                    to_upload.append(db_file)
            
            if not to_upload:
                safe_print("✅ All local databases are already uploaded")
                return
            
            safe_print(f"📤 {len(to_upload)} databases need uploading:")
            for db_file in to_upload:
                print(f"   📁 {db_file.name}")
            
            proceed = input(f"\nUpload {len(to_upload)} databases? (y/N): ")
            if proceed.lower() != 'y':
                safe_print("❌ Sync cancelled")
                return
            
            # Upload missing databases
            success_count = 0
            for db_file in to_upload:
                # Try to extract customer info from filename or prompt
                customer_email = input(f"\nCustomer email for {db_file.name}: ")
                project_name = input(f"Project name for {db_file.name}: ")
                
                if self.upload_database(db_file, customer_email, project_name):
                    success_count += 1
            
            safe_print(f"\n✅ Sync complete: {success_count}/{len(to_upload)} databases uploaded")
            
        except Exception as e:
            safe_print(f"❌ Sync error: {e}")
    
    def _get_db_info(self, db_path):
        """Get information about a database file."""
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Get document count
            cursor.execute("SELECT COUNT(*) FROM document_metadata")
            doc_count = cursor.fetchone()[0]
            
            # Get total characters
            cursor.execute("SELECT SUM(character_count) FROM document_metadata")
            total_chars = cursor.fetchone()[0] or 0
            
            conn.close()
            
            return {
                'document_count': doc_count,
                'total_characters': total_chars,
                'file_size': db_path.stat().st_size
            }
        except Exception as e:
            return {'error': str(e)}
    
    def _format_size(self, size_bytes):
        """Format file size in human readable format."""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024
            i += 1
        
        return f"{size_bytes:.1f} {size_names[i]}"

def main():
    """Main CLI interface."""
    parser = argparse.ArgumentParser(description="Remote Database Manager for Customer Portal")
    parser.add_argument('--url', help='Portal URL (or set PORTAL_URL env var)')
    parser.add_argument('--key', help='Admin API key (or set ADMIN_API_KEY env var)')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Test command
    test_parser = subparsers.add_parser('test', help='Test connection to portal')
    
    # Upload command
    upload_parser = subparsers.add_parser('upload', help='Upload database to portal')
    upload_parser.add_argument('database', help='Path to database file')
    upload_parser.add_argument('customer_email', help='Customer email address')
    upload_parser.add_argument('project_name', help='Project name')
    upload_parser.add_argument('--description', help='Project description')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List remote portal data')
    
    # Remove project command
    remove_project_parser = subparsers.add_parser('remove-project', help='Remove project from portal')
    remove_project_parser.add_argument('customer_email', help='Customer email')
    remove_project_parser.add_argument('project_name', help='Project name')
    
    # Remove customer command
    remove_customer_parser = subparsers.add_parser('remove-customer', help='Remove customer from portal')
    remove_customer_parser.add_argument('customer_email', help='Customer email')
    
    # Sync command
    sync_parser = subparsers.add_parser('sync', help='Sync local databases to portal')
    sync_parser.add_argument('--local-dir', default='customer_databases', help='Local database directory')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        print("\n💡 Examples:")
        print("   python remote_data_manager.py --url https://your-app.railway.app --key YOUR_API_KEY test")
        print("   python remote_data_manager.py upload database.db customer@email.com \"Project Name\"")
        print("   python remote_data_manager.py list")
        print("   python remote_data_manager.py remove-project customer@email.com \"Old Project\"")
        print("   python remote_data_manager.py sync")
        print("\n🔑 Set environment variables to avoid repeating URL/key:")
        print("   set PORTAL_URL=https://your-app.railway.app")
        print("   set ADMIN_API_KEY=your_secret_key")
        return
    
    # Initialize manager
    manager = RemoteDataManager(args.url, args.key)
    
    safe_print("🌐 Remote Database Manager")
    print("=" * 50)
    
    if args.command == 'test':
        manager.test_connection()
    elif args.command == 'upload':
        manager.upload_database(args.database, args.customer_email, args.project_name, args.description)
    elif args.command == 'list':
        manager.list_remote_data()
    elif args.command == 'remove-project':
        manager.remove_remote_project(args.customer_email, args.project_name)
    elif args.command == 'remove-customer':
        manager.remove_remote_customer(args.customer_email)
    elif args.command == 'sync':
        manager.sync_local_to_remote(args.local_dir)

if __name__ == "__main__":
    main()
