#!/usr/bin/env python3
"""
Vercel serverless function wrapper for the web application.
This file adapts our Flask app to work with Vercel's serverless architecture.
"""

import sys
import os
from pathlib import Path

# Add the parent directory to the path so we can import our modules
sys.path.append(str(Path(__file__).parent.parent))

# Import our main Flask application
from web_app import app

# Vercel expects the Flask app to be available as 'app'
# This is the entry point for all requests
if __name__ == "__main__":
    app.run()