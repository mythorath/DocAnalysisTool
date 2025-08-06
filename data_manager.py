#!/usr/bin/env python3
"""
Data Management Tool for Customer Portal
Allows easy management of customer data, projects, and databases.
"""

import os
import sys
import sqlite3
import shutil
import argparse
from pathlib import Path
from datetime import datetime
import json

# Configuration
ADMIN_DATA_DIR = Path("admin_data")
CUSTOMER_DATABASES_DIR = Path("customer_databases")

def init_dirs():
    """Initialize required directories."""
    ADMIN_DATA_DIR.mkdir(exist_ok=True)
    CUSTOMER_DATABASES_DIR.mkdir(exist_ok=True)

def format_size(size_bytes):
    """Format file size in human readable format."""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"

def get_database_info(db_path):
    """Get information about a customer database."""
    if not db_path.exists():
        return {"exists": False}
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get document count
        cursor.execute("SELECT COUNT(*) FROM document_metadata")
        doc_count = cursor.fetchone()[0]
        
        # Get total text size
        cursor.execute("SELECT SUM(character_count) FROM document_metadata")
        total_chars = cursor.fetchone()[0] or 0
        
        conn.close()
        
        # Get file size
        file_size = db_path.stat().st_size
        
        return {
            "exists": True,
            "document_count": doc_count,
            "total_characters": total_chars,
            "file_size": file_size,
            "file_size_human": format_size(file_size)
        }
    except Exception as e:
        return {"exists": True, "error": str(e)}

def list_customers():
    """List all customers and their projects."""
    init_dirs()
    
    db_path = ADMIN_DATA_DIR / "customers.db"
    if not db_path.exists():
        print("❌ No customer database found. Run the portal first to initialize.")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get customers with project counts
        cursor.execute('''
            SELECT c.*, COUNT(cd.id) as project_count
            FROM customers c
            LEFT JOIN customer_databases cd ON c.id = cd.customer_id
            GROUP BY c.id
            ORDER BY c.name
        ''')
        
        customers = cursor.fetchall()
        
        if not customers:
            print("📋 No customers found.")
            return
        
        print("\n📋 Customer Overview")
        print("=" * 80)
        
        total_customers = len(customers)
        total_projects = 0
        total_size = 0
        
        for customer in customers:
            print(f"\n👤 {customer['name']} ({customer['email']})")
            print(f"   Organization: {customer['organization'] or 'N/A'}")
            print(f"   Projects: {customer['project_count']}")
            print(f"   Created: {customer['created_at'][:10] if customer['created_at'] else 'Unknown'}")
            
            # Get project details
            cursor.execute('''
                SELECT * FROM customer_databases 
                WHERE customer_id = ? 
                ORDER BY uploaded_at DESC
            ''', (customer['id'],))
            
            projects = cursor.fetchall()
            total_projects += len(projects)
            
            for project in projects:
                db_file = CUSTOMER_DATABASES_DIR / project['database_filename']
                db_info = get_database_info(db_file)
                
                if db_info['exists']:
                    if 'error' in db_info:
                        status = f"❌ Error: {db_info['error']}"
                    else:
                        status = f"✅ {db_info['document_count']} docs, {db_info['file_size_human']}"
                        total_size += db_info['file_size']
                else:
                    status = "❌ Database file missing"
                
                upload_date = project['uploaded_at'][:10] if project['uploaded_at'] else 'Unknown'
                print(f"     📊 {project['project_name']} - {status} - {upload_date}")
        
        print(f"\n📊 Summary")
        print(f"   Total Customers: {total_customers}")
        print(f"   Total Projects: {total_projects}")
        print(f"   Total Data Size: {format_size(total_size)}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error listing customers: {e}")

