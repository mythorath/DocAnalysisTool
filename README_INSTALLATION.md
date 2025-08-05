# 🚀 Installation Guide - Public Comment Analysis Tool

## 🎯 **ONE-CLICK INSTALLATION** (Recommended)

### **Windows Users**
1. **Double-click** `INSTALL.bat` 
2. **Wait 3-5 minutes** for automatic installation
3. **Follow the setup wizard** for first-time configuration
4. **Start analyzing!** 

### **Linux/macOS Users**
1. **Run** `./INSTALL.sh` in terminal
2. **Wait 3-5 minutes** for automatic installation  
3. **Follow the setup wizard** for first-time configuration
4. **Start analyzing!**

---

## 📋 **What the Installer Does**

### ✅ **Automatic Setup**
- **Checks Python environment** (installs guidance if missing)
- **Installs all Python packages** (pandas, scikit-learn, BERTopic, etc.)
- **Downloads & configures Tesseract OCR** for text recognition
- **Downloads & configures Poppler** for PDF processing
- **Creates project directories** (input/, downloads/, text/, output/, logs/)
- **Sets up desktop shortcuts** and launchers
- **Validates installation** with comprehensive tests
- **Launches setup wizard** for first-time configuration

### 🎮 **User-Friendly Features**
- **Graphical installer** with progress tracking
- **Real-time status updates** and logging
- **Error handling** with clear solutions
- **Automatic dependency resolution**
- **Cross-platform compatibility**
- **No technical knowledge required**

---

## 🔧 **System Requirements**

### **Minimum Requirements**
- **Windows 10+ (64-bit)** | **Linux (Ubuntu 18+)** | **macOS 10.14+**
- **Python 3.8+** (installed automatically if missing)
- **4GB RAM** minimum, **8GB recommended**
- **2GB free disk space** for installation
- **Internet connection** for downloading dependencies

### **Recommended Specifications**
- **8GB+ RAM** for large document collections
- **SSD storage** for faster processing
- **Stable internet** for downloading ML models (one-time)
- **Modern CPU** for faster clustering

---

## 🚨 **Troubleshooting Installation**

### **Common Issues & Solutions**

