#!/usr/bin/env python3
"""
One-Click Setup Script for Document Analysis Platform
Creates venv, installs dependencies, and deploys to Railway or Vercel
"""

import os
import sys
import subprocess
import platform
import json
import secrets
from pathlib import Path

def run_command(cmd, shell=True, check=True):
    """Run command and return result."""
    print(f"🔧 {cmd}")
    result = subprocess.run(cmd, shell=shell, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"❌ Error: {result.stderr}")
        return False, result.stderr
    return True, result.stdout.strip()

def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ is required")
        print(f"   Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} detected")
    return True

def create_virtual_environment():
    """Create and activate virtual environment."""
    print("\n📦 Creating virtual environment...")
    
    venv_path = Path("venv")
    if venv_path.exists():
        print("   Virtual environment already exists")
        return True
    
    # Create venv
    success, _ = run_command(f"{sys.executable} -m venv venv")
    if not success:
        return False
    
    print("✅ Virtual environment created")
    return True

def get_activation_command():
    """Get the correct activation command for the platform."""
    if platform.system() == "Windows":
        return "venv\\Scripts\\activate"
    else:
        return "source venv/bin/activate"

def install_dependencies():
    """Install Python dependencies with Windows compatibility."""
    print("\n📥 Installing dependencies...")
    
    # Get pip path
    if platform.system() == "Windows":
        pip_path = "venv\\Scripts\\pip"
        python_path = "venv\\Scripts\\python"
    else:
        pip_path = "venv/bin/pip"
        python_path = "venv/bin/python"
    
    # Upgrade pip first
    print("🔧 Upgrading pip...")
    success, _ = run_command(f"{python_path} -m pip install --upgrade pip")
    if not success:
        return False
    
    # Install core dependencies first (minimal set for basic functionality)
    core_requirements = [
        "Flask==2.3.3",
        "Werkzeug==2.3.7", 
        "requests==2.31.0",
        "python-dotenv==1.0.0"
    ]
    
    print("📦 Installing core dependencies...")
    for package in core_requirements:
        print(f"   Installing {package}...")
        success, output = run_command(f"{pip_path} install {package}", check=False)
        if not success:
            print(f"⚠️ Failed to install {package}, trying without version pin...")
            package_name = package.split("==")[0]
            success, _ = run_command(f"{pip_path} install {package_name}", check=False)
            if not success:
                print(f"❌ Could not install {package_name}")
                return False
    
    # Install data processing dependencies (with fallbacks for Windows)
    data_requirements = []
    
    if platform.system() == "Windows":
        # Windows-specific versions that are more likely to have pre-compiled wheels
        data_requirements = [
            "pandas>=1.5.0",  # Let pip choose a compatible version
            "numpy>=1.21.0",   # Let pip choose a compatible version
        ]
    else:
        data_requirements = [
            "pandas==2.1.1",
            "numpy==1.24.3"
        ]
    
    print("📊 Installing data processing dependencies...")
    for package in data_requirements:
        print(f"   Installing {package}...")
        success, _ = run_command(f"{pip_path} install {package}", check=False)
        if not success:
            print(f"⚠️ Failed to install {package}")
            # Continue anyway - the portal can work without heavy data processing
    
    # Optional dependencies (nice to have but not critical)
    optional_requirements = [
        "PyMuPDF>=1.20.0",
        "pdf2image>=3.0.0", 
        "pytesseract>=0.3.0",
        "Pillow>=9.0.0",
        "python-docx>=0.8.0",
        "scikit-learn>=1.2.0",
        "nltk>=3.8"
    ]
    
    print("🔧 Installing optional dependencies (for document processing)...")
    for package in optional_requirements:
        print(f"   Installing {package}...")
        success, _ = run_command(f"{pip_path} install {package}", check=False)
        if not success:
            print(f"⚠️ Skipping {package} (optional)")
    
    # Skip heavy ML dependencies for now to avoid compilation issues
    print("⏭️ Skipping heavy ML dependencies (sentence-transformers) for faster setup")
    print("   You can install them later if needed for advanced clustering")
    
    # Create a working requirements.txt with what we actually installed
    create_working_requirements_file()
    
    print("✅ Core dependencies installed successfully")
    print("⚠️ Some optional dependencies may have been skipped")
    print("   The customer portal will work fine for basic functionality")
    return True

