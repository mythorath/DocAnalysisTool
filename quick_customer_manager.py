#!/usr/bin/env python3
"""
Quick Customer Manager - Instant customer operations without redeployment
=========================================================================

Fast API-based customer management for your Railway portal.
No redeployment needed - all operations happen instantly via API calls.
"""

import os
import sys
import subprocess
from pathlib import Path

# Windows emoji compatibility
def safe_print(text):
    """Print text with emoji fallbacks for Windows."""
    if os.name == 'nt':  # Windows
        emoji_replacements = {
            '🚀': '[ROCKET]',
            '✅': '[OK]',
            '❌': '[ERROR]',
            '⚡': '[FAST]',
            '📋': '[LIST]',
            '🗑️': '[DELETE]',
            '👤': '[USER]',
            '📊': '[STATS]',
            '🎯': '[TARGET]',
            '💾': '[SAVE]',
            '🔄': '[SYNC]',
            '📡': '[API]',
        }
        for emoji, replacement in emoji_replacements.items():
            text = text.replace(emoji, replacement)
    print(text)

class QuickCustomerManager:
    """Fast customer management without redeployment."""
    
    def __init__(self):
        self.portal_url = os.getenv('PORTAL_URL', 'https://narrow-clocks-production.up.railway.app')
        self.admin_key = os.getenv('ADMIN_API_KEY', 'secure_admin_key_2024_changeme')
        
    def run_api_command(self, action, *args):
        """Run a remote_data_manager command."""
        cmd = [
            'python', 'remote_data_manager.py',
            '--url', self.portal_url,
            '--key', self.admin_key,
            action
        ] + list(args)
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                safe_print(result.stdout)
                return True
            else:
                safe_print(f"❌ Error: {result.stderr}")
                return False
        except Exception as e:
            safe_print(f"❌ Command failed: {e}")
            return False
    
    def quick_upload(self, db_path, customer_email, project_name):
        """🚀 INSTANT: Upload database and auto-create customer."""
        safe_print(f"\n⚡ INSTANT UPLOAD (No Redeployment)")
        safe_print(f"📡 Database: {db_path}")
        safe_print(f"👤 Customer: {customer_email}")
        safe_print(f"📊 Project: {project_name}")
        safe_print("-" * 50)
        
        return self.run_api_command('upload', db_path, customer_email, project_name)
    
    def quick_list(self):
        """📋 INSTANT: List all customers and projects."""
        safe_print(f"\n⚡ INSTANT CUSTOMER LIST (No Redeployment)")
        safe_print("-" * 50)
        
        return self.run_api_command('list')
    
    def quick_remove_customer(self, customer_email):
        """🗑️ INSTANT: Remove customer and all their projects."""
        safe_print(f"\n⚡ INSTANT CUSTOMER REMOVAL (No Redeployment)")
        safe_print(f"👤 Removing: {customer_email}")
        safe_print("-" * 50)
        
        return self.run_api_command('remove-customer', customer_email)
    
    def quick_remove_project(self, customer_email, project_name):
        """🗑️ INSTANT: Remove specific project."""
        safe_print(f"\n⚡ INSTANT PROJECT REMOVAL (No Redeployment)")
        safe_print(f"👤 Customer: {customer_email}")
        safe_print(f"📊 Project: {project_name}")
        safe_print("-" * 50)
        
        return self.run_api_command('remove-project', customer_email, project_name)

def show_menu():
    """Show the quick operations menu."""
    safe_print("\n🎯 QUICK CUSTOMER MANAGER")
    safe_print("=" * 50)
    safe_print("⚡ INSTANT operations (No redeployment needed)")
    safe_print("")
    safe_print("1. 📋 List all customers")
    safe_print("2. 🚀 Upload database (auto-creates customer)")
    safe_print("3. 🗑️ Remove customer")
    safe_print("4. 🗑️ Remove project")
    safe_print("5. 💾 Exit")
    safe_print("")

def main():
    """Main interactive menu."""
    manager = QuickCustomerManager()
    
    safe_print("🎯 QUICK CUSTOMER MANAGER")
    safe_print("=" * 50)
    safe_print("⚡ All operations are INSTANT via API calls")
    safe_print("📡 No redeployment needed!")
    safe_print("")
    
    while True:
        show_menu()
        choice = input("Choose an option (1-5): ").strip()
        
        if choice == "1":
            manager.quick_list()
            
        elif choice == "2":
            safe_print("\n🚀 Upload Database")
            safe_print("-" * 30)
            
            # Show available databases
            workspace_path = Path("workspace/customers")
            if workspace_path.exists():
                safe_print("📋 Available databases:")
                db_files = list(workspace_path.rglob("*.db"))
                for i, db_file in enumerate(db_files, 1):
                    safe_print(f"   {i}. {db_file}")
                
                if db_files:
                    try:
                        db_choice = int(input(f"\nSelect database (1-{len(db_files)}) or enter path: "))
                        if 1 <= db_choice <= len(db_files):
                            db_path = str(db_files[db_choice - 1])
                        else:
                            db_path = input("Enter database path: ").strip()
                    except ValueError:
                        db_path = input("Enter database path: ").strip()
                else:
                    db_path = input("Enter database path: ").strip()
            else:
                db_path = input("Enter database path: ").strip()
            
            customer_email = input("Customer email: ").strip()
            project_name = input("Project name: ").strip()
            
            if db_path and customer_email and project_name:
                manager.quick_upload(db_path, customer_email, project_name)
            else:
                safe_print("❌ Missing required information")
                
        elif choice == "3":
            safe_print("\n🗑️ Remove Customer")
            safe_print("-" * 30)
            customer_email = input("Customer email to remove: ").strip()
            if customer_email:
                confirm = input(f"⚠️ Really remove {customer_email}? (yes/no): ").strip().lower()
                if confirm == 'yes':
                    manager.quick_remove_customer(customer_email)
                else:
                    safe_print("❌ Cancelled")
            
        elif choice == "4":
            safe_print("\n🗑️ Remove Project")
            safe_print("-" * 30)
            customer_email = input("Customer email: ").strip()
            project_name = input("Project name: ").strip()
            if customer_email and project_name:
                confirm = input(f"⚠️ Really remove project '{project_name}' from {customer_email}? (yes/no): ").strip().lower()
                if confirm == 'yes':
                    manager.quick_remove_project(customer_email, project_name)
                else:
                    safe_print("❌ Cancelled")
                    
        elif choice == "5":
            safe_print("✅ Goodbye!")
            break
            
        else:
            safe_print("❌ Invalid choice")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()
