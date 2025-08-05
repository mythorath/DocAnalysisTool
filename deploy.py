#!/usr/bin/env python3
"""
One-click deployment script for Public Comment Analysis Tool
Supports multiple cloud platforms with automatic setup.
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def run_command(cmd, check=True):
    """Run shell command and return result."""
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"Error: {result.stderr}")
        sys.exit(1)
    return result

def check_docker():
    """Check if Docker is installed."""
    try:
        result = run_command("docker --version", check=False)
        return result.returncode == 0
    except:
        return False

def deploy_railway():
    """Deploy to Railway.app"""
    print("🚂 Deploying to Railway...")
    
    # Check if Railway CLI is installed
    result = run_command("railway --version", check=False)
    if result.returncode != 0:
        print("Installing Railway CLI...")
        if os.name == 'nt':  # Windows
            run_command("npm install -g @railway/cli")
        else:  # Linux/Mac
            run_command("curl -fsSL https://railway.app/install.sh | sh")
    
    # Login and deploy
    print("Please login to Railway (browser will open):")
    run_command("railway login")
    
    # Create project if needed
    run_command("railway create comment-analyzer", check=False)
    
    # Set environment variables
    run_command('railway env set FLASK_ENV=production')
    run_command('railway env set SECRET_KEY=your-secret-key-change-me')
    run_command('railway env set PORT=8080')
    
    # Deploy
    run_command("railway up")
    
    print("✅ Deployed to Railway!")
    print("Your app will be available at the URL shown above.")

def deploy_render():
    """Deploy to Render.com"""
    print("🎨 Deploying to Render...")
    print("📋 Manual steps for Render.com:")
    print("1. Go to https://render.com")
    print("2. Connect your GitHub account")
    print("3. Create 'New Web Service'")
    print("4. Select this repository")
    print("5. Choose 'Docker' environment")
    print("6. Set environment variables:")
    print("   - FLASK_ENV=production")
    print("   - SECRET_KEY=your-secret-key")
    print("   - PORT=8080")
    print("7. Click 'Create Web Service'")
    print("\n✅ Configuration files are ready in your repository!")

def deploy_fly():
    """Deploy to Fly.io"""
    print("🪰 Deploying to Fly.io...")
    
    # Check if Fly CLI is installed
    result = run_command("fly version", check=False)
    if result.returncode != 0:
        print("Installing Fly CLI...")
        if os.name == 'nt':  # Windows
            run_command("powershell -Command \"iwr https://fly.io/install.ps1 -useb | iex\"")
        else:  # Linux/Mac
            run_command("curl -L https://fly.io/install.sh | sh")
    
    # Login and deploy
    print("Please login to Fly.io:")
    run_command("fly auth login")
    
    # Launch app
    run_command("fly launch --name comment-analyzer --region ewr")
    
    # Set secrets
    run_command("fly secrets set FLASK_ENV=production SECRET_KEY=your-secret-key-change-me")
    
    # Deploy
    run_command("fly deploy")
    
    print("✅ Deployed to Fly.io!")

def deploy_vercel():
    """Deploy to Vercel"""
    print("⚡ Deploying to Vercel...")
    
    # Check if Vercel CLI is installed
    result = run_command("vercel --version", check=False)
    if result.returncode != 0:
        print("Installing Vercel CLI...")
        run_command("npm install -g vercel")
    
    # Login and deploy
    print("Please login to Vercel:")
    run_command("vercel login")
    
    # Deploy
    print("Deploying to Vercel...")
    run_command("vercel --prod")
    
    print("✅ Deployed to Vercel!")
    print("📝 Note: This is a demo version with limited functionality.")
    print("   For full processing, deploy to Railway or DigitalOcean.")

def deploy_digitalocean():
    """Deploy to DigitalOcean App Platform"""
    print("🌊 Deploying to DigitalOcean...")
    print("📋 Manual steps for DigitalOcean App Platform:")
    print("1. Go to https://cloud.digitalocean.com/apps")
    print("2. Click 'Create App'")
    print("3. Connect your GitHub repository")
    print("4. Select 'Autodeploy' for automatic updates")
    print("5. Choose 'Docker' as build method")
    print("6. Set environment variables:")
    print("   - FLASK_ENV=production")
    print("   - SECRET_KEY=your-secret-key")
    print("   - PORT=8080")
    print("7. Choose your plan (Basic $5/month recommended)")
    print("8. Click 'Create Resources'")
    print("\n✅ Your app will be deployed automatically!")

def test_local():
    """Test the application locally"""
    print("🧪 Testing locally...")
    
    if not check_docker():
        print("❌ Docker not found. Please install Docker first.")
        return
    
    # Build and run with Docker
    print("Building Docker image...")
    run_command("docker build -t comment-analyzer .")
    
    print("Starting local server...")
    print("📱 Your app will be available at: http://localhost:8080")
    print("Press Ctrl+C to stop")
    
    try:
        run_command("docker run -p 8080:8080 comment-analyzer")
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")

def main():
    """Main deployment interface"""
    print("🌐 Public Comment Analysis Tool - Cloud Deployment")
    print("=" * 60)
    
    if len(sys.argv) > 1:
        platform = sys.argv[1].lower()
    else:
        print("Available deployment options:")
        print("1. vercel     - Vercel (You have account, demo version)")
        print("2. railway    - Railway.app (Recommended for full version)")
        print("3. render     - Render.com (Free tier)")
        print("4. fly        - Fly.io (Global edge)")
        print("5. do         - DigitalOcean (Paid, reliable)")
        print("6. local      - Test locally with Docker")
        print()
        platform = input("Choose platform (1-6): ").strip()
    
    # Map choices
    platform_map = {
        '1': 'vercel',
        '2': 'railway',
        '3': 'render', 
        '4': 'fly',
        '5': 'do',
        '6': 'local',
        'vercel': 'vercel',
        'railway': 'railway',
        'render': 'render',
        'fly': 'fly',
        'do': 'do',
        'digitalocean': 'do',
        'local': 'local',
        'test': 'local'
    }
    
    platform = platform_map.get(platform)
    
    if platform == 'vercel':
        deploy_vercel()
    elif platform == 'railway':
        deploy_railway()
    elif platform == 'render':
        deploy_render()
    elif platform == 'fly':
        deploy_fly()
    elif platform == 'do':
        deploy_digitalocean()
    elif platform == 'local':
        test_local()
    else:
        print("❌ Invalid option. Please choose 1-6.")
        sys.exit(1)

if __name__ == "__main__":
    main()