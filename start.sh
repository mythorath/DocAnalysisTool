#!/bin/bash
# Railway start script for Document Analysis Tool

echo "🚂 Starting Railway Document Analysis Tool..."

# Install lightweight requirements
echo "📦 Installing dependencies..."
pip install -r requirements_railway.txt

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p downloads text output logs input

# Start the application
echo "🚀 Starting web application..."
python railway_web_app.py