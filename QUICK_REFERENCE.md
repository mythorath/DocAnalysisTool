# 📋 Quick Reference Guide
**Document Processing & Customer Portal System**

## 🚀 Getting Started

### First Time Setup
```bash
# Option 1: Automated setup (recommended)
python setup.py

# Option 2: Manual setup
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### GPU Support Setup (Optional - for RTX 3080 Ti)
```bash
# Install GPU dependencies
python install_gpu_support.py

# Test GPU functionality
python gpu_enhanced_processor.py test_document.pdf
```

---

## 🔄 Daily Workflow

### 1. Process Customer Documents
```bash
# Activate environment
venv\Scripts\activate

# Process with standard extraction
python local_processor_lite.py process input/sample.csv --customer "Customer Name" --project "Project Name"

# Process with GPU acceleration (RTX 3080 Ti)
python local_processor_lite.py process input/sample.csv --customer "Customer Name" --project "Project Name" --gpu
```

### 2. Upload to Customer Portal
```bash
# Upload processed database
python upload_customer_data.py upload "path/to/database.db" customer@email.com "Project Name"

# Create new customer first (if needed)
python upload_customer_data.py create-customer customer@email.com "Customer Name" "password123" --organization "Company Name"
```

### 3. Start Local Portal (for testing)
```bash
# Run customer portal locally
python customer_portal_lite.py
# Access at: http://localhost:5000
```

---

## 🌐 Deployment Commands

### Deploy to Railway
```bash
# Deploy current version
railway up

# Check deployment status
railway status

# View logs
railway logs

# Open deployed site
railway open
```

### Deploy to Vercel (Alternative)
```bash
# Deploy to Vercel
vercel --prod

# Check status
vercel ls
```

---

## 🗂️ Data Management

### Local Data Management
```bash
# See all customers, projects, and storage usage
python data_manager.py list

# Remove entire customer and all their data
python data_manager.py remove-customer customer@example.com

# Remove specific project only
python data_manager.py remove-project customer@example.com "Project Name"

# Clean up orphaned files
python data_manager.py cleanup

# Export customer data to JSON
python data_manager.py export
```

### Remote Data Management (Deployed Site)

**⚡ Quick Setup (Choose one method):**

```bash
# Method 1: Run setup script (EASIEST)
python setup_remote_access.py

# Method 2: Set environment variables permanently
set PORTAL_URL=https://narrow-clocks-production.up.railway.app
set ADMIN_API_KEY=secure_admin_key_2024_changeme

# Method 3: Use parameters each time (no setup needed)
python remote_data_manager.py --url https://narrow-clocks-production.up.railway.app --key secure_admin_key_2024_changeme test
```

**🌐 Daily Operations:**

```bash
# Test connection to deployed portal
python remote_data_manager.py test

# Push new database to deployed site (NO REDEPLOY NEEDED!)
python remote_data_manager.py upload "path/to/database.db" customer@email.com "Project Name"

# List all data on deployed site
python remote_data_manager.py list

# Remove project from deployed site
python remote_data_manager.py remove-project customer@email.com "Project Name"

# Remove customer from deployed site
python remote_data_manager.py remove-customer customer@email.com

# Sync all local databases to deployed site
python remote_data_manager.py sync
```

---

## 🔍 Search & Browse Local Data

### Local Database Operations
```bash
# List local projects
python local_processor_lite.py list

# Search in local database
python local_processor_lite.py search "path/to/database.db" "search query"

# Test search functionality
python upload_customer_data.py test-search "database.db" "medicare"
```

---

## 🛠️ Maintenance & Troubleshooting

### Check System Status
```bash
# Test all dependencies
python -c "import torch, easyocr; print('GPU:', torch.cuda.is_available())"

# Check GPU memory
python -c "import torch; print(f'GPU Memory: {torch.cuda.get_device_properties(0).total_memory/1e9:.1f}GB')" 2>/dev/null || echo "No GPU detected"

# Verify OCR
python -c "import pytesseract; print('Tesseract version:', pytesseract.get_tesseract_version())" 2>/dev/null || echo "Tesseract not found"
```

### Clean Up System
```bash
# Remove temporary files
rmdir /s /q temp_install 2>nul || rm -rf temp_install
rmdir /s /q __pycache__ 2>nul || rm -rf __pycache__
del *.log 2>nul || rm -f *.log

