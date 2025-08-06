# 🚀 One-Click Setup

## Quick Start

### **Windows**
```bash
setup.bat
```

### **Linux/macOS**
```bash
chmod +x setup.sh
./setup.sh
```

### **Any Platform**
```bash
python setup.py
```

## What It Does

The setup script will:

1. ✅ **Check Python version** (3.8+ required)
2. 📦 **Create virtual environment** (`venv/`)
3. 📥 **Install all dependencies** (Flask, pandas, ML libraries, etc.)
4. 📁 **Set up directories** (workspace, portal_data, etc.)
5. 🌐 **Deploy to Railway or Vercel** (your choice)
6. 👤 **Create test customer** (test@example.com / password123)

## Deployment Options

### **Railway (Recommended)**
- ✅ Best for production
- ✅ Persistent file storage
- ✅ Background processing support
- ✅ Easy scaling

### **Vercel**
- ✅ Good for demos
- ⚠️ Serverless limitations
- ⚠️ No persistent storage

### **Local Only**
- ✅ Skip deployment for now
- 🔧 Deploy manually later

## After Setup

### **Your Portal**
- 🌐 **URL**: Provided after deployment
- 👤 **Test Login**: test@example.com / password123

### **Local Processing**
```bash
# Activate environment
venv\Scripts\activate          # Windows
source venv/bin/activate       # Linux/macOS

# Process customer data
python local_processor.py process input/sample_comment_links.csv --customer "Test Customer" --project "Sample"

# Upload to portal
python upload_customer_data.py upload [database_path] test@example.com "Sample Project"
```

### **Management Commands**
```bash
# List customers
python upload_customer_data.py list-customers

# List projects  
python upload_customer_data.py list-projects

# List local processing
python local_processor.py list
```

## System Requirements

### **Required**
- Python 3.8+
- Internet connection for deployment

### **Optional (For OCR)**
- Tesseract OCR
- Poppler utils

### **Install OCR Dependencies**
```bash
# With conda (recommended)
conda install tesseract poppler -c conda-forge

# Or download manually:
# Tesseract: https://github.com/UB-Mannheim/tesseract/wiki
# Poppler: https://blog.alivate.com.au/poppler-windows/
```

## Troubleshooting

### **Python Not Found**
- Install Python 3.8+ from https://python.org
- Make sure it's in your PATH

### **Permission Errors**
- Run as administrator (Windows)
- Use `sudo` if needed (Linux/macOS)

### **Deployment Fails**
- Install Railway CLI: `npm install -g @railway/cli`
- Install Vercel CLI: `npm install -g vercel`

### **Dependencies Fail**
- Try updating pip: `python -m pip install --upgrade pip`
- On Linux: `sudo apt-get install python3-dev`

## What You Get

After setup completes:

### **🏠 Local Processing**
- Complete document processing pipeline
- OCR and text extraction
- Search database generation
- Customer data management

### **🌐 Customer Portal**
- Professional web interface
- Secure customer login
- Full-text search
- Data export capabilities

### **📋 Workflow**
1. Customer emails you CSV
2. You process locally
3. You upload results
4. Customer accesses via web portal
5. You get paid! 💰

## Ready to Start!

Run the setup script and you'll have a complete document analysis service ready for customers in minutes! 🎉

