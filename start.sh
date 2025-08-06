#!/bin/bash
echo "🚀 Starting Document Analysis Platform Manager"
echo ""
echo "Activating virtual environment..."
source venv/bin/activate
echo ""
echo "Starting interactive manager..."
python interactive_manager.py
