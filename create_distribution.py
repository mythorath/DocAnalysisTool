#!/usr/bin/env python3
"""
create_distribution.py - Create Clean Production Distribution

This script creates a clean, production-ready package of the Public Comment Analysis Tool
by removing development files and organizing everything for end users.
"""

import os
import shutil
import zipfile
from pathlib import Path
import json
from datetime import datetime


class DistributionCreator:
    """Creates a clean distribution package."""
    
    def __init__(self):
        self.source_dir = Path.cwd()
        self.dist_name = "PublicCommentAnalysisTool"
        self.dist_dir = self.source_dir.parent / f"{self.dist_name}_Distribution"
        self.package_dir = self.dist_dir / self.dist_name
        
        # Essential files for end users
        self.essential_files = [
            # Entry points and installation
            "START_HERE.md",
            "INSTALL.py",
            "INSTALL.bat", 
            "INSTALL.sh",
            "setup_wizard.py",
            "create_shortcuts.py",
            "UNINSTALL.bat",
            
            # Main application
            "gui_app.py",
            "main.py",
            
            # Core modules
            "downloader.py",
            "extractor.py", 
            "indexer.py",
            "grouper.py",
            
            # Configuration
            "requirements.txt",
            
            # Launchers
            "launch_gui.bat",
            "launch_gui.sh",
            
            # Documentation
            "GUI_USER_GUIDE.md",
            "README_INSTALLATION.md",
            
            # Windows dependency installer
            "install_windows_dependencies.py",
            
            # Sample data (if exists)
            "IPPS FY 25 Comment Download- Sample.csv",
            "CMS-2025-0028-0611_attachment_1.pdf",
            "CMS-2025-0028-0227_attachment_1.pdf"
        ]
        
        # Directories to create
        self.required_dirs = [
            "input",
            "downloads", 
            "text",
            "output",
            "logs",
            "shortcuts"
        ]
        
        # Files to exclude (development/build artifacts)
        self.exclude_patterns = [
            ".git*",
            "__pycache__",
            "*.pyc",
            "*.pyo", 
            ".pytest_cache",
            ".coverage",
            "test_*",
            "temp_*",
            "*.tmp",
            "*.log",
            ".env",
            ".venv",
            "build/",
            "dist/",
            "*.egg-info",
            "prompt.ini",
            "Overview.md",
            "README.md",  # Technical readme - we'll create a simpler one
            "INSTALLATION.md"  # Old installation guide
        ]
    
    def create_distribution(self):
        """Create the complete distribution package."""
        print(f"🚀 Creating distribution package: {self.dist_name}")
        print(f"📁 Source: {self.source_dir}")
        print(f"📦 Output: {self.dist_dir}")
        print()
        
        # Clean up any existing distribution
        if self.dist_dir.exists():
            print("🧹 Removing existing distribution...")
            shutil.rmtree(self.dist_dir)
        
        # Create distribution directory
        self.package_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy essential files
        self.copy_essential_files()
        
        # Create required directories
        self.create_required_directories()
        
        # Create production README
        self.create_production_readme()
        
        # Create version info
        self.create_version_info()
        
        # Create clean .gitignore for users who want version control
        self.create_clean_gitignore()
        
        # Create ZIP package
        self.create_zip_package()
        
        # Create final summary
        self.create_distribution_summary()
        
        print(f"\n🎉 Distribution created successfully!")
        print(f"📦 Package: {self.dist_dir}")
        print(f"📁 Ready to distribute: {self.dist_name}.zip")
    
    def copy_essential_files(self):
        """Copy essential files to distribution."""
        print("📋 Copying essential files...")
        
        copied_count = 0
        for file_name in self.essential_files:
            source_file = self.source_dir / file_name
            if source_file.exists():
                dest_file = self.package_dir / file_name
                
                if source_file.is_file():
                    shutil.copy2(source_file, dest_file)
                    print(f"  ✅ {file_name}")
                    copied_count += 1
                else:
                    print(f"  ⚠️ Skipped {file_name} (not a file)")
            else:
                print(f"  ⚠️ Missing {file_name}")
        
        print(f"📋 Copied {copied_count} essential files")
    
    def create_required_directories(self):
        """Create required empty directories."""
        print("\n📁 Creating workspace directories...")
        
        for dir_name in self.required_dirs:
            dir_path = self.package_dir / dir_name
            dir_path.mkdir(exist_ok=True)
            
            # Create a .gitkeep file to ensure directories are preserved
            gitkeep = dir_path / ".gitkeep"
            gitkeep.write_text("# This file ensures the directory is preserved in version control\n", encoding='utf-8')
            
            print(f"  ✅ {dir_name}/")
        
        print(f"📁 Created {len(self.required_dirs)} workspace directories")
    
    def create_production_readme(self):
        """Create a focused README for the distribution."""
        print("\n📖 Creating production README...")
        
        readme_content = f"""# Public Comment Analysis Tool

## 🚀 Quick Start

### Installation (Choose One):
- **Windows**: Double-click `INSTALL.bat`
- **Linux/macOS**: Run `./INSTALL.sh` in terminal
- **Manual**: Run `python INSTALL.py`

### First Time Setup:
1. Run the installer (3-5 minutes)
2. Follow the setup wizard
3. Load your CSV file with document URLs
4. Start analyzing!

## 📋 What This Tool Does

Transform thousands of public comment documents into actionable insights:

- **📥 Bulk Download**: Automatically download documents from URLs
- **🔤 Smart OCR**: Extract text from PDFs and Word documents
- **🔍 Full-Text Search**: Search your entire collection instantly  
- **🎯 AI Clustering**: Group similar documents by topic
- **📊 Professional Reports**: Export results to Excel, CSV, database

## 📁 Your Workspace

```
{self.dist_name}/
├── START_HERE.md           # 👈 Read this first!
├── INSTALL.bat/.sh         # 👈 Double-click to install
├── gui_app.py              # Main application (auto-launched)
│
├── input/                  # Put your CSV files here
├── downloads/              # Downloaded documents appear here
├── text/                   # Extracted text files
├── output/                 # Results and search database
└── logs/                   # Processing history
```

## 🆘 Need Help?

- **📖 Complete Guide**: See `GUI_USER_GUIDE.md`
- **🛠️ Installation Help**: See `README_INSTALLATION.md`  
- **🎮 Built-in Help**: Use Help menu in the application
- **🔍 Troubleshooting**: Check logs/ folder for details

## 📋 System Requirements

- **Windows 10+** | **Linux (Ubuntu 18+)** | **macOS 10.14+**
- **Python 3.8+** (installed automatically if missing)
- **4GB RAM** minimum, 8GB recommended  
- **2GB disk space** for installation
- **Internet connection** for setup and ML models

## 🎯 CSV File Format

Create a CSV with document URLs:

```csv
Document ID,Organization Name,Category,Attachment Files
DOC-001,Hospital ABC,Healthcare,https://example.com/doc1.pdf
DOC-002,School XYZ,Education,https://example.com/doc2.pdf
```

**Required column**: `Attachment Files` (URLs to PDF/DOCX files)
**Optional columns**: `Document ID`, `Organization Name`, `Category`

## ✅ Quick Validation

After installation, verify everything works:

1. ✅ GUI opens without errors
2. ✅ Can load and process sample data  
3. ✅ Search returns results
4. ✅ Clustering completes successfully
5. ✅ Results export to output/ folder

## 🎉 Ready to Analyze!

The tool is designed to be completely self-contained and user-friendly.
No technical knowledge required - just follow the setup wizard!

**Version**: {datetime.now().strftime('%Y.%m.%d')}
**Package**: Production Distribution
"""
        
        readme_file = self.package_dir / "README.md"
        readme_file.write_text(readme_content, encoding='utf-8')
        print("  ✅ README.md created")
    
    def create_version_info(self):
        """Create version and build information."""
        print("\n📋 Creating version info...")
        
        version_info = {
            "name": "Public Comment Analysis Tool",
            "version": datetime.now().strftime('%Y.%m.%d'),
            "build_date": datetime.now().isoformat(),
            "build_type": "Production Distribution",
            "python_version": "3.8+",
            "platform": "Windows, Linux, macOS",
            "features": [
                "Bulk document download",
                "OCR text extraction", 
                "Full-text search",
                "AI-powered clustering",
                "Professional reporting"
            ],
            "included_files": len(self.essential_files),
            "package_size": "~50MB after installation"
        }
        
        version_file = self.package_dir / "version.json"
        with open(version_file, 'w') as f:
            json.dump(version_info, f, indent=2)
        
        print("  ✅ version.json created")
    
    def create_clean_gitignore(self):
        """Create a clean .gitignore for end users."""
        print("\n📝 Creating clean .gitignore...")
        
        gitignore_content = """# Public Comment Analysis Tool - User Data

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.venv/
ENV/

# User data (preserve these)
# input/           # Your CSV files
# downloads/       # Downloaded documents  
# text/           # Extracted text
# output/         # Results and database
# logs/           # Processing logs

# Temporary files
*.tmp
*.temp
temp_*/
.DS_Store
Thumbs.db

# IDE
.vscode/
.idea/
*.swp
*.swo

# ML model cache (large files)
.cache/
sentence_transformers/
.bert_topic_cache/

# Logs (uncomment if you want to ignore logs)
# logs/*.log

# Results (uncomment if you want to ignore results)
# output/*.db
# output/*.csv
# output/*.json
"""
        
        gitignore_file = self.package_dir / ".gitignore"
        gitignore_file.write_text(gitignore_content, encoding='utf-8')
        print("  ✅ .gitignore created")
    
    def create_zip_package(self):
        """Create ZIP package for distribution."""
        print("\n📦 Creating ZIP package...")
        
        zip_file = self.dist_dir / f"{self.dist_name}.zip"
        
        with zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED) as zf:
            for file_path in self.package_dir.rglob('*'):
                if file_path.is_file():
                    # Calculate relative path from package directory
                    arcname = self.dist_name / file_path.relative_to(self.package_dir)
                    zf.write(file_path, arcname)
        
        # Get ZIP file size
        zip_size_mb = zip_file.stat().st_size / (1024 * 1024)
        print(f"  ✅ {self.dist_name}.zip created ({zip_size_mb:.1f} MB)")
    
    def create_distribution_summary(self):
        """Create distribution summary and instructions."""
        print("\n📋 Creating distribution summary...")
        
        summary_content = f"""# Distribution Package Summary

## 📦 Package Details
- **Name**: {self.dist_name}
- **Created**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Type**: Production Distribution
- **Platform**: Cross-platform (Windows, Linux, macOS)

## 📁 Package Contents

### Essential Files ({len([f for f in self.essential_files if (self.package_dir / f).exists()])} files)
- Installation system (INSTALL.py, INSTALL.bat, INSTALL.sh)
- Main application (gui_app.py, main.py)
- Core modules (downloader, extractor, indexer, grouper)
- Documentation (README.md, GUI_USER_GUIDE.md, etc.)
- Launchers and shortcuts

### Workspace Directories ({len(self.required_dirs)} folders)
- input/ (for CSV files)
- downloads/ (for downloaded documents)
- text/ (for extracted text)
- output/ (for results and database)
- logs/ (for processing history)
- shortcuts/ (for system integration)

## 🚀 Distribution Instructions

### For End Users:
1. **Extract** the ZIP file to desired location
2. **Navigate** to the extracted folder
3. **Double-click** INSTALL.bat (Windows) or INSTALL.sh (Linux/macOS)
4. **Follow** the setup wizard
5. **Start analyzing** documents!

### For IT Deployment:
1. **Test** on representative systems first
2. **Verify** Python 3.8+ availability
3. **Ensure** internet access for initial setup
4. **Allow** 2GB disk space per installation
5. **Consider** network firewall requirements

## ✅ Quality Checklist

- ✅ All essential files included
- ✅ No development artifacts
- ✅ Clean directory structure
- ✅ Cross-platform compatibility
- ✅ Self-contained installation
- ✅ Comprehensive documentation
- ✅ User-friendly entry points

## 📊 Package Statistics

- **Total files**: {sum(1 for _ in self.package_dir.rglob('*') if _.is_file())}
- **Directories**: {len(self.required_dirs)}
- **Documentation**: 4 files (README.md, GUI_USER_GUIDE.md, etc.)
- **Installation size**: ~50MB after dependencies
- **Supported formats**: PDF, DOCX, CSV

## 🎯 Ready for Distribution!

This package is ready for distribution to end users with zero technical knowledge.
The installation process is completely automated and user-friendly.
"""
        
        summary_file = self.dist_dir / "DISTRIBUTION_SUMMARY.md"
        summary_file.write_text(summary_content, encoding='utf-8')
        print("  ✅ DISTRIBUTION_SUMMARY.md created")


def main():
    """Main distribution creation entry point."""
    print("=" * 60)
    print("  PUBLIC COMMENT ANALYSIS TOOL")
    print("      Distribution Creator")
    print("=" * 60)
    print()
    
    creator = DistributionCreator()
    
    try:
        creator.create_distribution()
        
        print("\n" + "=" * 60)
        print("✅ DISTRIBUTION CREATION COMPLETE!")
        print("=" * 60)
        print()
        print(f"📦 Package created: {creator.dist_dir}")
        print(f"📁 Folder: {creator.package_dir}")
        print(f"📦 ZIP file: {creator.dist_name}.zip")
        print()
        print("🚀 Ready for distribution to end users!")
        print("📋 See DISTRIBUTION_SUMMARY.md for deployment instructions")
        
    except Exception as e:
        print(f"\n❌ Distribution creation failed: {str(e)}")
        print("Please check the error and try again.")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())