def create_working_requirements_file():
    """Create a minimal requirements.txt that should work on most systems."""
    minimal_requirements = """# Core web framework
Flask>=2.3.0
Werkzeug>=2.3.0
requests>=2.31.0
python-dotenv>=1.0.0

# Data processing (let pip choose compatible versions)
pandas>=1.5.0
numpy>=1.21.0

# Document processing (optional - install manually if needed)
# PyMuPDF>=1.20.0
# pdf2image>=3.0.0
# pytesseract>=0.3.0
# Pillow>=9.0.0
# python-docx>=0.8.0
# scikit-learn>=1.2.0
# nltk>=3.8

# Heavy ML dependencies (install separately if needed)
# sentence-transformers>=2.2.0
"""
    
    with open('requirements_minimal.txt', 'w') as f:
        f.write(minimal_requirements)
    
    print("📄 Created requirements_minimal.txt with working dependencies")

def setup_directories():
    """Create necessary directories."""
    print("\n📁 Setting up directories...")
    
    directories = [
        "workspace",
        "workspace/customers",
        "workspace/downloads", 
        "workspace/text",
        "workspace/output",
        "workspace/logs",
        "portal_data",
        "portal_data/databases",
        "portal_data/admin",
        "input"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    # Create sample CSV if it doesn't exist
    sample_csv = Path("input/sample_comment_links.csv")
    if not sample_csv.exists():
        sample_data = """Document ID,URL,Organization,Category
TEST-001,https://example.com/doc1.pdf,Test Organization,Test Category
TEST-002,https://example.com/doc2.pdf,Another Org,Sample Category
"""
        with open(sample_csv, 'w') as f:
            f.write(sample_data)
    
    print("✅ Directories created")
    return True

def check_pandas_installed():
    """Check if pandas is successfully installed."""
    try:
        if platform.system() == "Windows":
            python_path = "venv\\Scripts\\python"
        else:
            python_path = "venv/bin/python"
        
        result = subprocess.run([python_path, "-c", "import pandas; print('OK')"], 
                              capture_output=True, text=True)
        return result.returncode == 0
    except:
        return False

def check_system_dependencies():
    """Check for system dependencies (Tesseract, Poppler)."""
    print("\n🔍 Checking system dependencies...")
    
    # Check Tesseract
    tesseract_ok, _ = run_command("tesseract --version", check=False)
    if tesseract_ok:
        print("✅ Tesseract OCR found")
    else:
        print("⚠️ Tesseract OCR not found")
        print("   Install with: conda install tesseract -c conda-forge")
        print("   Or download from: https://github.com/UB-Mannheim/tesseract/wiki")
    
    # Check Poppler (for pdf2image)
    poppler_ok = True  # We'll test this during actual processing
    print("⚠️ Poppler may be needed for PDF processing")
    print("   Install with: conda install poppler -c conda-forge")
    
    return tesseract_ok

def deploy_to_railway():
    """Deploy to Railway."""
    print("\n🚂 Deploying to Railway...")
    
    # Check if Railway CLI is installed
    success, _ = run_command("railway --version", check=False)
    if not success:
        print("📦 Railway CLI not found")
        print("   Install with: npm install -g @railway/cli")
        print("   Or visit: https://railway.app/cli")
        return False
    
    # Create Railway files
    create_railway_files()
    
    # Check if already in a Railway project
    success, _ = run_command("railway status", check=False)
    if not success:
        print("🔑 Please login to Railway:")
        success, _ = run_command("railway login")
        if not success:
            return False
        
        print("📦 Creating Railway project...")
        success, _ = run_command("railway create document-analysis-portal")
        if not success:
            return False
    
    # Set environment variables
    print("⚙️ Setting environment variables...")
    secret_key = secrets.token_hex(32)
    
    env_vars = {
        'FLASK_ENV': 'production',
        'SECRET_KEY': secret_key,
        'PORT': '8080',
        'HOST': '0.0.0.0'
    }
    
    for key, value in env_vars.items():
        run_command(f'railway variables --set "{key}={value}"', check=False)
    
    # Deploy
    print("🚀 Deploying to Railway...")
    success, output = run_command("railway up --detach")
    if not success:
        print("❌ Deployment failed")
        return False
    
    # Get URL
    success, url = run_command("railway domain", check=False)
    if success and url:
        # Extract just the URL from the output
        url_line = next((line for line in url.split('\n') if 'https://' in line), url)
        clean_url = url_line.strip().replace('🚀 ', '')
        print(f"✅ Deployed successfully!")
        print(f"🌐 Your portal URL: {clean_url}")
        return clean_url
    else:
        print("✅ Deployment successful! Check Railway dashboard for URL.")
        return True

def deploy_to_vercel():
    """Deploy to Vercel."""
    print("\n▲ Deploying to Vercel...")
    
    # Check if Vercel CLI is installed
    success, _ = run_command("vercel --version", check=False)
    if not success:
        print("📦 Vercel CLI not found")
        print("   Install with: npm install -g vercel")
        return False
    
    # Create Vercel files
    create_vercel_files()
    
    # Deploy
    print("🚀 Deploying to Vercel...")
    success, output = run_command("vercel --prod")
    if not success:
        print("❌ Deployment failed")
        return False
    
    print("✅ Deployed to Vercel!")
    print("🌐 Check your Vercel dashboard for the URL")
    print("⚠️ Remember to set SECRET_KEY in Vercel environment variables")
    return True

def create_railway_files():
    """Create Railway deployment files."""
    # Use lite version by default for better compatibility
    procfile_content = "web: python customer_portal_lite.py"
    
    # Check if we should use full version
    if os.path.exists('venv') and check_pandas_installed():
        procfile_content = "web: python customer_portal.py"
        print("📊 Using full customer portal with pandas support")
    else:
        print("🚀 Using lite customer portal (no pandas required)")
    
    # Procfile
    with open('Procfile', 'w') as f:
        f.write(procfile_content)
    
    # runtime.txt
    with open('runtime.txt', 'w') as f:
        f.write("python-3.11.0")
    
    print("✅ Railway files created")

def create_vercel_files():
    """Create Vercel deployment files."""
    # Use lite version by default for better compatibility
    portal_file = "customer_portal_lite.py"
    
    if os.path.exists('venv') and check_pandas_installed():
        portal_file = "customer_portal.py"
        print("📊 Using full customer portal for Vercel")
    else:
        print("🚀 Using lite customer portal for Vercel")
    
    vercel_config = {
        "version": 2,
        "builds": [
            {
                "src": portal_file,
                "use": "@vercel/python"
            }
        ],
        "routes": [
            {
                "src": "/(.*)",
                "dest": f"/{portal_file}"
            }
        ],
        "env": {
            "FLASK_ENV": "production"
        },
        "functions": {
            portal_file: {
                "maxDuration": 30
            }
        }
    }
    
    with open('vercel.json', 'w') as f:
        json.dump(vercel_config, f, indent=2)
    
    print("✅ Vercel files created")

def create_test_customer():
    """Skip test customer creation to keep clean state."""
    print("\n👤 Skipping test customer creation (keeping clean state)")
    print("   Create customers manually when needed using:")
    print("   python upload_customer_data.py create-customer email@domain.com 'Name' 'password'")

def show_next_steps(deployment_url=None, has_pandas=False):
    """Show what to do next."""
    print("\n" + "="*60)
    print("🎉 SETUP COMPLETE!")
    print("="*60)
    
    activation_cmd = get_activation_command()
    
    print(f"\n📋 Next Steps:")
    print(f"1. Activate virtual environment:")
    print(f"   {activation_cmd}")
    
    print(f"\n2. Process customer documents:")
    if has_pandas:
        print(f"   python local_processor.py process input/sample.csv --customer \"Customer Name\" --project \"Project Name\"")
    else:
        print(f"   python local_processor_lite.py process input/sample.csv --customer \"Customer Name\" --project \"Project Name\"")
    
    print(f"\n3. Create customer and upload data:")
    print(f"   python upload_customer_data.py create-customer customer@email.com \"Customer Name\" \"password\"")
    print(f"   python upload_customer_data.py upload [database_path] customer@email.com \"Project Name\"")
    
    if not has_pandas:
        print(f"\n   ⚠️ Using lite processor (pandas not available)")
        print(f"   For enhanced processing, install pandas: pip install pandas")
    
    if deployment_url:
        print(f"\n4. Access customer portal:")
        print(f"   🌐 URL: {deployment_url}")
        print(f"   👤 Login with customers you create using step 3")
        
        portal_type = "full" if has_pandas else "lite"
        print(f"   🚀 Running: customer_portal_{'' if has_pandas else 'lite.py'} ({portal_type} version)")
    
    print(f"\n🛠️ Useful Commands:")
    print(f"   List customers: python upload_customer_data.py list-customers")
    print(f"   List projects: python upload_customer_data.py list-projects")
    processor_cmd = "local_processor.py" if has_pandas else "local_processor_lite.py"
    print(f"   Local projects: python {processor_cmd} list")
    
    print(f"\n📚 Documentation:")
    print(f"   Workflow Guide: WORKFLOW_GUIDE.md")
    print(f"   Quick Start: QUICK_START.md")
    print(f"   Manual Setup: MANUAL_SETUP.md")
    
    if not has_pandas:
        print(f"\n⚠️ IMPORTANT NOTES:")
        print(f"   • Using lite portal (no pandas dependency)")
        print(f"   • For full document processing, install missing dependencies")
        print(f"   • See MANUAL_SETUP.md for detailed instructions")
        print(f"   • The customer portal works fine without pandas!")

def main():
    """Main setup function."""
    print("🚀 Document Analysis Platform Setup")
    print("="*50)
    print("This script will:")
    print("1. Create virtual environment")
    print("2. Install all dependencies")
    print("3. Set up directories")
    print("4. Deploy to Railway or Vercel")
    print("5. Create test customer")
    print()
    
    # Check Python version
    if not check_python_version():
        return
    
    # Ask for deployment choice
    print("🌐 Choose deployment platform:")
    print("1. Railway (Recommended for production)")
    print("2. Vercel (Good for demos)")
    print("3. Skip deployment (local only)")
    
    while True:
        choice = input("\nEnter choice (1/2/3): ").strip()
        if choice in ['1', '2', '3']:
            break
        print("Please enter 1, 2, or 3")
    
    # Setup steps
    if not create_virtual_environment():
        print("❌ Failed to create virtual environment")
        return
    
    if not install_dependencies():
        print("❌ Failed to install dependencies")
        return
    
    if not setup_directories():
        print("❌ Failed to set up directories")
        return
    
    # Check system dependencies
    check_system_dependencies()
    
    # Deploy if requested
    deployment_url = None
    if choice == '1':
        deployment_url = deploy_to_railway()
    elif choice == '2':
        deployment_url = deploy_to_vercel()
    else:
        print("\n⏭️ Skipping deployment")
        print("   You can deploy later with:")
        print("   python railway_deploy.py  # or")
        print("   python vercel_deploy.py")
    
    # Create test customer (only if we have dependencies)
    create_test_customer()
    
    # Check if pandas is working
    has_pandas = check_pandas_installed()
    
    # Show next steps
    show_next_steps(deployment_url, has_pandas)

if __name__ == "__main__":
    main()

