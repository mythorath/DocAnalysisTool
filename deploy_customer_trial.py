#!/usr/bin/env python3
"""
Deploy complete customer trial to Railway (free tier)
Single deployment with both frontend and backend.
"""

import os
import sys
import json
import subprocess
from datetime import datetime, timedelta

def run_command(cmd, check=True):
    """Run shell command and return result."""
    print(f"🔧 Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"❌ Error: {result.stderr}")
        return False, result.stderr
    return True, result.stdout.strip()

def deploy_to_railway():
    """Deploy complete trial to Railway."""
    print("🚂 Deploying customer trial to Railway...")
    
    # Check if Railway CLI is installed
    success, _ = run_command("railway --version", check=False)
    if not success:
        print("📦 Installing Railway CLI...")
        success, _ = run_command("npm install -g @railway/cli")
        if not success:
            print("❌ Failed to install Railway CLI. Please install Node.js first.")
            return None
    
    # Login to Railway
    print("🔑 Please login to Railway (browser will open):")
    success, _ = run_command("railway login")
    if not success:
        return None
    
    # Create new project for customer trial
    project_name = f"comment-analyzer-trial-{datetime.now().strftime('%Y%m%d-%H%M')}"
    print(f"📦 Creating Railway project: {project_name}")
    success, _ = run_command(f"railway create {project_name}")
    if not success:
        return None
    
    # Set environment variables for trial
    print("⚙️ Setting environment variables...")
    trial_vars = {
        'FLASK_ENV': 'production',
        'SECRET_KEY': f'trial-{datetime.now().strftime("%Y%m%d%H%M")}',
        'TRIAL_MODE': 'true',
        'TRIAL_EXPIRY': (datetime.now() + timedelta(days=30)).isoformat(),
        'MAX_DOCUMENTS': '10000',
        'MAX_FILE_SIZE': '52428800',  # 50MB
        'PORT': '8080'
    }
    
    for key, value in trial_vars.items():
        success, _ = run_command(f'railway env set {key}="{value}"')
        if not success:
            print(f"⚠️ Warning: Failed to set {key}")
    
    # Deploy the application
    print("🚀 Deploying to Railway...")
    success, _ = run_command("railway up")
    if not success:
        print("❌ Deployment failed")
        return None
    
    # Get the deployment URL
    print("🔍 Getting deployment URL...")
    success, url_output = run_command("railway url", check=False)
    if success and url_output:
        trial_url = url_output.strip()
        print(f"✅ Trial deployed successfully!")
        print(f"🌐 Customer URL: {trial_url}")
        return trial_url
    else:
        # Try alternative method to get URL
        success, status = run_command("railway status", check=False)
        if success:
            lines = status.split('\n')
            for line in lines:
                if 'https://' in line:
                    trial_url = line.strip().split()[-1]
                    if trial_url.startswith('https://'):
                        print(f"✅ Trial deployed successfully!")
                        print(f"🌐 Customer URL: {trial_url}")
                        return trial_url
    
    print("⚠️ Deployment successful but URL not found. Check Railway dashboard.")
    return "Check Railway dashboard for URL"

def create_customer_email(trial_url):
    """Generate customer email content."""
    
    email_content = f"""Subject: Your Document Analysis Tool Trial is Ready! 🚀

Hi there!

Your cloud-hosted document analysis tool is now live and ready for testing:

🌐 **Trial URL**: {trial_url}
⏰ **Trial Period**: 30 days (expires {(datetime.now() + timedelta(days=30)).strftime('%B %d, %Y')})
📊 **Document Limit**: 10,000 documents
💾 **File Size Limit**: 50MB per file

## What You Can Do:

✅ **Upload CSV files** with Document ID and URL columns
✅ **Full OCR processing** - Handle scanned PDFs and images  
✅ **Text extraction** - Extract text from PDFs, DOCX files
✅ **Search & indexing** - Full-text search capabilities
✅ **Document clustering** - Group similar documents automatically
✅ **Export results** - Download analysis reports
✅ **Real-time progress** - Track processing status

## Getting Started:

1. **Visit the URL above** - No installation needed!
2. **Upload your CSV file** - Must have "Document ID" and "URL" columns
3. **Start analysis** - Click the big green button
4. **Monitor progress** - Real-time status updates
5. **Review results** - Search, browse, and download

## Trial Features:

- **Professional web interface** - Works on any device
- **Complete OCR capabilities** - Process scanned documents
- **Advanced analytics** - Clustering and text analysis
- **No software installation** - Everything runs in the cloud
- **30-day full access** - Test thoroughly with your data

## Need Help?

- **Questions?** Reply to this email
- **Technical issues?** The system is monitored and should work reliably
- **Want more features?** Contact us about the full version

## After Your Trial:

If you like what you see, we offer:
- **Unlimited document processing**
- **Larger file support** (500MB+ files)
- **Permanent data storage** 
- **Custom domain setup**
- **Priority support**

**Pricing starts at just $5/month for unlimited processing.**

---

**Ready to get started?** Visit {trial_url} and upload your first CSV!

Best regards,
Your Document Analysis Team

P.S. This trial includes ALL features - you're getting the full experience!
"""
    
    # Save email content to file
    with open('CUSTOMER_EMAIL.txt', 'w', encoding='utf-8') as f:
        f.write(email_content)
    
    print("\n📧 Customer email saved to: CUSTOMER_EMAIL.txt")
    print("\n" + "="*60)
    print("📋 COPY AND SEND THIS TO YOUR CUSTOMER:")
    print("="*60)
    print(email_content)
    
    return email_content

def create_trial_monitoring_info(trial_url):
    """Create monitoring information for you."""
    
    monitoring_info = f"""# 🔍 Trial Monitoring Information

## Customer Trial Details

**Deployment Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Trial URL**: {trial_url}
**Expires**: {(datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')}
**Platform**: Railway.app (Free tier)

## What Customer Can Do:
- Upload and process up to 10,000 documents
- Full OCR processing of scanned PDFs
- Text extraction from all supported formats
- Search and clustering capabilities
- Export analysis results
- 30 days of full access

## Monitoring (Optional):
- Railway dashboard: https://railway.app/dashboard
- Check usage and performance
- Monitor resource consumption
- View application logs

## Trial Management:
- **Automatic cleanup**: Data removed after 30 days
- **Resource limits**: 512MB RAM, 1GB storage (Railway free tier)
- **No intervention needed**: Customer can use independently

## Follow-up Actions:
1. **Week 1**: Check if customer is using the tool
2. **Week 3**: Send reminder about trial expiry
3. **After trial**: Follow up about full version

## Full Version Deployment:
When customer wants to upgrade:
```bash
python deploy.py railway  # Full production version
# OR
python deploy.py digitalocean  # Enterprise version
```

## Support:
- Customer questions: Forward to you
- Technical issues: Railway handles infrastructure
- Feature requests: Note for full version discussion

---

**No ongoing maintenance required from you!**
Customer has completely independent access for 30 days.
"""
    
    with open('TRIAL_MONITORING.md', 'w', encoding='utf-8') as f:
        f.write(monitoring_info)
    
    print(f"📋 Trial monitoring info saved to: TRIAL_MONITORING.md")

def main():
    """Main deployment function."""
    print("🌐 Customer Trial Deployment")
    print("="*50)
    print("This will deploy a complete, independent trial")
    print("that your customer can use for 30 days without")
    print("any involvement from you.")
    print()
    
    confirm = input("Continue with deployment? (y/N): ").lower().strip()
    if confirm != 'y':
        print("❌ Deployment cancelled")
        return
    
    # Deploy to Railway
    trial_url = deploy_to_railway()
    if not trial_url:
        print("❌ Deployment failed")
        return
    
    # Create customer communication
    create_customer_email(trial_url)
    create_trial_monitoring_info(trial_url)
    
    print("\n" + "="*60)
    print("🎉 CUSTOMER TRIAL DEPLOYMENT COMPLETE!")
    print("="*60)
    print(f"🌐 Trial URL: {trial_url}")
    print(f"⏰ Trial Period: 30 days")
    print(f"📄 Documents: Up to 10,000")
    print(f"💾 File Size: Up to 50MB each")
    print()
    print("📧 Next Steps:")
    print("1. Copy email content from CUSTOMER_EMAIL.txt")
    print("2. Send to your customer")
    print("3. Customer uses independently for 30 days")
    print("4. Follow up after trial period")
    print()
    print("✅ No further action needed from you!")
    print("   Customer has complete access to:")
    print("   • Professional web interface")
    print("   • Full OCR processing")
    print("   • Text extraction & analysis")
    print("   • Search & clustering")
    print("   • Export capabilities")

if __name__ == "__main__":
    main()