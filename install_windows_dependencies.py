#!/usr/bin/env python3
"""
Windows Dependency Installer for Public Comment Analysis Tool

This script provides alternative installation methods for Windows users
when conda installation hangs or fails.
"""

import os
import sys
import subprocess
import urllib.request
import zipfile
import shutil
from pathlib import Path


def check_admin():
    """Check if running as administrator."""
    try:
        return os.getuid() == 0
    except AttributeError:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin() != 0


def install_with_chocolatey():
    """Install dependencies using Chocolatey package manager."""
    print("Attempting installation with Chocolatey...")
    
    # Check if chocolatey is installed
    try:
        result = subprocess.run(['choco', '--version'], capture_output=True, text=True)
        if result.returncode != 0:
            print("Chocolatey not found. Install from: https://chocolatey.org/install")
            return False
    except FileNotFoundError:
        print("Chocolatey not found. Install from: https://chocolatey.org/install")
        return False
    
    try:
        # Install Tesseract
        print("Installing Tesseract OCR...")
        subprocess.run(['choco', 'install', 'tesseract', '-y'], check=True)
        
        # Install Poppler
        print("Installing Poppler...")
        subprocess.run(['choco', 'install', 'poppler', '-y'], check=True)
        
        print("✅ Successfully installed dependencies with Chocolatey!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Chocolatey installation failed: {e}")
        return False


def install_with_scoop():
    """Install dependencies using Scoop package manager."""
    print("Attempting installation with Scoop...")
    
    # Check if scoop is installed
    try:
        result = subprocess.run(['scoop', '--version'], capture_output=True, text=True)
        if result.returncode != 0:
            print("Scoop not found. Install with: Set-ExecutionPolicy RemoteSigned -Scope CurrentUser; irm get.scoop.sh | iex")
            return False
    except FileNotFoundError:
        print("Scoop not found. Install with: Set-ExecutionPolicy RemoteSigned -Scope CurrentUser; irm get.scoop.sh | iex")
        return False
    
    try:
        # Add extras bucket for tesseract
        subprocess.run(['scoop', 'bucket', 'add', 'extras'], check=True)
        
        # Install Tesseract
        print("Installing Tesseract OCR...")
        subprocess.run(['scoop', 'install', 'tesseract'], check=True)
        
        # Install Poppler
        print("Installing Poppler...")
        subprocess.run(['scoop', 'install', 'poppler'], check=True)
        
        print("✅ Successfully installed dependencies with Scoop!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Scoop installation failed: {e}")
        return False


def download_and_extract(url, extract_to, description):
    """Download and extract a zip file."""
    print(f"Downloading {description}...")
    
    try:
        # Create temp directory
        temp_dir = Path.home() / "Downloads" / "temp_install"
        temp_dir.mkdir(exist_ok=True)
        
        # Download file
        zip_path = temp_dir / "download.zip"
        urllib.request.urlretrieve(url, zip_path)
        
        # Extract
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
        
        # Cleanup
        zip_path.unlink()
        
        print(f"✅ Downloaded and extracted {description} to {extract_to}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to download {description}: {e}")
        return False


def manual_install():
    """Manual installation by downloading binaries."""
    print("Attempting manual installation...")
    
    # Create local bin directory
    local_bin = Path.home() / "AppData" / "Local" / "bin"
    local_bin.mkdir(exist_ok=True)
    
    success = True
    
    # Install Tesseract
    print("\n📦 Installing Tesseract OCR...")
    tesseract_url = "https://github.com/UB-Mannheim/tesseract/releases/download/v5.3.3.20231005/tesseract-ocr-w64-setup-5.3.3.20231005.exe"
    print(f"Please download and install Tesseract from:")
    print(f"  {tesseract_url}")
    print("  Or visit: https://github.com/UB-Mannheim/tesseract/wiki")
    
    # Install Poppler
    print("\n📦 Installing Poppler...")
    poppler_url = "https://github.com/oschwartz10612/poppler-windows/releases/download/v23.11.0-0/Release-23.11.0-0.zip"
    
    if download_and_extract(poppler_url, local_bin, "Poppler"):
        # Add to PATH instructions
        print(f"\n⚠️  IMPORTANT: Add this to your PATH environment variable:")
        print(f"  {local_bin / 'poppler-23.11.0' / 'Library' / 'bin'}")
    else:
        success = False
    
    return success


def test_installations():
    """Test if installations are working."""
    print("\n🧪 Testing installations...")
    
    # Test Tesseract
    try:
        result = subprocess.run(['tesseract', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Tesseract is working!")
            print(f"   Version: {result.stdout.split()[1]}")
        else:
            print("❌ Tesseract test failed")
            return False
    except FileNotFoundError:
        print("❌ Tesseract not found in PATH")
        return False
    
    # Test Poppler (pdf2image)
    try:
        import pdf2image
        print("✅ pdf2image (Poppler) is working!")
    except ImportError:
        print("❌ pdf2image not installed")
        return False
    except Exception as e:
        print(f"❌ pdf2image test failed: {e}")
        return False
    
    return True


def show_path_instructions():
    """Show instructions for adding to PATH."""
    print("\n📋 PATH Configuration Instructions:")
    print("=" * 50)
    print("1. Press Windows + R, type 'sysdm.cpl', press Enter")
    print("2. Click 'Environment Variables' button")
    print("3. Under 'System Variables', find and select 'Path', click 'Edit'")
    print("4. Click 'New' and add these paths:")
    print("   - C:\\Program Files\\Tesseract-OCR")
    print("   - Your Poppler installation path (see above)")
    print("5. Click OK on all dialogs")
    print("6. Restart your terminal/command prompt")
    print("7. Test with: tesseract --version")


def main():
    """Main installation function."""
    print("🔧 Windows Dependencies Installer for Public Comment Analysis Tool")
    print("=" * 70)
    
    print("\nThis script will try multiple methods to install:")
    print("  - Tesseract OCR (for PDF text extraction)")
    print("  - Poppler (for PDF to image conversion)")
    
    # Try different installation methods
    methods = [
        ("Chocolatey", install_with_chocolatey),
        ("Scoop", install_with_scoop),
        ("Manual Download", manual_install)
    ]
    
    for method_name, method_func in methods:
        print(f"\n🚀 Trying {method_name}...")
        try:
            if method_func():
                print(f"✅ {method_name} installation completed!")
                break
        except Exception as e:
            print(f"❌ {method_name} failed: {e}")
            continue
    else:
        print("\n❌ All automatic installation methods failed.")
        print("Please try manual installation:")
        print("  1. Tesseract: https://github.com/UB-Mannheim/tesseract/wiki")
        print("  2. Poppler: https://blog.alivate.com.au/poppler-windows/")
        show_path_instructions()
        return False
    
    # Test installations
    if test_installations():
        print("\n🎉 All dependencies are working correctly!")
        print("You can now run the Public Comment Analysis Tool.")
        return True
    else:
        print("\n⚠️  Installation completed but tests failed.")
        print("You may need to restart your terminal or check PATH configuration.")
        show_path_instructions()
        return False


if __name__ == "__main__":
    main()