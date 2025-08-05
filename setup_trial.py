#!/usr/bin/env python3
"""
Complete trial setup script for hands-off customer deployment.
Sets up both frontend and backend for independent customer use.
"""

import os
import sys
import json
import subprocess
import time
from datetime import datetime, timedelta

def run_command(cmd, check=True):
    """Run shell command and return result."""
    print(f"🔧 Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"❌ Error: {result.stderr}")
        return False
    return True

def check_prerequisites():
    """Check if required tools are installed."""
    print("🔍 Checking prerequisites...")
    
    # Check for git
    if not run_command("git --version", check=False):
        print("❌ Git not found. Please install Git first.")
        return False
    
    # Check for Node.js (for Vercel CLI)
    if not run_command("node --version", check=False):
        print("❌ Node.js not found. Please install Node.js first.")
        return False
    
    print("✅ Prerequisites checked")
    return True

def setup_railway_backend():
    """Set up Railway backend for full processing."""
    print("\n🚂 Setting up Railway backend...")
    
    # Install Railway CLI if needed
    result = subprocess.run("railway --version", shell=True, capture_output=True)
    if result.returncode != 0:
        print("📦 Installing Railway CLI...")
        if not run_command("npm install -g @railway/cli"):
            return False
    
    # Create Railway project
    print("🔧 Setting up Railway project...")
    if not run_command("railway login"):
        return False
    
    # Create new project for trial
    project_name = f"comment-analyzer-trial-{datetime.now().strftime('%Y%m%d')}"
    if not run_command(f"railway create {project_name}"):
        return False
    
    # Set environment variables for trial
    trial_vars = {
        'FLASK_ENV': 'production',
        'TRIAL_MODE': 'true',
        'TRIAL_EXPIRY': (datetime.now() + timedelta(days=30)).isoformat(),
        'MAX_DOCUMENTS': '10000',
        'MAX_FILE_SIZE': '52428800',  # 50MB
        'SECRET_KEY': f'trial-key-{datetime.now().strftime("%Y%m%d")}'
    }
    
    for key, value in trial_vars.items():
        if not run_command(f'railway env set {key}="{value}"'):
            return False
    
    # Deploy to Railway
    print("🚀 Deploying backend to Railway...")
    if not run_command("railway up"):
        return False
    
    # Get the Railway URL
    result = subprocess.run("railway url", shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        backend_url = result.stdout.strip()
        print(f"✅ Backend deployed: {backend_url}")
        return backend_url
    
    return None

def setup_vercel_frontend(backend_url):
    """Set up Vercel frontend connected to Railway backend."""
    print("\n⚡ Setting up Vercel frontend...")
    
    # Install Vercel CLI if needed
    result = subprocess.run("vercel --version", shell=True, capture_output=True)
    if result.returncode != 0:
        print("📦 Installing Vercel CLI...")
        if not run_command("npm install -g vercel"):
            return False
    
    # Create trial-specific config
    trial_config = {
        "version": 2,
        "builds": [
            {
                "src": "trial_app.py",
                "use": "@vercel/python",
                "config": {
                    "runtime": "python3.10"
                }
            }
        ],
        "routes": [
            {
                "src": "/(.*)",
                "dest": "trial_app.py"
            }
        ],
        "env": {
            "FLASK_ENV": "production",
            "BACKEND_URL": backend_url,
            "TRIAL_MODE": "true",
            "SECRET_KEY": f"vercel-trial-{datetime.now().strftime('%Y%m%d')}"
        },
        "functions": {
            "trial_app.py": {
                "maxDuration": 30
            }
        }
    }
    
    # Write trial config
    with open('vercel_trial.json', 'w') as f:
        json.dump(trial_config, f, indent=2)
    
    # Login to Vercel
    if not run_command("vercel login"):
        return False
    
    # Deploy to Vercel
    print("🚀 Deploying frontend to Vercel...")
    if not run_command("vercel --prod --name comment-analyzer-trial"):
        return False
    
    # Get Vercel URL
    result = subprocess.run("vercel ls", shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        # Parse the URL from vercel ls output
        lines = result.stdout.split('\n')
        for line in lines:
            if 'comment-analyzer-trial' in line and 'https://' in line:
                frontend_url = line.split()[-1]
                if frontend_url.startswith('https://'):
                    print(f"✅ Frontend deployed: {frontend_url}")
                    return frontend_url
    
    return None

def create_trial_app():
    """Create a trial-specific Flask app."""
    print("📝 Creating trial application...")
    
    trial_app_content = '''#!/usr/bin/env python3
"""
Trial version of the Public Comment Analysis Tool
Connected to Railway backend for full processing.
"""

import os
import json
import requests
from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'trial-secret-key')

# Backend configuration
BACKEND_URL = os.environ.get('BACKEND_URL', 'http://localhost:8080')
TRIAL_MODE = os.environ.get('TRIAL_MODE', 'true').lower() == 'true'

@app.route('/')
def index():
    """Main trial page."""
    return render_template('trial_index.html', 
                         backend_url=BACKEND_URL,
                         trial_mode=TRIAL_MODE)

@app.route('/health')
def health():
    """Health check."""
    return jsonify({
        'status': 'healthy',
        'mode': 'trial',
        'backend': BACKEND_URL,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/proxy/<path:endpoint>', methods=['GET', 'POST'])
def proxy_to_backend(endpoint):
    """Proxy requests to Railway backend."""
    try:
        url = f"{BACKEND_URL}/{endpoint}"
        
        if request.method == 'POST':
            if request.is_json:
                response = requests.post(url, json=request.get_json(), timeout=30)
            else:
                response = requests.post(url, files=request.files, data=request.form, timeout=30)
        else:
            response = requests.get(url, params=request.args, timeout=30)
        
        return response.content, response.status_code, response.headers.items()
    
    except Exception as e:
        return jsonify({'error': f'Backend connection failed: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=False)
'''
    
    with open('trial_app.py', 'w') as f:
        f.write(trial_app_content)
    
    print("✅ Trial app created")

def create_trial_template():
    """Create trial-specific HTML template."""
    print("📝 Creating trial template...")
    
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    trial_template = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Document Analysis Tool - Trial Version</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-success">
        <div class="container">
            <a class="navbar-brand" href="/">
                <i class="fas fa-file-text me-2"></i>
                Document Analysis Tool
            </a>
            <span class="badge bg-warning text-dark ms-auto">FREE TRIAL</span>
        </div>
    </nav>

    <div class="container mt-4">
        <div class="alert alert-success">
            <h5><i class="fas fa-gift me-2"></i>Welcome to Your Free Trial!</h5>
            <p class="mb-0">
                This is a fully-featured document analysis tool. 
                Process up to 10,000 documents with OCR, search, and clustering capabilities.
                <strong>Trial expires in 30 days.</strong>
            </p>
        </div>

        <div class="row">
            <div class="col-lg-8 mx-auto">
                <div class="card">
                    <div class="card-header bg-primary text-white">
                        <h5 class="mb-0">
                            <i class="fas fa-upload me-2"></i>
                            Upload Documents for Analysis
                        </h5>
                    </div>
                    <div class="card-body">
                        <div class="upload-area border border-dashed border-primary rounded p-4 text-center">
                            <i class="fas fa-cloud-upload-alt fa-3x text-primary mb-3"></i>
                            <h5>Upload CSV File</h5>
                            <p class="text-muted">
                                CSV must contain "Document ID" and "URL" columns<br>
                                <strong>Trial limit:</strong> 10,000 documents, 50MB files
                            </p>
                            <input type="file" id="csvFile" accept=".csv" style="display: none;">
                            <button class="btn btn-primary" onclick="document.getElementById('csvFile').click()">
                                <i class="fas fa-folder-open me-2"></i>Choose File
                            </button>
                        </div>
                        
                        <div id="uploadStatus" class="mt-3" style="display: none;"></div>
                        
                        <div class="mt-3">
                            <button id="startAnalysis" class="btn btn-success btn-lg" disabled>
                                <i class="fas fa-rocket me-2"></i>Start Analysis
                            </button>
                        </div>
                    </div>
                </div>

                <div id="progressSection" class="card mt-4" style="display: none;">
                    <div class="card-header bg-info text-white">
                        <h5 class="mb-0">
                            <i class="fas fa-tasks me-2"></i>
                            Analysis Progress
                        </h5>
                    </div>
                    <div class="card-body">
                        <div class="progress mb-3">
                            <div id="progressBar" class="progress-bar progress-bar-striped progress-bar-animated" 
                                 role="progressbar" style="width: 0%"></div>
                        </div>
                        <div id="progressMessage">Initializing...</div>
                    </div>
                </div>

                <div class="card mt-4 border-warning">
                    <div class="card-header bg-warning text-dark">
                        <h5 class="mb-0">
                            <i class="fas fa-star me-2"></i>
                            Trial Features
                        </h5>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-6">
                                <h6 class="text-success">✅ Included in Trial:</h6>
                                <ul class="list-unstyled">
                                    <li><i class="fas fa-check text-success me-2"></i>Full OCR processing</li>
                                    <li><i class="fas fa-check text-success me-2"></i>Text extraction</li>
                                    <li><i class="fas fa-check text-success me-2"></i>Search indexing</li>
                                    <li><i class="fas fa-check text-success me-2"></i>Document clustering</li>
                                    <li><i class="fas fa-check text-success me-2"></i>Export capabilities</li>
                                </ul>
                            </div>
                            <div class="col-md-6">
                                <h6 class="text-warning">⚠️ Trial Limits:</h6>
                                <ul class="list-unstyled">
                                    <li><i class="fas fa-clock text-warning me-2"></i>30-day access</li>
                                    <li><i class="fas fa-file text-warning me-2"></i>10,000 documents max</li>
                                    <li><i class="fas fa-hdd text-warning me-2"></i>50MB file size limit</li>
                                    <li><i class="fas fa-database text-warning me-2"></i>Data cleanup after trial</li>
                                </ul>
                            </div>
                        </div>
                        
                        <div class="alert alert-info mt-3">
                            <h6><i class="fas fa-info-circle me-2"></i>Need Full Version?</h6>
                            <p class="mb-0">
                                Contact us for unlimited processing, larger files, and permanent data storage.
                                Production deployments available from $5/month.
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        const backendUrl = "{{ backend_url }}";
        let uploadedFile = null;

        document.getElementById('csvFile').addEventListener('change', handleFileUpload);

        function handleFileUpload(event) {
            const file = event.target.files[0];
            if (!file) return;

            if (!file.name.toLowerCase().endsWith('.csv')) {
                alert('Please select a CSV file');
                return;
            }

            if (file.size > 50 * 1024 * 1024) {
                alert('File too large for trial (max 50MB)');
                return;
            }

            const formData = new FormData();
            formData.append('csv_file', file);

            document.getElementById('uploadStatus').innerHTML = 
                '<div class="progress"><div class="progress-bar progress-bar-striped progress-bar-animated" style="width: 100%"></div></div>';
            document.getElementById('uploadStatus').style.display = 'block';

            fetch('/proxy/upload', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    uploadedFile = data.filename;
                    document.getElementById('uploadStatus').innerHTML = 
                        `<div class="alert alert-success">
                            <strong>File uploaded:</strong> ${data.filename}<br>
                            <strong>Documents:</strong> ${data.document_count}
                        </div>`;
                    document.getElementById('startAnalysis').disabled = false;
                } else {
                    document.getElementById('uploadStatus').innerHTML = 
                        `<div class="alert alert-danger">Upload failed: ${data.error}</div>`;
                }
            })
            .catch(error => {
                document.getElementById('uploadStatus').innerHTML = 
                    `<div class="alert alert-danger">Upload failed: ${error.message}</div>`;
            });
        }

        document.getElementById('startAnalysis').addEventListener('click', () => {
            if (!uploadedFile) return;

            document.getElementById('progressSection').style.display = 'block';
            document.getElementById('startAnalysis').disabled = true;

            fetch('/proxy/start_analysis', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ csv_file: uploadedFile })
            })
            .then(response => response.json())
            .then(data => {
                if (data.job_id) {
                    monitorJob(data.job_id);
                } else {
                    alert('Failed to start analysis: ' + (data.error || 'Unknown error'));
                    document.getElementById('startAnalysis').disabled = false;
                }
            });
        });

        function monitorJob(jobId) {
            fetch(`/proxy/job_status/${jobId}`)
            .then(response => response.json())
            .then(data => {
                document.getElementById('progressBar').style.width = data.progress + '%';
                document.getElementById('progressMessage').textContent = data.message;

                if (data.status === 'completed') {
                    document.getElementById('progressBar').className = 'progress-bar bg-success';
                    document.getElementById('progressMessage').innerHTML = 
                        `<strong>Analysis Complete!</strong> <a href="/proxy/download_results/${jobId}" class="btn btn-sm btn-primary ms-2">Download Results</a>`;
                } else if (data.status === 'failed') {
                    document.getElementById('progressBar').className = 'progress-bar bg-danger';
                    document.getElementById('progressMessage').textContent = 'Analysis failed: ' + data.message;
                    document.getElementById('startAnalysis').disabled = false;
                } else {
                    setTimeout(() => monitorJob(jobId), 2000);
                }
            })
            .catch(error => {
                console.error('Error monitoring job:', error);
                setTimeout(() => monitorJob(jobId), 5000);
            });
        }
    </script>