# Clean up workspace downloads
del workspace\downloads\*.* 2>nul || rm -f workspace/downloads/*
```

### Reset Environment
```bash
# Remove and recreate virtual environment
rmdir /s /q venv 2>nul || rm -rf venv
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

---

## 📁 File Structure Reference

```
Upwork/
├── 📄 local_processor_lite.py      # Main processing tool
├── 📄 customer_portal_lite.py      # Web portal
├── 📄 upload_customer_data.py      # Data upload tool
├── 📄 data_manager.py              # Data management
├── 📄 gpu_enhanced_processor.py    # GPU processing
├── 📄 setup.py                     # Automated setup
├── 📄 install_gpu_support.py       # GPU setup
├── 📄 requirements.txt             # Dependencies
├── 📄 Procfile                     # Railway config
├── 📂 input/                       # CSV files
│   └── sample.csv
├── 📂 workspace/                   # Local processing
│   ├── customers/
│   ├── downloads/
│   ├── text/
│   └── output/
├── 📂 admin_data/                  # Portal database
│   └── customers.db
├── 📂 customer_databases/          # Customer data
├── 📂 templates/                   # Web templates
└── 📂 venv/                       # Python environment
```

---

## 🎯 Interactive Manager (EASIEST WAY)

### 🚀 One-Click Start
```bash
# Windows
start.bat

# Linux/Mac  
./start.sh

# Or manually
python interactive_manager.py
```

**Features:**
- ✅ **All commands in one place** - no need to remember syntax
- ✅ **File selection menus** - choose from available files
- ✅ **Step-by-step guidance** - prompts for all required info
- ✅ **Real-time feedback** - see command results immediately
- ✅ **Safe operations** - confirmation prompts for destructive actions

## ⚡ Quick Commands Cheat Sheet

| Task | Interactive Manager | Command |
|------|---------------------|---------|
| **Start interactive UI** | *Just run start.bat* | `python interactive_manager.py` |
| **Start processing** | *Document Processing menu* | `venv\Scripts\activate` |
| **Process documents** | `python local_processor_lite.py process input/sample.csv --customer "Name" --project "Project"` |
| **With GPU** | `...same command... --gpu` |
| **Upload to portal** | `python upload_customer_data.py upload "db_path" email@domain.com "Project"` |
| **Create customer** | `python upload_customer_data.py create-customer email name password` |
| **Run portal locally** | `python customer_portal_lite.py` |
| **Deploy to cloud** | `railway up` |
| **Push to deployed site** | `python remote_data_manager.py upload "db_path" email "Project"` |
| **List remote data** | `python remote_data_manager.py list` |
| **List local data** | `python data_manager.py list` |
| **Remove from site** | `python remote_data_manager.py remove-project email "Project"` |
| **Clean orphaned files** | `python data_manager.py cleanup` |
| **Check GPU status** | `python install_gpu_support.py` |

---

## 🚨 Common Issues & Solutions

### "Module not found" errors
```bash
# Ensure virtual environment is activated
venv\Scripts\activate

# Reinstall dependencies
pip install -r requirements.txt
```

### GPU not working
```bash
# Reinstall GPU support
python install_gpu_support.py

# Check NVIDIA drivers
nvidia-smi
```

### Portal not accessible
```bash
# Check if running
python customer_portal_lite.py

# For Railway deployment
railway logs
railway open
```

### Unicode/Emoji errors (Windows)
- Fixed in latest version
- Use `[IMAGE]` instead of 📷 in logs
- Ensure UTF-8 encoding in file handlers

### Database corruption
```bash
# Check database integrity
python data_manager.py list

# Remove corrupted projects
python data_manager.py remove-project email "Project Name"

# Clean up orphaned files
python data_manager.py cleanup
```

---

## 📞 Workflow Examples

### Complete New Customer Workflow
```bash
# 1. Activate environment
venv\Scripts\activate

# 2. Process their documents
python local_processor_lite.py process input/customer_docs.csv --customer "ABC Corp" --project "Q1 2025 Analysis" --gpu

# 3. Create customer account
python upload_customer_data.py create-customer contact@abccorp.com "ABC Corporation" "secure_password" --organization "ABC Corp"

# 4. Upload processed data
python upload_customer_data.py upload "workspace/customers/abc_corp/abc_corp_20250106_143022/output/abc_corp_20250106_143022.db" contact@abccorp.com "Q1 2025 Analysis"

# 5. Deploy updates (if needed)
railway up
```

### Monthly Maintenance
```bash
# 1. Check system status
python data_manager.py list

# 2. Clean up old data
python data_manager.py cleanup

# 3. Export backup
python data_manager.py export

# 4. Check deployments
railway status
```

---

## 🔗 Access URLs

- **Local Portal**: http://localhost:5000
- **Railway Portal**: https://your-app-name.railway.app
- **Railway Dashboard**: https://railway.app/dashboard

---

*💡 Tip: Keep this reference handy and bookmark the URLs for quick access!*
