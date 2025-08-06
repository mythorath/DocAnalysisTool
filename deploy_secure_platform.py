#!/usr/bin/env python3
"""
Deploy the secure customer data access platform to various cloud providers.
Supports Railway, DigitalOcean, and AWS deployments.
"""

import os
import sys
import json
import subprocess
import secrets
from datetime import datetime
from pathlib import Path

def run_command(cmd, check=True):
    """Run shell command and return result."""
    print(f"🔧 Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"❌ Error: {result.stderr}")
        return False, result.stderr
    return True, result.stdout.strip()

def create_production_requirements():
    """Create production requirements.txt with security-focused packages."""
    requirements = """# Core Flask Application
Flask==2.3.3
Werkzeug==2.3.7

# Security & Authentication
bcrypt==4.0.1
cryptography==41.0.4

# Data Processing
pandas==2.1.1
numpy==1.24.3
sqlite3

# Document Processing (Optional - for admin processing)
PyMuPDF==1.23.3
pdf2image==3.0.1
pytesseract==0.3.10
Pillow==10.0.0
python-docx==0.8.11

# Text Analysis (Optional)
scikit-learn==1.3.0
sentence-transformers==2.2.2
nltk==3.8.1

# Production Server
gunicorn==21.2.0
gevent==23.7.0

# Monitoring & Logging
sentry-sdk[flask]==1.32.0

# Environment Management
python-dotenv==1.0.0

# Database (Production)
psycopg2-binary==2.9.7  # For PostgreSQL
"""
    
    with open('requirements_production.txt', 'w') as f:
        f.write(requirements)
    
    print("✅ Created requirements_production.txt")

def create_production_config():
    """Create production configuration files."""
    
    # Gunicorn configuration
    gunicorn_config = """# Gunicorn configuration for production
bind = "0.0.0.0:8080"
workers = 4
worker_class = "gevent"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
timeout = 300
keepalive = 2
preload_app = True

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "secure-document-platform"

# Graceful shutdown
graceful_timeout = 30
"""
    
    with open('gunicorn.conf.py', 'w') as f:
        f.write(gunicorn_config)
    
    # Docker configuration
    dockerfile = """FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    tesseract-ocr \\
    poppler-utils \\
    libpq-dev \\
    gcc \\
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements_production.txt .
RUN pip install --no-cache-dir -r requirements_production.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p platform_data/customers platform_data/admin platform_data/logs

# Set environment variables
ENV FLASK_ENV=production
ENV PYTHONPATH=/app

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:8080/health || exit 1

# Run the application
CMD ["gunicorn", "--config", "gunicorn.conf.py", "secure_platform:app"]
"""
    
    with open('Dockerfile', 'w') as f:
        f.write(dockerfile)
    
    # Docker Compose for local development
    docker_compose = """version: '3.8'

services:
  app:
    build: .
    ports:
      - "8080:8080"
    environment:
      - FLASK_ENV=production
      - SECRET_KEY=${SECRET_KEY}
      - DATABASE_URL=${DATABASE_URL}
    volumes:
      - ./platform_data:/app/platform_data
    depends_on:
      - postgres
    restart: unless-stopped

  postgres:
    image: postgres:15
    environment:
      - POSTGRES_DB=document_platform
      - POSTGRES_USER=platform_user
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - app
    restart: unless-stopped

volumes:
  postgres_data:
"""
    
    with open('docker-compose.yml', 'w') as f:
        f.write(docker_compose)
    
    # Nginx configuration
    nginx_config = """events {
    worker_connections 1024;
}

http {
    upstream app {
        server app:8080;
    }

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=login:10m rate=5r/m;
    limit_req_zone $binary_remote_addr zone=api:10m rate=60r/m;

    server {
        listen 80;
        server_name _;
        return 301 https://$host$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name _;

        # SSL configuration (add your certificates)
        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers HIGH:!aNULL:!MD5;

        # Security headers
        add_header X-Frame-Options DENY;
        add_header X-Content-Type-Options nosniff;
        add_header X-XSS-Protection "1; mode=block";
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";

        # File upload size
        client_max_body_size 500M;

        # Rate limiting
        location /login {
            limit_req zone=login burst=3 nodelay;
            proxy_pass http://app;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        location /api/ {
            limit_req zone=api burst=10 nodelay;
            proxy_pass http://app;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        location / {
            proxy_pass http://app;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # Timeout settings
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 300s;
        }
    }
}
"""
    
    with open('nginx.conf', 'w') as f:
        f.write(nginx_config)
    
    print("✅ Created production configuration files")

def create_railway_config():
    """Create Railway deployment configuration."""
    
    railway_config = {
        "build": {
            "builder": "DOCKERFILE"
        },
        "deploy": {
            "healthcheckPath": "/health",
            "restartPolicyType": "ON_FAILURE",
            "healthcheckTimeout": 300
        }
    }
    
    with open('railway.json', 'w') as f:
        json.dump(railway_config, f, indent=2)
    
    # Railway deployment script
    railway_deploy = """#!/bin/bash
set -e

echo "🚂 Deploying to Railway..."

# Install Railway CLI if not present
if ! command -v railway &> /dev/null; then
    echo "Installing Railway CLI..."
    npm install -g @railway/cli
fi

# Login to Railway
echo "Please login to Railway:"
railway login

# Create new project
PROJECT_NAME="secure-document-platform-$(date +%Y%m%d-%H%M)"
railway create $PROJECT_NAME

# Set environment variables
echo "Setting environment variables..."
railway env set SECRET_KEY="$(openssl rand -base64 32)"
railway env set FLASK_ENV="production"
railway env set DATABASE_URL="sqlite:///platform_data/admin/platform.db"

# Deploy
echo "Deploying application..."
railway deploy

# Get deployment URL
echo "Getting deployment URL..."
railway url

echo "✅ Deployment complete!"
echo "📱 Your secure platform is now live!"
"""
    
    with open('deploy_railway.sh', 'w') as f:
        f.write(railway_deploy)
    
    os.chmod('deploy_railway.sh', 0o755)
    
    print("✅ Created Railway deployment configuration")

def create_digitalocean_config():
    """Create DigitalOcean App Platform configuration."""
    
    do_config = {
        "name": "secure-document-platform",
        "services": [{
            "name": "web",
            "source_dir": "/",
            "github": {
                "repo": "your-username/your-repo",
                "branch": "main"
            },
            "run_command": "gunicorn --config gunicorn.conf.py secure_platform:app",
            "environment_slug": "python",
            "instance_count": 1,
            "instance_size_slug": "basic-xxs",
            "health_check": {
                "http_path": "/health"
            },
            "envs": [{
                "key": "SECRET_KEY",
                "scope": "RUN_TIME",
                "type": "SECRET"
            }, {
                "key": "FLASK_ENV",
                "scope": "RUN_TIME",
                "value": "production"
            }]
        }],
        "databases": [{
            "name": "db",
            "engine": "PG",
            "version": "15"
        }]
    }
    
    with open('.do/app.yaml', 'w') as f:
        json.dump(do_config, f, indent=2)
    
    print("✅ Created DigitalOcean deployment configuration")

def create_environment_template():
    """Create environment template file."""
    
    env_template = """# Production Environment Variables
# Copy this to .env and fill in your values

# Security
SECRET_KEY=your-secret-key-here-use-long-random-string
FLASK_ENV=production

# Database (for PostgreSQL production deployment)
DATABASE_URL=postgresql://username:password@localhost:5432/database_name

# Optional: External services
SENTRY_DSN=your-sentry-dsn-for-error-tracking

# Optional: Email configuration (for notifications)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password

# Optional: Cloud storage (for large file handling)
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_S3_BUCKET=your-s3-bucket-name
AWS_REGION=us-east-1

# Application settings
MAX_CONTENT_LENGTH=536870912  # 512MB
SESSION_TIMEOUT=86400  # 24 hours in seconds
"""
    
    with open('.env.template', 'w') as f:
        f.write(env_template)
    
    print("✅ Created environment template")

def create_security_documentation():
    """Create security documentation and best practices."""
    
    security_doc = """# Security Features & Best Practices

## 🔒 Built-in Security Features

### Authentication & Authorization
- ✅ Secure password hashing (bcrypt)
- ✅ Session management with secure cookies
- ✅ Role-based access control (admin/customer)
- ✅ User account isolation
- ✅ API key authentication for admin operations

### Data Protection
- ✅ Customer data isolation (separate directories)
- ✅ SQL injection prevention (parameterized queries)
- ✅ XSS protection (secure headers)
- ✅ CSRF protection (SameSite cookies)
- ✅ Input validation and sanitization

### Infrastructure Security
- ✅ HTTPS enforcement (production)
- ✅ Rate limiting (login attempts, API calls)
- ✅ File upload restrictions
- ✅ Audit logging for all actions
- ✅ Health check endpoints

## 🛡️ Production Security Checklist

### Before Deployment
- [ ] Generate strong SECRET_KEY (use: `openssl rand -base64 32`)
- [ ] Set up SSL/TLS certificates
- [ ] Configure firewall rules
- [ ] Set up database backups
- [ ] Configure monitoring and alerts

### Environment Variables
- [ ] SECRET_KEY (required)
- [ ] FLASK_ENV=production
- [ ] DATABASE_URL (for PostgreSQL)
- [ ] SENTRY_DSN (error tracking)

### Database Security
- [ ] Use PostgreSQL in production (not SQLite)
- [ ] Regular database backups
- [ ] Database user with minimal privileges
- [ ] Network-level database isolation

### File System Security
- [ ] Secure file permissions (600 for sensitive files)
- [ ] Regular cleanup of temp files
- [ ] Disk encryption for data directory
- [ ] Separate volumes for customer data

### Network Security
- [ ] HTTPS only (HTTP redirects to HTTPS)
- [ ] Strong SSL/TLS configuration
- [ ] Rate limiting in reverse proxy
- [ ] DDoS protection (Cloudflare recommended)

### Monitoring & Maintenance
- [ ] Set up log aggregation
- [ ] Monitor disk usage (customer data grows)
- [ ] Set up uptime monitoring
- [ ] Regular security updates
- [ ] Audit log review

## 🚨 Incident Response

### Data Breach Response
1. Immediately isolate affected systems
2. Identify scope of breach
3. Notify affected customers (if required by law)
4. Document incident and remediation steps
5. Review and improve security measures

### Customer Data Access
- All customer access is logged
- Customers can only access their own data
- Admin actions are audited
- Data export capabilities are limited

### Backup & Recovery
- Daily database backups
- Customer data directory backups
- Point-in-time recovery capability
- Disaster recovery plan documentation

## 📝 Compliance Considerations

### Data Privacy
- Customer data is isolated and protected
- Clear data retention policies
- Data export capabilities for customers
- Data deletion upon customer request

### Access Controls
- Role-based permissions
- Admin account restrictions
- Regular access review
- Strong password requirements

### Audit Trail
- All user actions logged
- Admin operations tracked
- Failed login attempts recorded
- Data access events monitored
"""
    
    with open('SECURITY.md', 'w') as f:
        f.write(security_doc)
    
    print("✅ Created security documentation")

def main():
    """Main deployment setup function."""
    print("🌐 Setting up Secure Document Platform Deployment")
    print("=" * 60)
    
    # Create all configuration files
    create_production_requirements()
    create_production_config()
    create_railway_config()
    create_digitalocean_config()
    create_environment_template()
    create_security_documentation()
    
    print("\n" + "=" * 60)
    print("🎉 DEPLOYMENT SETUP COMPLETE!")
    print("=" * 60)
    
    print("\n📁 Files Created:")
    print("  - requirements_production.txt (Production dependencies)")
    print("  - Dockerfile (Container configuration)")
    print("  - docker-compose.yml (Local development)")
    print("  - gunicorn.conf.py (Production server config)")
    print("  - nginx.conf (Reverse proxy config)")
    print("  - railway.json (Railway deployment)")
    print("  - .do/app.yaml (DigitalOcean deployment)")
    print("  - .env.template (Environment variables)")
    print("  - SECURITY.md (Security documentation)")
    print("  - deploy_railway.sh (Railway deployment script)")
    
    print("\n🚀 Deployment Options:")
    print("  1. Railway: ./deploy_railway.sh")
    print("  2. DigitalOcean: Use .do/app.yaml with doctl")
    print("  3. Docker: docker-compose up -d")
    print("  4. Manual: gunicorn --config gunicorn.conf.py secure_platform:app")
    
    print("\n⚠️  Important Next Steps:")
    print("  1. Copy .env.template to .env and fill in values")
    print("  2. Generate a strong SECRET_KEY")
    print("  3. Set up SSL certificates for production")
    print("  4. Review SECURITY.md for production checklist")
    print("  5. Set up monitoring and backups")
    
    print("\n🔐 Security Features Included:")
    print("  ✅ User authentication & authorization")
    print("  ✅ Customer data isolation")
    print("  ✅ Audit logging")
    print("  ✅ Rate limiting")
    print("  ✅ Input validation")
    print("  ✅ Secure sessions")
    
    print("\n📱 Your customers will be able to:")
    print("  • Securely log in to their private dashboard")
    print("  • Search their processed documents")
    print("  • Export their data in multiple formats")
    print("  • View processing status and results")
    
    print("\n👨‍💼 As an admin, you can:")
    print("  • Create and manage customer accounts")
    print("  • Process customer document batches")
    print("  • Monitor platform usage and activity")
    print("  • View system logs and statistics")

if __name__ == "__main__":
    main()

