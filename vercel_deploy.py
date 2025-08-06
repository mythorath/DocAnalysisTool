#!/usr/bin/env python3
"""
Vercel deployment for the secure document platform.
Note: Vercel is better for demos, Railway is better for production.
"""

import os
import json
import secrets

def create_vercel_files():
    """Create necessary files for Vercel deployment."""
    
    # Create vercel.json configuration
    vercel_config = {
        "version": 2,
        "builds": [
            {
                "src": "customer_portal.py",
                "use": "@vercel/python"
            }
        ],
        "routes": [
            {
                "src": "/(.*)",
                "dest": "/customer_portal.py"
            }
        ],
        "env": {
            "FLASK_ENV": "production"
        },
        "functions": {
            "customer_portal.py": {
                "maxDuration": 30
            }
        }
    }
    
    with open('vercel.json', 'w') as f:
        json.dump(vercel_config, f, indent=2)
    
    # Create requirements.txt for Vercel
    requirements = """Flask==2.3.3
Werkzeug==2.3.7
pandas==2.1.1
python-dotenv==1.0.0
"""
    
    with open('requirements.txt', 'w') as f:
        f.write(requirements)
    
    # Create .env.example
    env_example = """# Copy this to .env and fill in your values
SECRET_KEY=your-secret-key-here
FLASK_ENV=production
"""
    
    with open('.env.example', 'w') as f:
        f.write(env_example)
    
    print("✅ Created Vercel deployment files")

def create_deployment_guide():
    """Create deployment guide."""
    
    guide = """# 🚀 Deployment Guide

## Railway Deployment (Recommended for Production)

Railway is better for production because it supports:
- File storage for customer data
- Background processing
- SQLite databases
- Longer request timeouts

### Deploy to Railway:
```bash
python railway_deploy.py
```

## Vercel Deployment (Good for Demos)

Vercel is good for demos but has limitations:
- No persistent file storage
- 30-second function timeouts
- Serverless architecture limitations

### Deploy to Vercel:
1. Install Vercel CLI: `npm install -g vercel`
2. Run: `python vercel_deploy.py`
3. Run: `vercel`
4. Set environment variables in Vercel dashboard

## Environment Variables

Both platforms need these environment variables:
- `SECRET_KEY`: Generate with `python -c "import secrets; print(secrets.token_hex(32))"`
- `FLASK_ENV`: Set to "production"

## Post-Deployment

1. Visit your platform URL
2. Login as admin: admin@platform.com / admin123
3. **IMMEDIATELY** change the admin password
4. Create your first customer account
5. Test document processing

## Security Notes

- Always use HTTPS in production
- Change default admin password immediately
- Set strong SECRET_KEY
- Monitor audit logs regularly
"""
    
    with open('DEPLOYMENT.md', 'w') as f:
        f.write(guide)
    
    print("✅ Created deployment guide")

def main():
    """Main function for Vercel setup."""
    print("🌐 Vercel Setup for Secure Document Platform")
    print("=" * 60)
    print("⚠️  Note: Railway is recommended for production!")
    print("   Vercel is good for demos but has limitations.")
    print()
    
    create_vercel_files()
    create_deployment_guide()
    
    print("\n📋 Vercel Deployment Steps:")
    print("1. Install Vercel CLI: npm install -g vercel")
    print("2. Run: vercel")
    print("3. Follow the prompts")
    print("4. Set SECRET_KEY in Vercel dashboard")
    print("5. Visit your deployment URL")
    
    print("\n🚂 For production, use Railway instead:")
    print("   python railway_deploy.py")

if __name__ == "__main__":
    main()