#### **"Python not found"**
**Windows:**
1. Download Python from [python.org](https://www.python.org/downloads/)
2. **Check "Add Python to PATH"** during installation
3. Restart and run installer again

**Linux:**
```bash
sudo apt install python3 python3-pip python3-tk  # Ubuntu/Debian
sudo yum install python3 python3-pip tkinter      # CentOS/RHEL
```

**macOS:**
```bash
brew install python3  # If Homebrew installed
```

#### **"Permission denied" or "Access denied"**
**Windows:** Right-click `INSTALL.bat` → "Run as Administrator"

**Linux/macOS:** Run with sudo: `sudo ./INSTALL.sh`

#### **"Internet connection required"**
- Check firewall/antivirus settings
- Try different network if behind corporate firewall
- Disable VPN temporarily if connection issues

#### **"Insufficient disk space"**
- Free up at least 2GB disk space
- Clean temporary files: `Windows + R` → `%temp%` → Delete contents
- Move installation to different drive if needed

#### **Installation hangs or freezes**
1. **Close installer** and all Python processes
2. **Delete temp files:** Remove `temp_install/` folder if exists
3. **Restart computer** if necessary
4. **Run installer again**

#### **"Tesseract/Poppler not found"**
- Re-run installer (it will re-download)
- Check PATH environment variable
- Try manual installation (see Manual Installation below)

---

## 🔧 **Manual Installation** (Advanced Users)

If the automatic installer fails, you can install manually:

### **Step 1: Install Python Dependencies**
```bash
pip install -r requirements.txt
```

### **Step 2: Install System Dependencies**

**Windows:**
- Download Tesseract: [UB-Mannheim/tesseract](https://github.com/UB-Mannheim/tesseract/releases)
- Download Poppler: [oschwartz10612/poppler-windows](https://github.com/oschwartz10612/poppler-windows/releases)
- Add both to PATH environment variable

**Linux (Ubuntu/Debian):**
```bash
sudo apt install tesseract-ocr poppler-utils
```

**Linux (CentOS/RHEL):**
```bash
sudo yum install tesseract poppler-utils
```

**macOS:**
```bash
brew install tesseract poppler
```

### **Step 3: Create Directories**
```bash
mkdir -p input downloads text output logs
```

### **Step 4: Test Installation**
```bash
python -c "import pytesseract, pdf2image, sklearn, sentence_transformers; print('✅ All dependencies working!')"
```

---

## 🎮 **Getting Started After Installation**

### **1. Launch the Application**
- **Windows:** Double-click desktop shortcut or `shortcuts/Launch_Analysis_Tool.bat`
- **Linux/macOS:** Run `./shortcuts/Launch_Analysis_Tool.sh` or `python3 gui_app.py`
- **Direct:** `python gui_app.py`

### **2. Follow the Setup Wizard**
The setup wizard will guide you through:
- **Workspace configuration**
- **Sample data download**
- **Installation testing**
- **System validation**
- **First analysis project**

### **3. Prepare Your Data**
Create a CSV file with these columns:
- **Attachment Files** (required): URLs to PDF/DOCX files
- **Document ID** (optional): Unique identifier
- **Organization Name** (optional): Source organization
- **Category** (optional): Document category

### **4. Run Your First Analysis**
1. **Load CSV** in Download tab
2. **Download documents** automatically
3. **Extract text** with OCR
4. **Build search index** for fast searching
5. **Cluster documents** with AI
6. **Export results** and explore!

---

## 📁 **Installation Structure**

After installation, your workspace will contain:

```
your_workspace/
├── 🎮 Application Files
│   ├── gui_app.py              # Main GUI application
│   ├── main.py                 # Command-line interface
│   ├── downloader.py           # Document download module
│   ├── extractor.py            # Text extraction + OCR
│   ├── indexer.py              # Full-text search engine
│   └── grouper.py              # AI clustering module
│
├── 📁 Data Directories
│   ├── input/                  # Your CSV files
│   ├── downloads/              # Downloaded documents
│   ├── text/                   # Extracted text files
│   ├── output/                 # Results and database
│   └── logs/                   # Processing logs
│
├── 🚀 Launchers
│   ├── shortcuts/Launch_Analysis_Tool.bat  # Windows launcher
│   ├── shortcuts/Launch_Analysis_Tool.sh   # Linux/macOS launcher
│   └── INSTALL.py              # Re-run installer if needed
│
├── 📚 Documentation
│   ├── README.md               # Technical documentation
│   ├── GUI_USER_GUIDE.md       # User interface guide
│   ├── INSTALLATION.md         # This file
│   └── user_config.json        # Your saved preferences
│
└── 🔧 Configuration
    ├── requirements.txt         # Python dependencies
    └── .gitignore              # Version control settings
```

---

## 🆘 **Getting Help**

### **Built-in Help**
- **Application Help:** Menu → Help → User Guide
- **Tooltips:** Hover over buttons for context help
- **Status Bar:** Shows current operation status
- **Log Files:** Check `logs/` folder for detailed information

### **Documentation**
- **User Guide:** `GUI_USER_GUIDE.md` - Complete workflow guide
- **README:** `README.md` - Technical documentation  
- **This Guide:** `README_INSTALLATION.md` - Installation help

### **Self-Diagnosis**
1. **Run setup wizard again:** `python setup_wizard.py`
2. **Check logs:** Look in `logs/` folder for error details
3. **Validate installation:** Use Help → System Validation in GUI
4. **Re-run installer:** Execute `INSTALL.py` again

### **Uninstallation**
1. **Close application** if running
2. **Delete workspace folder** (contains all project files)
3. **Remove shortcuts** from desktop/start menu
4. **Uninstall Python packages** (optional): `pip uninstall -r requirements.txt`

---

## ✅ **Installation Success Checklist**

After installation, you should have:

- ✅ **GUI launches** without errors
- ✅ **All tabs accessible** (Download, Extract, Search, Cluster, Results)
- ✅ **File dialogs work** (can browse for CSV files)
- ✅ **Sample data processed** successfully (if using setup wizard)
- ✅ **Search functionality** working (can build index and search)
- ✅ **Clustering methods** available (BERTopic, TF-IDF, LDA)
- ✅ **Export features** functional (can open output folder)
- ✅ **Shortcuts created** (desktop/start menu launchers)

**If any item fails, re-run the installer or check troubleshooting section above.**

---

## 🎉 **Ready to Analyze!**

Your installation is complete! The Public Comment Analysis Tool is now ready to help you:

- 📥 **Download** thousands of documents automatically
- 📝 **Extract** text from PDFs and Word documents with OCR
- 🔍 **Search** your entire collection instantly
- 🎯 **Cluster** similar documents with AI
- 📊 **Export** professional reports and visualizations

**Happy analyzing! 🚀**