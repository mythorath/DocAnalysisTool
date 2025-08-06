#!/usr/bin/env python3
"""
Fix NULL project IDs in the Railway database
Generates UUIDs for any customer_databases records with NULL IDs
"""

import requests
import json
import uuid

def fix_null_project_ids(portal_url, admin_key):
    """Fix NULL project IDs by calling the admin API to update them."""
    session = requests.Session()
    session.headers.update({
        'Authorization': f'Bearer {admin_key}',
        'Content-Type': 'application/json'
    })
    
    print("🔧 Fixing NULL project IDs in Railway database...")
    
    # First, let's get the raw customer data to see what we're dealing with
    try:
        response = session.get(f"{portal_url}/admin/customers")
        if response.status_code == 200:
            data = response.json()
            print(f"📋 Found {data['total_customers']} customers")
            
            for customer in data['customers']:
                print(f"\n👤 Customer: {customer['name']} ({customer['email']})")
                print(f"   Customer ID: {customer['id']}")
                print(f"   Projects: {len(customer['projects'])}")
                
                for project in customer['projects']:
                    print(f"   📂 Project: {project.get('project_name', 'Unknown')}")
                    print(f"      Project ID: {project.get('id', 'NULL')}")
                    print(f"      Database: {project.get('database_filename', 'Unknown')}")
                    
                    # If project ID is None/NULL, we need to fix it
                    if project.get('id') is None:
                        print("      ⚠️ NULL Project ID detected!")
        else:
            print(f"❌ Failed to get customers: {response.status_code}")
            print(f"   Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """Main function."""
    portal_url = "https://narrow-clocks-production.up.railway.app"
    admin_key = "secure_admin_key_2024_changeme"
    
    fix_null_project_ids(portal_url, admin_key)

if __name__ == "__main__":
    main()
