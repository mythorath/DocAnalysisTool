#!/bin/bash
# One-Click Installer for Public Comment Analysis Tool
# This script automatically installs everything needed

echo "========================================"
echo "  PUBLIC COMMENT ANALYSIS TOOL"
echo "        One-Click Installer"
echo "========================================"
echo

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ ERROR: Python 3 not found!"
    echo
    echo "Please install Python 3.8+ first:"
    echo "Ubuntu/Debian: sudo apt install python3 python3-pip python3-tk"
    echo "CentOS/RHEL:   sudo yum install python3 python3-pip tkinter"
    echo "macOS:         brew install python3"
    echo
    exit 1
fi

echo "✅ Python found - starting installation..."
echo

# Make sure we have pip
if ! command -v pip3 &> /dev/null; then
    echo "📦 Installing pip..."
    curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
    python3 get-pip.py --user
    rm get-pip.py
fi

# Run the Python installer
python3 INSTALL.py

# Check if installation was successful
if [ $? -ne 0 ]; then
    echo
    echo "❌ Installation encountered errors."
    echo "Check the messages above for details."
    echo
    read -p "Press any key to continue..."
    exit 1
fi

echo
echo "✅ Installation completed successfully!"
echo
echo "🚀 To start the application:"
echo "  - Run: ./shortcuts/Launch_Analysis_Tool.sh"
echo "  - Or run: python3 gui_app.py"
echo
echo "📋 Desktop shortcut created (if supported)"
echo

# Make launcher executable
if [ -f "shortcuts/Launch_Analysis_Tool.sh" ]; then
    chmod +x shortcuts/Launch_Analysis_Tool.sh
fi

read -p "Press any key to continue..."