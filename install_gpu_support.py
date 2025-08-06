#!/usr/bin/env python3
"""
GPU Support Installation Script
Installs CUDA-enabled PyTorch and EasyOCR for RTX 3080 Ti acceleration.
"""

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
                   .replace('🗑️', '[DELETE]')
                   .replace('📁', '[FILES]')
                   .replace('🗂️', '[FOLDER]')
                   .replace('💡', '[TIP]')
                   .replace('🚀', '[START]')
                   .replace('📍', '[LOCATION]')
                   .replace('🕒', '[TIME]')
                   .replace('🌐', '[WEB]')
                   .replace('⚙️', '[SYSTEM]')
                   .replace('📚', '[HELP]')
                   .replace('🚪', '[EXIT]')
                   .replace('🔧', '[TOOL]')
                   .replace('💻', '[CMD]')
                   .replace('📤', '[UPLOAD]')
                   .replace('❓', '[QUESTION]')
                   .replace('🎉', '[SUCCESS]')
                   .replace('📂', '[FOLDER]')
                   .replace('📈', '[COUNT]')
                   .replace('🧹', '[CLEANUP]')
                   .replace('⬅️', '[BACK]')
                   .replace('🔥', '[PROCESS]')
                   .replace('🔍', '[SEARCH]')
                   .replace('📎', '[LINK]')
                   .replace('📥', '[DOWNLOAD]')
                   .replace('📝', '[EXTRACT]'))
    try:
        print(text)
    except UnicodeEncodeError:
        # Final fallback - remove all non-ASCII characters
        print(text.encode('ascii', 'ignore').decode('ascii'))



import os
import sys
import subprocess
import platform

