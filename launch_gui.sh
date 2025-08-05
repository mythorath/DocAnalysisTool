#!/bin/bash
# Launch script for Public Comment Analysis Tool GUI
echo "Starting Public Comment Analysis Tool..."
echo

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python3 not found. Please install Python 3.8+ first."
    exit 1
fi

# Check if required modules are available
python3 -c "import tkinter" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "ERROR: tkinter not available. Please install python3-tk package."
    echo "Ubuntu/Debian: sudo apt-get install python3-tk"
    echo "CentOS/RHEL: sudo yum install tkinter"
    echo "macOS: Should be included with Python"
    exit 1
fi

# Launch the GUI application
echo "Launching GUI application..."
python3 gui_app.py

# Check exit status
if [ $? -ne 0 ]; then
    echo
    echo "Application closed with an error. Check the messages above."
    read -p "Press any key to continue..."
fi