def remove_customer(customer_email):
    """Remove a customer and all their data."""
    init_dirs()
    
    db_path = ADMIN_DATA_DIR / "customers.db"
    if not db_path.exists():
        print("❌ No customer database found.")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Find customer
        cursor.execute("SELECT * FROM customers WHERE email = ?", (customer_email,))
        customer = cursor.fetchone()
        
        if not customer:
            print(f"❌ Customer not found: {customer_email}")
            conn.close()
            return
        
        print(f"🗑️ Removing customer: {customer['name']} ({customer['email']})")
        
        # Get all projects for this customer
        cursor.execute("SELECT * FROM customer_databases WHERE customer_id = ?", (customer['id'],))
        projects = cursor.fetchall()
        
        if projects:
            print(f"   Found {len(projects)} projects to remove:")
            
            # Remove database files
            for project in projects:
                db_file = CUSTOMER_DATABASES_DIR / project['database_filename']
                if db_file.exists():
                    try:
                        db_file.unlink()
                        print(f"   ✅ Removed database: {project['database_filename']}")
                    except Exception as e:
                        print(f"   ❌ Failed to remove {project['database_filename']}: {e}")
                else:
                    print(f"   ⚠️ Database file not found: {project['database_filename']}")
            
            # Remove database records
            cursor.execute("DELETE FROM customer_databases WHERE customer_id = ?", (customer['id'],))
            print(f"   ✅ Removed {len(projects)} project records")
        
        # Remove customer record
        cursor.execute("DELETE FROM customers WHERE id = ?", (customer['id'],))
        
        conn.commit()
        conn.close()
        
        print(f"✅ Customer {customer['email']} completely removed")
        
    except Exception as e:
        print(f"❌ Error removing customer: {e}")

def remove_project(customer_email, project_name):
    """Remove a specific project from a customer."""
    init_dirs()
    
    db_path = ADMIN_DATA_DIR / "customers.db"
    if not db_path.exists():
        print("❌ No customer database found.")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Find customer and project
        cursor.execute('''
            SELECT cd.*, c.name as customer_name, c.email
            FROM customer_databases cd
            JOIN customers c ON cd.customer_id = c.id
            WHERE c.email = ? AND cd.project_name = ?
        ''', (customer_email, project_name))
        
        project = cursor.fetchone()
        
        if not project:
            print(f"❌ Project not found: {project_name} for {customer_email}")
            conn.close()
            return
        
        print(f"🗑️ Removing project: {project_name} from {project['customer_name']}")
        
        # Remove database file
        db_file = CUSTOMER_DATABASES_DIR / project['database_filename']
        if db_file.exists():
            try:
                db_file.unlink()
                print(f"   ✅ Removed database: {project['database_filename']}")
            except Exception as e:
                print(f"   ❌ Failed to remove database: {e}")
        else:
            print(f"   ⚠️ Database file not found: {project['database_filename']}")
        
        # Remove database record
        cursor.execute("DELETE FROM customer_databases WHERE id = ?", (project['id'],))
        
        conn.commit()
        conn.close()
        
        print(f"✅ Project {project_name} removed from {customer_email}")
        
    except Exception as e:
        print(f"❌ Error removing project: {e}")

