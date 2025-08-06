#!/usr/bin/env python3
"""
Quick setup script for remote data management.
Sets up environment variables for accessing the deployed portal.
"""

import os
import sys

def main():
    print("🚀 Setting up Remote Data Management Access")
    print("=" * 50)
    
    # Default values
    default_portal_url = "https://narrow-clocks-production.up.railway.app"
    default_admin_key = "secure_admin_key_2024_changeme"
    
    print(f"\n📍 Portal URL: {default_portal_url}")
    print(f"🔑 Admin Key: {default_admin_key}")
    
    print("\n🔧 Setting environment variables...")
    
    # Set environment variables for current session
    os.environ['PORTAL_URL'] = default_portal_url
    os.environ['ADMIN_API_KEY'] = default_admin_key
    
    print("✅ Environment variables set for current session!")
    
    # Test connection
    print("\n🧪 Testing connection...")
    try:
        import requests
        from urllib.parse import urljoin
        
        session = requests.Session()
        session.headers.update({
            'Authorization': f'Bearer {default_admin_key}',
            'Content-Type': 'application/json'
        })
        
        url = urljoin(default_portal_url, '/admin/health')
        response = session.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Connected successfully!")
            print(f"   Service: {data.get('service', 'Unknown')}")
            print(f"   Version: {data.get('version', 'Unknown')}")
        else:
            print(f"❌ Connection failed: HTTP {response.status_code}")
            print(f"   Response: {response.text}")
            
    except ImportError:
        print("⚠️  'requests' library not installed - install it to test connection")
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 READY TO USE!")
    print("\nNow you can run:")
    print("  python remote_data_manager.py test")
    print("  python remote_data_manager.py list")
    print("  python remote_data_manager.py upload database.db customer@email.com 'Project'")
    
    print("\n💡 To make these permanent, add to your system environment:")
    print(f"   PORTAL_URL={default_portal_url}")
    print(f"   ADMIN_API_KEY={default_admin_key}")

if __name__ == '__main__':
    main()
