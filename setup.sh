#!/bin/bash

echo "🚀 Document Analysis Platform Setup (Linux/macOS)"
echo "=================================================="
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed"
    echo "Please install Python 3.8+ from your package manager"
    exit 1
fi

echo "✅ Python found"
echo

# Make setup.py executable
chmod +x setup.py

# Run the setup script
echo "🔧 Running setup script..."
python3 setup.py

echo
echo "📋 To activate your environment later, run:"
echo "   source venv/bin/activate"
echo
echo "🎉 Setup complete! Check the output above for your portal URL."