def run_command(command, description):
    """Run a command and handle errors."""
    safe_print(f"🔧 {description}...")
    print(f"   Running: {command}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        safe_print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        safe_print(f"❌ {description} failed")
        print(f"   Error: {e.stderr}")
        return False

def detect_gpu():
    """Detect if NVIDIA GPU is available."""
    try:
        result = subprocess.run("nvidia-smi", shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            safe_print("🚀 NVIDIA GPU detected!")
            # Extract GPU info
            lines = result.stdout.split('\n')
            for line in lines:
                if 'GeForce' in line or 'RTX' in line or 'GTX' in line:
                    gpu_info = line.strip()
                    print(f"   GPU: {gpu_info}")
                    break
            return True
        else:
            safe_print("⚠️ NVIDIA GPU not detected or drivers not installed")
            return False
    except FileNotFoundError:
        safe_print("⚠️ nvidia-smi not found - NVIDIA drivers may not be installed")
        return False

def check_package_installed(package_name, import_name=None):
    """Check if a package is already installed."""
    if import_name is None:
        import_name = package_name
    
    try:
        __import__(import_name)
        return True
    except ImportError:
        return False

def install_pytorch_cuda():
    """Install PyTorch with CUDA support."""
    safe_print("\n📦 Checking PyTorch installation...")
    
    # Check if PyTorch is already installed
    if check_package_installed("torch"):
        try:
            import torch
            if torch.cuda.is_available():
                safe_print(f"✅ PyTorch {torch.__version__} with CUDA {torch.version.cuda} already installed")
                return True
            else:
                safe_print("⚠️ PyTorch installed but CUDA not available, reinstalling...")
        except:
            safe_print("⚠️ PyTorch installation issues, reinstalling...")
    else:
        safe_print("📦 PyTorch not found, installing...")
    
    # Use CUDA 11.8 for broad compatibility
    pytorch_command = "pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118"
    
    return run_command(pytorch_command, "PyTorch CUDA installation")

def install_easyocr():
    """Install EasyOCR for GPU-accelerated OCR."""
    safe_print("\n📦 Checking EasyOCR installation...")
    
    # Check if EasyOCR is already installed
    if check_package_installed("easyocr"):
        try:
            import easyocr
            safe_print(f"✅ EasyOCR already installed")
            # Test GPU functionality
            reader = easyocr.Reader(['en'], gpu=True)
            safe_print("✅ EasyOCR GPU test successful")
            return True
        except Exception as e:
            safe_print(f"⚠️ EasyOCR installed but GPU test failed: {e}")
            print("   Reinstalling...")
    else:
        safe_print("📦 EasyOCR not found, installing...")
    
    easyocr_command = "pip install easyocr"
    
    return run_command(easyocr_command, "EasyOCR installation")

def install_additional_deps():
    """Install additional GPU processing dependencies."""
    safe_print("\n📦 Checking additional dependencies...")
    
    deps = [
        ("opencv-python", "cv2"),  # For image processing
        ("scikit-image", "skimage"),   # For advanced image operations
    ]
    
    success = True
    for package_name, import_name in deps:
        if check_package_installed(package_name, import_name):
            safe_print(f"✅ {package_name} already installed")
        else:
            safe_print(f"📦 Installing {package_name}...")
            if not run_command(f"pip install {package_name}", f"Installing {package_name}"):
                success = False
    
    return success

def test_gpu_setup():
    """Test if GPU setup is working."""
    print("\n🧪 Testing GPU setup...")
    
    test_script = '''
import torch
import easyocr

safe_print("🔧 PyTorch version:", torch.__version__)
safe_print("🔧 CUDA available:", torch.cuda.is_available())

if torch.cuda.is_available():
    safe_print("🔧 CUDA version:", torch.version.cuda)
    safe_print("🔧 GPU device:", torch.cuda.get_device_name(0))
    safe_print("🔧 GPU memory:", f"{torch.cuda.get_device_properties(0).total_memory / 1e9:.1f}GB")
    
    try:
        reader = easyocr.Reader(['en'], gpu=True)
        safe_print("✅ EasyOCR GPU initialization successful")
    except Exception as e:
        safe_print("❌ EasyOCR GPU initialization failed:", e)
else:
    safe_print("❌ CUDA not available")
'''
    
    try:
        with open("test_gpu_temp.py", "w") as f:
            f.write(test_script)
        
        result = subprocess.run([sys.executable, "test_gpu_temp.py"], 
                              capture_output=True, text=True)
        
        print(result.stdout)
        if result.stderr:
            print("Warnings/Errors:", result.stderr)
        
        # Clean up
        os.unlink("test_gpu_temp.py")
        
        return "GPU initialization successful" in result.stdout
        
    except Exception as e:
        safe_print(f"❌ GPU test failed: {e}")
        return False

def main():
    """Main installation process."""
    safe_print("🚀 GPU Support Installation for Document Processing")
    print("=" * 60)
    print("This script will install CUDA-enabled PyTorch and EasyOCR")
    print("for GPU-accelerated document processing on your RTX 3080 Ti.")
    print()
    
    # Check Python version
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
        safe_print("❌ Python 3.8+ required for GPU support")
        sys.exit(1)
    
    safe_print(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # Detect GPU
    if not detect_gpu():
        response = input("\n⚠️ GPU not detected. Continue anyway? (y/N): ")
        if response.lower() != 'y':
            print("Installation cancelled.")
            sys.exit(1)
    
    safe_print(f"\n🖥️ Platform: {platform.system()} {platform.release()}")
    
    # Quick check if everything is already installed
    safe_print("\n🔍 Checking current installation status...")
    
    all_installed = True
    try:
        import torch
        import easyocr
        if torch.cuda.is_available():
            reader = easyocr.Reader(['en'], gpu=True)
            safe_print("✅ All GPU dependencies are already installed and working!")
            
            response = input("\nEverything appears to be working. Run full check anyway? (y/N): ")
            if response.lower() != 'y':
                safe_print("✅ GPU support is ready to use!")
                safe_print("\n💡 Usage: python local_processor_lite.py process input/sample.csv --customer 'Customer' --project 'Project' --gpu")
                return
        else:
            all_installed = False
    except:
        all_installed = False
    
    if not all_installed:
        # Confirm installation
        safe_print("\n📋 Installation Plan:")
        print("   1. PyTorch with CUDA 11.8 support")
        print("   2. EasyOCR for GPU-accelerated OCR")
        print("   3. Additional image processing libraries")
        print("   4. Test GPU functionality")
        
        response = input("\nProceed with installation? (y/N): ")
        if response.lower() != 'y':
            print("Installation cancelled.")
            sys.exit(0)
    
    # Installation process
    success = True
    
    # Step 1: Install PyTorch with CUDA
    if not install_pytorch_cuda():
        success = False
    
    # Step 2: Install EasyOCR
    if success and not install_easyocr():
        success = False
    
    # Step 3: Install additional dependencies
    if success and not install_additional_deps():
        success = False
    
    # Step 4: Test setup
    if success:
        if test_gpu_setup():
            safe_print("\n🎉 GPU support installation completed successfully!")
            safe_print("\n📋 Usage:")
            print("   python local_processor_lite.py process input/sample.csv --customer 'Customer' --project 'Project' --gpu")
            safe_print("\n💡 The --gpu flag will enable RTX 3080 Ti acceleration for:")
            print("   • Advanced OCR for scanned PDFs and images")
            print("   • Enhanced image preprocessing")
            print("   • Faster text extraction from complex documents")
        else:
            safe_print("\n⚠️ Installation completed but GPU test failed")
            print("   You can still use CPU-based processing")
    else:
        safe_print("\n❌ Installation failed")
        print("   Check error messages above and try manual installation:")
        print("   pip install -r requirements_gpu.txt")

if __name__ == "__main__":
    main()
