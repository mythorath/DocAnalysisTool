# 🛠️ Manual Setup Guide

If the automated setup script fails (especially on Windows with pandas compilation issues), here's how to set everything up manually:

## 🎯 Quick Manual Setup

### **1. Create Virtual Environment**
```bash
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Linux/macOS)
source venv/bin/activate
```

### **2. Install Minimal Dependencies**
```bash
# Essential packages only (these ALWAYS work)
pip install Flask>=2.3.0
pip install Werkzeug>=2.3.0
pip install requests>=2.31.0
pip install python-dotenv>=1.0.0

# Try to install pandas (for enhanced features)
pip install pandas
# If pandas fails, no problem - lite versions work without it!

# Optional: Document processing (install what you can)
pip install PyMuPDF>=1.20.0  # For PDF text extraction
pip install python-docx>=0.8.0  # For DOCX files
```

### **3. Set Up Directories**
```bash
mkdir -p workspace/customers
mkdir -p workspace/downloads
mkdir -p workspace/text  
mkdir -p workspace/output
mkdir -p workspace/logs
mkdir -p portal_data/databases
mkdir -p portal_data/admin
mkdir -p input
```

### **4. Create Sample Data**
Create `input/sample_comment_links.csv`:
```csv
Document ID,URL,Organization,Category
TEST-001,https://example.com/doc1.pdf,Test Organization,Test Category
TEST-002,https://example.com/doc2.pdf,Another Org,Sample Category
```

### **5. Deploy Customer Portal**

#### **Option A: Railway (Recommended)**
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and create project
railway login
railway create document-analysis-portal

# Create Procfile
echo "web: python customer_portal_lite.py" > Procfile

# Set environment variables
railway env set FLASK_ENV="production"
railway env set SECRET_KEY="your-secret-key-here"
railway env set PORT="8080"
railway env set HOST="0.0.0.0"

# Deploy
railway deploy

# Get URL
railway url
```

#### **Option B: Vercel**
```bash
# Install Vercel CLI
npm install -g vercel

# Create vercel.json
```
Create `vercel.json`:
```json
{
  "version": 2,
  "builds": [
    {
      "src": "customer_portal_lite.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "/customer_portal_lite.py"
    }
  ],
  "env": {
    "FLASK_ENV": "production"
  },
  "functions": {
    "customer_portal_lite.py": {
      "maxDuration": 30
    }
  }
}
```

```bash
# Deploy
vercel --prod

# Set SECRET_KEY in Vercel dashboard
```

### **6. Test Local Setup**
```bash
# Test customer portal locally (always works)
python customer_portal_lite.py
# Should start on http://localhost:5000

# Test local processing (works with minimal dependencies)
python local_processor_lite.py process input/sample_comment_links.csv --customer "Test Customer" --project "Sample Project"

# List processed projects
python local_processor_lite.py list
```

## 🔧 Local Processing Setup

### **Full vs Lite Versions**

**✅ LITE VERSIONS (Always Work):**
- `customer_portal_lite.py` - Customer portal without pandas
- `local_processor_lite.py` - Document processing with minimal dependencies

**🚀 FULL VERSIONS (Need More Dependencies):**
- `customer_portal.py` - Enhanced portal with pandas support
- `local_processor.py` - Full processing with advanced features

### **Optional Processing Dependencies**
```bash
# Advanced document processing (install if you want enhanced features)
pip install PyMuPDF>=1.20.0      # PDF text extraction
pip install pdf2image>=3.0.0     # PDF to image conversion
pip install pytesseract>=0.3.0   # OCR for scanned PDFs
pip install Pillow>=9.0.0        # Image processing
pip install python-docx>=0.8.0   # DOCX file support
pip install scikit-learn>=1.2.0  # Document clustering
pip install nltk>=3.8            # Text processing

# Skip any that fail - lite versions work without them!
```

### **System Dependencies**
For OCR processing, install:
- **Tesseract OCR**: https://github.com/UB-Mannheim/tesseract/wiki
- **Poppler**: https://blog.alivate.com.au/poppler-windows/

Or with conda:
```bash
conda install tesseract poppler -c conda-forge
```

## 📋 Your Workflow After Setup

### **1. Create Customer Account**
```bash
python upload_customer_data.py create-customer john@company.com "John Smith" "password123" --organization "ABC Corp"
```

### **2. Process Customer Data Locally**
```bash
# ALWAYS WORKS: Lite processor (minimal dependencies)
python local_processor_lite.py process customer_data.csv --customer "John Smith" --project "Analysis"

# OR: Full processor (if you have pandas and other dependencies)
python local_processor.py process customer_data.csv --customer "John Smith" --project "Analysis"

# This creates: workspace/customers/john_smith/[timestamp]/output/[database].db
```

### **3. Upload to Customer Portal**
```bash
python upload_customer_data.py upload "path/to/database.db" john@company.com "Analysis Project"
```

### **4. Customer Accesses Data**
- Customer visits your deployed portal URL
- Logs in with their credentials
- Searches and exports their processed documents

## 🚨 Troubleshooting

### **Pandas Compilation Fails**
- Use `customer_portal_lite.py` instead (no pandas required)
- The lite version has manual CSV export without pandas dependency

### **OCR Dependencies Missing**
- Local processing will work but skip OCR for scanned PDFs
- Install Tesseract manually when ready for full OCR support

### **Deployment Issues**
- **Railway**: Make sure Railway CLI is installed: `npm install -g @railway/cli`
- **Vercel**: Make sure Vercel CLI is installed: `npm install -g vercel`
- **Environment variables**: Set SECRET_KEY in platform dashboard

### **Permission Errors**
- **Windows**: Run command prompt as Administrator
- **Linux/macOS**: Use `sudo` if needed for global installs

### **Import Errors**
- Make sure virtual environment is activated
- Try installing packages one by one to identify issues

## 🎯 Minimal Working Setup

**✅ GUARANTEED TO WORK (even on Windows with compilation issues):**
1. Virtual environment with just Flask, Werkzeug, requests, python-dotenv
2. `customer_portal_lite.py` running locally and deployed
3. `local_processor_lite.py` for document processing (no pandas required)
4. SQLite database for search (built-in to Python)

**🚀 ENHANCED SETUP (if dependencies install successfully):**
1. Full versions with pandas, PyMuPDF, advanced clustering
2. OCR support with Tesseract
3. Advanced document analysis features

**Everything can be added incrementally - start with lite versions!**

## 📞 If You're Still Stuck

1. **Use the lite versions** - they're designed to work with minimal dependencies
2. **Skip optional features** - focus on getting the basic portal working first  
3. **Install dependencies gradually** - add OCR and ML features later
4. **Test locally first** - make sure everything works before deploying

The beauty of this setup is that the customer portal works with just Flask, and you can add processing capabilities incrementally! 🎉