</body>
</html>'''
    
    with open('templates/trial_index.html', 'w') as f:
        f.write(trial_template)
    
    print("✅ Trial template created")

def generate_customer_instructions(frontend_url, backend_url):
    """Generate instructions for customer."""
    instructions = f"""
# 🌐 Your Document Analysis Tool Trial is Ready!

## **ACCESS INFORMATION**

**Frontend URL**: {frontend_url}
**Trial Period**: 30 days from today
**Document Limit**: 10,000 documents
**File Size Limit**: 50MB per file

## **FEATURES INCLUDED**

✅ **Full OCR Processing** - Handle scanned PDFs
✅ **Text Extraction** - Extract text from all document types  
✅ **Search Indexing** - Full-text search capabilities
✅ **Document Clustering** - Group similar documents
✅ **Export Functions** - Download results in multiple formats
✅ **Real-time Progress** - Track analysis status
✅ **Professional Interface** - Easy-to-use web application

## **GETTING STARTED**

1. **Visit**: {frontend_url}
2. **Upload**: CSV file with "Document ID" and "URL" columns
3. **Analyze**: Click "Start Analysis" and monitor progress
4. **Review**: Search, browse, and download results
5. **Test**: Try multiple document batches

## **TRIAL DETAILS**

- **Duration**: 30 days
- **Processing**: Up to 10,000 documents total
- **File Types**: PDF, DOCX, TXT files
- **Features**: All functionality included
- **Support**: Reply to this email with questions

## **AFTER TRIAL**

Contact us for:
- Unlimited document processing
- Larger file support (500MB+)
- Permanent data storage
- Production deployment
- Custom domain setup

**Pricing**: Starting at $5/month for unlimited processing

---

**Questions?** Reply to this email for immediate support.

**Technical Issues?** The system monitors itself and should work reliably.
"""
    
    with open('CUSTOMER_INSTRUCTIONS.md', 'w') as f:
        f.write(instructions)
    
    print(f"✅ Customer instructions saved to CUSTOMER_INSTRUCTIONS.md")
    print(f"\n📧 SEND TO CUSTOMER:")
    print(f"Frontend URL: {frontend_url}")
    print(f"Instructions: See CUSTOMER_INSTRUCTIONS.md")

def main():
    """Main setup function."""
    print("🚀 Setting up complete trial deployment...")
    print("=" * 60)
    
    if not check_prerequisites():
        sys.exit(1)
    
    # Create trial-specific files
    create_trial_app()
    create_trial_template()
    
    # Deploy backend
    print("\n🚂 Deploying backend processing...")
    backend_url = setup_railway_backend()
    if not backend_url:
        print("❌ Backend deployment failed")
        sys.exit(1)
    
    # Deploy frontend
    print("\n⚡ Deploying frontend interface...")
    frontend_url = setup_vercel_frontend(backend_url)
    if not frontend_url:
        print("❌ Frontend deployment failed")
        sys.exit(1)
    
    # Generate customer instructions
    generate_customer_instructions(frontend_url, backend_url)
    
    print("\n" + "=" * 60)
    print("🎉 TRIAL SETUP COMPLETE!")
    print("=" * 60)
    print(f"📱 Customer URL: {frontend_url}")
    print(f"🔧 Backend URL: {backend_url}")
    print(f"⏰ Trial Period: 30 days")
    print(f"📄 Document Limit: 10,000")
    print("\n📧 Next Steps:")
    print("1. Send customer the frontend URL")
    print("2. Share CUSTOMER_INSTRUCTIONS.md")
    print("3. Customer can use independently for 30 days")
    print("4. Follow up after trial period")
    print("\n✅ No further involvement needed from you!")

if __name__ == "__main__":
    main()