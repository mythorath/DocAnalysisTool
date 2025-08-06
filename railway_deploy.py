#!/usr/bin/env python3
"""
Simple Railway deployment for the secure document platform.
This script sets up everything needed to get your platform live.
"""

import os
import subprocess
import json
import secrets

def run_command(cmd, check=True):
    """Run shell command and return result."""
    print(f"🔧 {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"❌ Error: {result.stderr}")
        return False, result.stderr
    return True, result.stdout.strip()

def check_dependencies():
    """Check if Railway CLI is installed."""
    success, _ = run_command("railway --version", check=False)
    if not success:
        print("📦 Installing Railway CLI...")
        print("Please run: npm install -g @railway/cli")
        print("Or visit: https://railway.app/cli")
        return False
    return True

def create_railway_files():
    """Create necessary files for Railway deployment."""
    
    # Create Procfile for Railway
    procfile = "web: HOST=0.0.0.0 PORT=$PORT python customer_portal_lite.py"
    with open('Procfile', 'w') as f:
        f.write(procfile)
    
    # Create runtime.txt
    runtime = "python-3.11.0"
    with open('runtime.txt', 'w') as f:
        f.write(runtime)
    
    # Create requirements.txt for Railway
    requirements = """Flask==2.3.3
Werkzeug==2.3.7
pandas==2.1.1
sqlite3
gunicorn==21.2.0
python-dotenv==1.0.0
requests==2.31.0
"""
    
    with open('requirements.txt', 'w') as f:
        f.write(requirements)
    
    print("✅ Created Railway deployment files")

def deploy_to_railway():
    """Deploy the platform to Railway."""
    
    print("🚂 Starting Railway deployment...")
    
    # Check if already in a Railway project
    success, _ = run_command("railway status", check=False)
    if not success:
        print("📦 Creating new Railway project...")
        success, _ = run_command("railway login")
        if not success:
            print("❌ Railway login failed")
            return False
        
        success, _ = run_command("railway create secure-document-platform")
        if not success:
            print("❌ Failed to create Railway project")
            return False
    
    # Set environment variables
    print("⚙️ Setting environment variables...")
    secret_key = secrets.token_hex(32)
    
    env_vars = {
        'FLASK_ENV': 'production',
        'SECRET_KEY': secret_key,
        'ADMIN_API_KEY': 'secure_admin_key_2024_changeme',
        'PORT': '8080',
        'HOST': '0.0.0.0'
    }
    
    for key, value in env_vars.items():
        success, _ = run_command(f'railway env set {key}="{value}"')
        if not success:
            print(f"⚠️ Warning: Failed to set {key}")
    
    # Deploy
    print("🚀 Deploying to Railway...")
    success, output = run_command("railway deploy")
    if not success:
        print("❌ Deployment failed")
        print(output)
        return False
    
    # Get URL
    print("🔍 Getting deployment URL...")
    success, url = run_command("railway url", check=False)
    if success and url:
        print(f"✅ Platform deployed successfully!")
        print(f"🌐 Your platform URL: {url}")
        print(f"🔐 Admin login: admin@platform.com / admin123")
        print(f"⚠️ Change admin password immediately!")
        return url
    else:
        print("✅ Deployment successful! Check Railway dashboard for URL.")
        return True

def main():
    """Main deployment function."""
    print("🌐 Railway Deployment for Secure Document Platform")
    print("=" * 60)
    
    if not check_dependencies():
        return
    
    create_railway_files()
    
    print("\n🚀 Ready to deploy!")
    confirm = input("Deploy to Railway now? (y/N): ").lower().strip()
    if confirm != 'y':
        print("❌ Deployment cancelled")
        return
    
    result = deploy_to_railway()
    
    if result:
        print("\n" + "=" * 60)
        print("🎉 DEPLOYMENT COMPLETE!")
        print("=" * 60)
        print("\n📱 Next Steps:")
        print("1. Visit your platform URL")
        print("2. Login as admin (admin@platform.com / admin123)")
        print("3. Change the admin password immediately")
        print("4. Create your first customer account")
        print("5. Test the document processing workflow")
        print("\n✅ Your secure document platform is now live!")

if __name__ == "__main__":
    main()
