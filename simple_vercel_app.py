#!/usr/bin/env python3
"""
Minimal Vercel app - Just shows demo interface and redirects to Railway for processing
"""

from flask import Flask, render_template, request, jsonify
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'demo-key')

# Railway URL for full processing (we'll update this)
RAILWAY_URL = "https://your-railway-app.railway.app"

@app.route('/')
def index():
    """Demo landing page that redirects to Railway for actual processing."""
    return render_template('simple_demo.html', railway_url=RAILWAY_URL)

@app.route('/health')
def health():
    """Health check."""
    return jsonify({'status': 'healthy', 'mode': 'demo_redirect'})

@app.route('/upload', methods=['POST'])
def upload():
    """Handle upload redirect to Railway."""
    return jsonify({
        'redirect': True,
        'message': 'Please use the full version for processing',
        'url': RAILWAY_URL
    })

if __name__ == '__main__':
    app.run(debug=True)