def cleanup_orphaned_files():
    """Remove database files that don't have corresponding records."""
    init_dirs()
    
    db_path = ADMIN_DATA_DIR / "customers.db"
    if not db_path.exists():
        print("❌ No customer database found.")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get all database filenames from records
        cursor.execute("SELECT database_filename FROM customer_databases")
        valid_files = {row[0] for row in cursor.fetchall()}
        
        conn.close()
        
        # Check all files in customer_databases directory
        orphaned_files = []
        total_size = 0
        
        for db_file in CUSTOMER_DATABASES_DIR.glob("*.db"):
            if db_file.name not in valid_files:
                size = db_file.stat().st_size
                orphaned_files.append((db_file, size))
                total_size += size
        
        if not orphaned_files:
            print("✅ No orphaned database files found.")
            return
        
        print(f"🗑️ Found {len(orphaned_files)} orphaned database files:")
        
        for db_file, size in orphaned_files:
            print(f"   📁 {db_file.name} - {format_size(size)}")
        
        print(f"\n💾 Total size: {format_size(total_size)}")
        
        response = input(f"\nRemove all {len(orphaned_files)} orphaned files? (y/N): ")
        if response.lower() == 'y':
            removed_count = 0
            for db_file, size in orphaned_files:
                try:
                    db_file.unlink()
                    removed_count += 1
                    print(f"   ✅ Removed: {db_file.name}")
                except Exception as e:
                    print(f"   ❌ Failed to remove {db_file.name}: {e}")
            
            print(f"\n✅ Removed {removed_count}/{len(orphaned_files)} orphaned files")
            print(f"💾 Freed {format_size(total_size)} of disk space")
        else:
            print("❌ Cleanup cancelled.")
        
    except Exception as e:
        print(f"❌ Error during cleanup: {e}")

def export_customer_list():
    """Export customer and project information to JSON."""
    init_dirs()
    
    db_path = ADMIN_DATA_DIR / "customers.db"
    if not db_path.exists():
        print("❌ No customer database found.")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get all customers with their projects
        cursor.execute('''
            SELECT c.*, 
                   GROUP_CONCAT(cd.project_name, '|') as projects,
                   GROUP_CONCAT(cd.uploaded_at, '|') as upload_dates,
                   COUNT(cd.id) as project_count
            FROM customers c
            LEFT JOIN customer_databases cd ON c.id = cd.customer_id
            GROUP BY c.id
            ORDER BY c.name
        ''')
        
        customers = cursor.fetchall()
        
        export_data = {
            "export_date": datetime.now().isoformat(),
            "total_customers": len(customers),
            "customers": []
        }
        
        for customer in customers:
            customer_data = {
                "name": customer['name'],
                "email": customer['email'],
                "organization": customer['organization'],
                "created_at": customer['created_at'],
                "project_count": customer['project_count'],
                "projects": customer['projects'].split('|') if customer['projects'] else []
            }
            export_data["customers"].append(customer_data)
        
        conn.close()
        
        # Save to file
        export_file = f"customer_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(export_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Customer data exported to: {export_file}")
        print(f"📊 {export_data['total_customers']} customers exported")
        
    except Exception as e:
        print(f"❌ Error exporting data: {e}")

def main():
    """Main CLI interface."""
    parser = argparse.ArgumentParser(description="Customer Portal Data Manager")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List all customers and projects')
    
    # Remove customer command
    remove_customer_parser = subparsers.add_parser('remove-customer', help='Remove a customer and all their data')
    remove_customer_parser.add_argument('email', help='Customer email address')
    
    # Remove project command
    remove_project_parser = subparsers.add_parser('remove-project', help='Remove a specific project')
    remove_project_parser.add_argument('email', help='Customer email address')
    remove_project_parser.add_argument('project', help='Project name')
    
    # Cleanup command
    cleanup_parser = subparsers.add_parser('cleanup', help='Remove orphaned database files')
    
    # Export command
    export_parser = subparsers.add_parser('export', help='Export customer data to JSON')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        print("\n💡 Examples:")
        print("   python data_manager.py list")
        print("   python data_manager.py remove-customer customer@example.com")
        print("   python data_manager.py remove-project customer@example.com \"Project Name\"")
        print("   python data_manager.py cleanup")
        print("   python data_manager.py export")
        return
    
    print("🗂️ Customer Portal Data Manager")
    print("=" * 50)
    
    if args.command == 'list':
        list_customers()
    elif args.command == 'remove-customer':
        remove_customer(args.email)
    elif args.command == 'remove-project':
        remove_project(args.email, args.project)
    elif args.command == 'cleanup':
        cleanup_orphaned_files()
    elif args.command == 'export':
        export_customer_list()

if __name__ == "__main__":
    main()
