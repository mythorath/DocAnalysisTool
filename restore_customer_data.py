#!/usr/bin/env python3
"""
Restore Customer Data After Railway Deploy
==========================================

Since Railway deployments create fresh containers, SQLite data is lost.
This script quickly restores your customer account and project data.
"""

import subprocess
import sys
import os

# Windows emoji compatibility
def safe_print(text):
    """Print text with emoji fallbacks for Windows."""
    if os.name == 'nt':  # Windows
        emoji_replacements = {
            '🔄': '[RESTORE]',
            '✅': '[OK]',
            '❌': '[ERROR]',
            '👤': '[USER]',
            '📊': '[PROJECT]',
            '🎯': '[TARGET]',
            '🚀': '[DEPLOY]',
        }
        for emoji, replacement in emoji_replacements.items():
            text = text.replace(emoji, replacement)
    print(text)

def run_command(cmd, description):
    """Run a remote_data_manager command."""
    safe_print(f"🔄 {description}...")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            safe_print(f"✅ {description} completed")
            # Print relevant output
            if "successful" in result.stdout or "OK" in result.stdout:
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if any(keyword in line for keyword in ['Email:', 'Password:', 'Database ID:', 'Documents:', 'Size:']):
                        safe_print(f"   {line.strip()}")
            return True
        else:
            safe_print(f"❌ {description} failed")
            safe_print(f"   Error: {result.stderr}")
            return False
    except Exception as e:
        safe_print(f"❌ {description} error: {e}")
        return False

def main():
    """Restore customer data after Railway deployment."""
    portal_url = "https://narrow-clocks-staging.up.railway.app"
    admin_key = "secure_admin_key_2024_changeme"
    
    # Customer details
    customer_email = "kathyb@upwork.com"
    customer_name = "Kathy B"
    customer_password = "CommentReview"
    
    # Project details
    database_path = "workspace/customers/kathyb@upwork.com/kathyb@upwork.com_20250806_151400/output/kathyb@upwork.com_20250806_151400.db"
    project_name = "First50CommentReview"
    
    safe_print("🚀 RAILWAY POST-DEPLOY DATA RESTORATION")
    safe_print("=" * 50)
    safe_print(f"🎯 Portal: {portal_url}")
    safe_print(f"👤 Customer: {customer_email}")
    safe_print(f"📊 Project: {project_name}")
    safe_print("")
    
    # Step 1: Create customer
    create_cmd = [
        'python', 'remote_data_manager.py',
        '--url', portal_url,
        '--key', admin_key,
        'create-customer', customer_email,
        '--name', customer_name,
        '--password', customer_password
    ]
    
    if not run_command(create_cmd, "Creating customer account"):
        safe_print("❌ Failed to create customer - aborting")
        return False
    
    # Step 2: Upload database
    upload_cmd = [
        'python', 'remote_data_manager.py',
        '--url', portal_url,
        '--key', admin_key,
        'upload', database_path, customer_email, project_name
    ]
    
    if not run_command(upload_cmd, "Uploading project database"):
        safe_print("❌ Failed to upload database - trying repair...")
        
        # Step 3: Repair database (in case of NULL ID issue)
        repair_cmd = [
            'python', 'remote_data_manager.py',
            '--url', portal_url,
            '--key', admin_key,
            'repair'
        ]
        
        if not run_command(repair_cmd, "Repairing database"):
            safe_print("❌ Database repair failed")
            return False
    
    # Step 4: Verify setup
    list_cmd = [
        'python', 'remote_data_manager.py',
        '--url', portal_url,
        '--key', admin_key,
        'list'
    ]
    
    safe_print("")
    safe_print("🔄 Verifying setup...")
    result = subprocess.run(list_cmd, capture_output=True, text=True, timeout=30)
    
    if result.returncode == 0 and "Total Projects: 1" in result.stdout:
        safe_print("✅ DATA RESTORATION COMPLETE!")
        safe_print("")
        safe_print("🎯 READY FOR USE:")
        safe_print(f"   Portal: {portal_url}")
        safe_print(f"   Email: {customer_email}")
        safe_print(f"   Password: {customer_password}")
        safe_print("")
        return True
    else:
        safe_print("❌ Verification failed - please check manually")
        return False

if __name__ == "__main__":
    main()
