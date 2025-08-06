#!/usr/bin/env python3
"""
Interactive Document Analysis Platform Manager
A simple UI to manage all operations without remembering commands.
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from datetime import datetime

# Windows console emoji compatibility
def safe_print(text):
    """Print text with emoji fallbacks for Windows console."""
    if os.name == 'nt':
        # Replace problematic emojis with ASCII equivalents
        text = (text.replace('🚀', '[START]')
                   .replace('📍', '[LOCATION]')
                   .replace('🕒', '[TIME]')
                   .replace('📄', '[DOCS]')
                   .replace('👤', '[USER]')
                   .replace('🌐', '[WEB]')
                   .replace('⚙️', '[SYSTEM]')
                   .replace('📚', '[HELP]')
                   .replace('🚪', '[EXIT]')
                   .replace('✅', '[OK]')
                   .replace('❌', '[ERROR]')
                   .replace('⚠️', '[WARNING]')
                   .replace('📁', '[FILES]')
                   .replace('📊', '[DATA]')
                   .replace('🔧', '[TOOL]')
                   .replace('💻', '[CMD]')
                   .replace('📤', '[UPLOAD]')
                   .replace('📋', '[LIST]')
                   .replace('🗑️', '[DELETE]')
                   .replace('❓', '[QUESTION]')
                   .replace('🎉', '[SUCCESS]')
                   .replace('💡', '[TIP]')
                   .replace('🔐', '[SECURE]')
                   .replace('📂', '[FOLDER]')
                   .replace('📈', '[COUNT]')
                   .replace('🧹', '[CLEANUP]')
                   .replace('⬅️', '[BACK]')
                   .replace('🆕', '[NEW]')
                   .replace('🧪', '[TEST]')
                   .replace('👥', '[USERS]')
                   .replace('📧', '[EMAIL]')
                   .replace('🚂', '[RAILWAY]'))
    try:
        print(text)
    except UnicodeEncodeError:
        # Final fallback - remove all non-ASCII characters
        print(text.encode('ascii', 'ignore').decode('ascii'))

class InteractiveManager:
    def __init__(self):
        self.portal_url = "https://narrow-clocks-production.up.railway.app"
        self.admin_key = "secure_admin_key_2024_changeme"
        
    def clear_screen(self):
        """Clear the terminal screen."""
        os.system('cls' if os.name == 'nt' else 'clear')
        
    def show_header(self):
        """Show the main header."""
        safe_print("🚀 Document Analysis Platform Manager")
        print("=" * 60)
        safe_print(f"📍 Portal: {self.portal_url}")
        safe_print(f"🕒 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
    def run_command(self, command, description=None):
        """Run a command and show results."""
        if description:
            safe_print(f"\n🔧 {description}")
            safe_print(f"💻 Running: {command}")
            print("-" * 40)
        
        try:
            if os.name == 'nt':  # Windows
                result = subprocess.run(command, shell=True, capture_output=True, text=True, cwd=os.getcwd())
            else:  # Unix/Linux
                result = subprocess.run(command, shell=True, capture_output=True, text=True, cwd=os.getcwd())
            
            if result.stdout:
                print(result.stdout)
            if result.stderr and result.returncode != 0:
                safe_print(f"❌ Error: {result.stderr}")
                
            return result.returncode == 0
            
        except Exception as e:
            safe_print(f"❌ Error running command: {e}")
            return False
    
    def get_input(self, prompt, default=None):
        """Get user input with optional default."""
        if default:
            full_prompt = f"{prompt} [{default}]: "
        else:
            full_prompt = f"{prompt}: "
            
        value = input(full_prompt).strip()
        return value if value else default
    
    def list_csv_files(self):
        """List available CSV files."""
        input_dir = Path("input")
        if not input_dir.exists():
            return []
        return [f.name for f in input_dir.glob("*.csv")]
    
    def list_databases(self):
        """List available database files."""
        workspace_dir = Path("workspace")
        databases = []
        
        if workspace_dir.exists():
            for db_file in workspace_dir.rglob("*.db"):
                relative_path = str(db_file.relative_to(Path(".")))
                databases.append(relative_path)
        
        return databases
    
    def document_processing_menu(self):
        """Handle document processing operations."""
        while True:
            self.clear_screen()
            self.show_header()
            safe_print("📄 DOCUMENT PROCESSING")
            print("=" * 60)
            
            # Show available CSV files
            csv_files = self.list_csv_files()
            if csv_files:
                print("📁 Available CSV files:")
                for i, file in enumerate(csv_files, 1):
                    print(f"   {i}. {file}")
            else:
                safe_print("❌ No CSV files found in input/ directory")
            
            print("\nOptions:")
            print("1. Process documents from CSV")
            print("2. Process with GPU acceleration")
            print("3. List processed projects")
            print("0. Back to main menu")
            
            choice = input("\nEnter choice: ").strip()
            
            if choice == "0":
                break
            elif choice == "1":
                self.process_documents(gpu=False)
            elif choice == "2":
                self.process_documents(gpu=True)
            elif choice == "3":
                self.list_projects()
            else:
                safe_print("❌ Invalid choice")
                input("Press Enter to continue...")
    
    def process_documents(self, gpu=False):
        """Process documents from CSV."""
        safe_print(f"\n📄 Process Documents {'(GPU)' if gpu else '(CPU)'}")
        print("-" * 40)
        
        # Select CSV file
        csv_files = self.list_csv_files()
        if not csv_files:
            safe_print("❌ No CSV files found in input/ directory")
            input("Press Enter to continue...")
            return
        
        if len(csv_files) == 1:
            csv_file = csv_files[0]
            safe_print(f"📁 Using: {csv_file}")
        else:
            safe_print("📁 Select CSV file:")
            for i, file in enumerate(csv_files, 1):
                print(f"   {i}. {file}")
            
            try:
                choice = int(input("Enter number: ")) - 1
                csv_file = csv_files[choice]
            except (ValueError, IndexError):
                safe_print("❌ Invalid selection")
                input("Press Enter to continue...")
                return
        
        # Get customer selection
        safe_print("\n👤 Customer Selection")
        print("-" * 40)
        
        # Get local customers from workspace
        local_customers = self.get_local_customers()
        
        customer_options = []
        if local_customers:
            customer_options.extend(local_customers)
        
        # Add special options
        customer_options.extend(["[New Customer]", "[Test Run - No Customer]"])
        
        safe_print("📋 Available options:")
        for i, option in enumerate(customer_options, 1):
            if option == "[New Customer]":
                safe_print(f"   {i}. 🆕 {option}")
            elif option == "[Test Run - No Customer]":
                safe_print(f"   {i}. 🧪 {option}")
            else:
                safe_print(f"   {i}. 👤 {option}")
        
        try:
            customer_choice = int(input("Select customer option: ")) - 1
            if 0 <= customer_choice < len(customer_options):
                selected_option = customer_options[customer_choice]
                
                if selected_option == "[New Customer]":
                    customer = self.get_input("New customer name", "Customer")
                elif selected_option == "[Test Run - No Customer]":
                    customer = "test"
                else:
                    customer = selected_option
            else:
                safe_print("❌ Invalid selection")
                input("Press Enter to continue...")
                return
        except (ValueError, IndexError):
            safe_print("❌ Invalid selection")
            input("Press Enter to continue...")
            return
        
        if not customer:
            safe_print("❌ Customer name is required")
            input("Press Enter to continue...")
            return
        
        project = self.get_input("Project name", "Project")
        
        # Build command
        gpu_flag = " --gpu" if gpu else ""
        command = f'python local_processor_lite.py process "input/{csv_file}" --customer "{customer}" --project "{project}"{gpu_flag}'
        
        # Run processing
        success = self.run_command(command, f"Processing {csv_file}")
        
        if success:
            safe_print(f"\n✅ Processing complete!")
            safe_print(f"📊 Customer: {customer}")
            safe_print(f"📁 Project: {project}")
            
            # Show next steps based on customer type
            if customer == "test":
                safe_print("\n💡 Test run completed - data stored locally only")
            else:
                safe_print(f"\n💡 Next steps:")
                safe_print(f"   📤 Upload to portal: Remote Management → Push database")
                safe_print(f"   🔍 View locally: Option 2 → List projects")
        
        input("\nPress Enter to continue...")
    
    def list_projects(self):
        """List processed projects."""
        command = "python local_processor_lite.py list"
        self.run_command(command, "Listing processed projects")
        input("\nPress Enter to continue...")
    
    def customer_management_menu(self):
        """Handle customer management operations."""
        while True:
            self.clear_screen()
            self.show_header()
            print("👤 CUSTOMER MANAGEMENT")
            print("=" * 60)
            print("Options:")
            print("1. Create new customer")
            print("2. List customers")
            print("3. List customer projects")
            print("4. Upload database to portal")
            print("0. Back to main menu")
            
            choice = input("\nEnter choice: ").strip()
            
            if choice == "0":
                break
            elif choice == "1":
                self.create_customer()
            elif choice == "2":
                self.list_customers()
            elif choice == "3":
                self.list_customer_projects()
            elif choice == "4":
                self.upload_database()
            else:
                safe_print("❌ Invalid choice")
                input("Press Enter to continue...")
    
    def create_customer(self):
        """Create a new customer."""
        print("\n👤 Create New Customer")
        print("-" * 40)
        
        email = self.get_input("Customer email")
        name = self.get_input("Customer name")
        password = self.get_input("Customer password", "password123")
        organization = self.get_input("Organization", "")
        
        if not email or not name:
            print("❌ Email and name are required")
            input("Press Enter to continue...")
            return
        
        # Build command
        org_flag = f' --organization "{organization}"' if organization else ""
        command = f'python upload_customer_data.py create-customer "{email}" "{name}" "{password}"{org_flag}'
        
        success = self.run_command(command, "Creating customer")
        
        if success:
            print(f"\n✅ Customer created successfully!")
            print(f"📧 Email: {email}")
            print(f"🔑 Password: {password}")
        
        input("\nPress Enter to continue...")
    
    def list_customers(self):
        """List all customers."""
        command = "python upload_customer_data.py list-customers"
        self.run_command(command, "Listing customers")
        input("\nPress Enter to continue...")
    
    def list_customer_projects(self):
        """List customer projects."""
        command = "python upload_customer_data.py list-projects"
        self.run_command(command, "Listing customer projects")
        input("\nPress Enter to continue...")
    
    def upload_database(self):
        """Upload database to portal."""
        print("\n📤 Upload Database to Portal")
        print("-" * 40)
        
        # Show available databases
        databases = self.list_databases()
        if not databases:
            print("❌ No database files found in workspace/")
            input("Press Enter to continue...")
            return
        
        print("📁 Available databases:")
        for i, db in enumerate(databases, 1):
            print(f"   {i}. {db}")
        
        try:
            choice = int(input("Select database: ")) - 1
            database = databases[choice]
        except (ValueError, IndexError):
            print("❌ Invalid selection")
            input("Press Enter to continue...")
            return
        
        email = self.get_input("Customer email")
        project = self.get_input("Project name")
        description = self.get_input("Description (optional)", "")
        
        if not email or not project:
            print("❌ Email and project name are required")
            input("Press Enter to continue...")
            return
        
        # Build command
        desc_flag = f' --description "{description}"' if description else ""
        command = f'python upload_customer_data.py upload "{database}" "{email}" "{project}"{desc_flag}'
        
        success = self.run_command(command, "Uploading database")
        
        if success:
            print(f"\n✅ Database uploaded successfully!")
            print(f"📊 Project: {project}")
            print(f"👤 Customer: {email}")
        
        input("\nPress Enter to continue...")
    
    def customer_management_menu(self):
        """Handle customer management operations (remote portal control)."""
        while True:
            self.clear_screen()
            self.show_header()
            safe_print("👤 CUSTOMER MANAGEMENT")
            print("=" * 60)
            safe_print("💡 Manages customers directly on the remote portal")
            print()
            print("Options:")
            print("1. List customers on portal")
            print("2. Create customer account")
            print("3. Remove customer from portal")
            print("4. List customer projects")
            print("5. Remove customer project")
            print("6. Upload database to customer")
            print("0. Back to main menu")
            
            choice = input("\nEnter choice: ").strip()
            
            if choice == "0":
                break
            elif choice == "1":
                self.list_portal_customers()
            elif choice == "2":
                self.create_portal_customer()
            elif choice == "3":
                self.remove_portal_customer()
            elif choice == "4":
                self.list_customer_projects()
            elif choice == "5":
                self.remove_customer_project()
            elif choice == "6":
                self.upload_database_to_customer()
            else:
                safe_print("❌ Invalid choice")
                input("Press Enter to continue...")
    
    def list_portal_customers(self):
        """List all customers on the portal."""
        safe_print("\n📋 Portal Customers")
        print("-" * 30)
        
        command = f'python remote_data_manager.py --url {self.portal_url} --key {self.admin_key} list'
        self.run_command(command, "Listing portal customers")
        input("\nPress Enter to continue...")
    
    def create_portal_customer(self):
        """Create a new customer account on the portal."""
        safe_print("\n🆕 Create Customer Account")
        print("-" * 30)
        
        email = self.get_input("Customer email")
        password = self.get_input("Customer password", "password123")
        
        if not email:
            safe_print("❌ Email is required")
            input("Press Enter to continue...")
            return
        
        safe_print(f"\n📧 Creating customer: {email}")
        safe_print("⚠️ Note: Customer creation requires direct portal API access")
        safe_print("💡 For now, customers will be created when first database is uploaded")
        
        input("\nPress Enter to continue...")
    
    def remove_portal_customer(self):
        """Remove a customer from the portal."""
        safe_print("\n🗑️ Remove Customer from Portal")
        print("-" * 30)
        safe_print("⚠️ This will remove ALL projects for this customer!")
        
        # Get customers from portal first
        customers = self.get_portal_customers()
        if customers:
            safe_print("📋 Available customers:")
            for i, customer in enumerate(customers, 1):
                print(f"   {i}. {customer}")
            print(f"   {len(customers) + 1}. Enter custom email")
            
            try:
                customer_choice = int(input("Select customer to remove: ")) - 1
                if 0 <= customer_choice < len(customers):
                    email = customers[customer_choice]
                elif customer_choice == len(customers):
                    email = self.get_input("Customer email")
                else:
                    safe_print("❌ Invalid selection")
                    input("Press Enter to continue...")
                    return
            except (ValueError, IndexError):
                safe_print("❌ Invalid selection")
                input("Press Enter to continue...")
                return
        else:
            email = self.get_input("Customer email")
        
        if not email:
            safe_print("❌ Email is required")
            input("Press Enter to continue...")
            return
        
        confirm = input(f"❓ Remove customer {email} and ALL their data? (y/N): ").strip().lower()
        if confirm != 'y':
            safe_print("❌ Cancelled")
            input("Press Enter to continue...")
            return
        
        command = f'python remote_data_manager.py --url {self.portal_url} --key {self.admin_key} remove-customer "{email}"'
        success = self.run_command(command, f"Removing customer {email}")
        
        if success:
            safe_print(f"\n✅ Customer {email} removed successfully!")
        
        input("\nPress Enter to continue...")
    
    def list_customer_projects(self):
        """List projects for a specific customer."""
        safe_print("\n📄 Customer Projects")
        print("-" * 30)
        
        # Get customers from portal first
        customers = self.get_portal_customers()
        if customers:
            safe_print("📋 Available customers:")
            for i, customer in enumerate(customers, 1):
                print(f"   {i}. {customer}")
            
            try:
                customer_choice = int(input("Select customer: ")) - 1
                if 0 <= customer_choice < len(customers):
                    email = customers[customer_choice]
                else:
                    safe_print("❌ Invalid selection")
                    input("Press Enter to continue...")
                    return
            except (ValueError, IndexError):
                safe_print("❌ Invalid selection")
                input("Press Enter to continue...")
                return
        else:
            email = self.get_input("Customer email")
        
        if not email:
            safe_print("❌ Email is required")
            input("Press Enter to continue...")
            return
        
        safe_print(f"\n📊 Projects for {email}:")
        command = f'python remote_data_manager.py --url {self.portal_url} --key {self.admin_key} list'
        self.run_command(command, f"Listing projects for {email}")
        
        input("\nPress Enter to continue...")
    
    def remove_customer_project(self):
        """Remove a specific project from a customer."""
        safe_print("\n🗑️ Remove Customer Project")
        print("-" * 30)
        
        # Get customers from portal first
        customers = self.get_portal_customers()
        if customers:
            safe_print("📋 Available customers:")
            for i, customer in enumerate(customers, 1):
                print(f"   {i}. {customer}")
            
            try:
                customer_choice = int(input("Select customer: ")) - 1
                if 0 <= customer_choice < len(customers):
                    email = customers[customer_choice]
                else:
                    safe_print("❌ Invalid selection")
                    input("Press Enter to continue...")
                    return
            except (ValueError, IndexError):
                safe_print("❌ Invalid selection")
                input("Press Enter to continue...")
                return
        else:
            email = self.get_input("Customer email")
        
        project = self.get_input("Project name")
        
        if not email or not project:
            safe_print("❌ Email and project name are required")
            input("Press Enter to continue...")
            return
        
        confirm = input(f"❓ Remove project '{project}' from {email}? (y/N): ").strip().lower()
        if confirm != 'y':
            safe_print("❌ Cancelled")
            input("Press Enter to continue...")
            return
        
        command = f'python remote_data_manager.py --url {self.portal_url} --key {self.admin_key} remove-project "{email}" "{project}"'
        success = self.run_command(command, f"Removing project {project}")
        
        if success:
            safe_print(f"\n✅ Project '{project}' removed successfully!")
        
        input("\nPress Enter to continue...")
    
    def upload_database_to_customer(self):
        """Upload a database to a specific customer (same as push to portal)."""
        safe_print("\n📤 Upload Database to Customer")
        print("-" * 30)
        safe_print("💡 This uploads processed data to the customer's portal account")
        
        # Reuse the existing push to portal functionality
        self.push_to_portal()
    
    def remote_management_menu(self):
        """Handle remote site management."""
        while True:
            self.clear_screen()
            self.show_header()
            print("🌐 REMOTE SITE MANAGEMENT")
            print("=" * 60)
            print("Options:")
            print("1. Test connection to portal")
            print("2. List data on portal")
            print("3. Push database to portal")
            print("4. Remove project from portal")
            print("5. Remove customer from portal")
            print("6. Sync all local data to portal")
            print("7. Deploy/Update Railway site")
            print("0. Back to main menu")
            
            choice = input("\nEnter choice: ").strip()
            
            if choice == "0":
                break
            elif choice == "1":
                self.test_portal_connection()
            elif choice == "2":
                self.list_remote_data()
            elif choice == "3":
                self.push_to_portal()
            elif choice == "4":
                self.remove_remote_project()
            elif choice == "5":
                self.remove_remote_customer()
            elif choice == "6":
                self.sync_to_portal()
            elif choice == "7":
                self.deploy_update_railway()
            else:
                safe_print("❌ Invalid choice")
                input("Press Enter to continue...")
    
    def test_portal_connection(self):
        """Test connection to the portal."""
        command = f'python remote_data_manager.py --url {self.portal_url} --key {self.admin_key} test'
        self.run_command(command, "Testing portal connection")
        input("\nPress Enter to continue...")
    
    def list_remote_data(self):
        """List data on the remote portal."""
        command = f'python remote_data_manager.py --url {self.portal_url} --key {self.admin_key} list'
        self.run_command(command, "Listing remote portal data")
        input("\nPress Enter to continue...")
    
    def get_local_customers(self):
        """Get list of local customers from workspace."""
        try:
            import os
            from pathlib import Path
            
            workspace_dir = Path("workspace/customers")
            if not workspace_dir.exists():
                return []
            
            customers = []
            for customer_dir in workspace_dir.iterdir():
                if customer_dir.is_dir() and not customer_dir.name.startswith('.'):
                    customers.append(customer_dir.name)
            
            return sorted(customers)
        except Exception as e:
            safe_print(f"⚠️ Could not fetch local customers: {e}")
            return []
    
    def get_portal_customers(self):
        """Get list of customers from the portal."""
        try:
            import subprocess
            
            # Run remote data manager to get customer list
            result = subprocess.run([
                'python', 'remote_data_manager.py', 
                '--url', self.portal_url, 
                '--key', self.admin_key,
                'list'
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                # Parse the output to extract customer emails
                output = result.stdout
                
                # Look for email patterns in the output
                import re
                email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
                found_emails = re.findall(email_pattern, output, re.IGNORECASE)
                
                # Remove duplicates and return unique emails
                unique_emails = list(set(found_emails))
                return sorted(unique_emails)
            else:
                return []
        except Exception as e:
            safe_print(f"⚠️ Could not fetch customers: {e}")
            return []
    
    def push_to_portal(self):
        """Push database to portal."""
        safe_print("\n📤 Push Database to Portal")
        print("-" * 40)
        
        databases = self.list_databases()
        if not databases:
            safe_print("❌ No database files found")
            input("Press Enter to continue...")
            return
        
        safe_print("📁 Available databases:")
        for i, db in enumerate(databases, 1):
            print(f"   {i}. {db}")
        
        try:
            choice = int(input("Select database: ")) - 1
            database = databases[choice]
        except (ValueError, IndexError):
            safe_print("❌ Invalid selection")
            input("Press Enter to continue...")
            return
        
        # Get customers from portal
        safe_print("\n👥 Fetching customers from portal...")
        customers = self.get_portal_customers()
        
        if customers:
            safe_print("📋 Available customers:")
            for i, customer in enumerate(customers, 1):
                print(f"   {i}. {customer}")
            print(f"   {len(customers) + 1}. Enter custom email")
            
            try:
                customer_choice = int(input("Select customer: ")) - 1
                if 0 <= customer_choice < len(customers):
                    email = customers[customer_choice]
                elif customer_choice == len(customers):
                    email = self.get_input("Customer email")
                else:
                    safe_print("❌ Invalid selection")
                    input("Press Enter to continue...")
                    return
            except (ValueError, IndexError):
                safe_print("❌ Invalid selection")
                input("Press Enter to continue...")
                return
        else:
            safe_print("⚠️ Could not fetch customers from portal")
            email = self.get_input("Customer email")
        
        project = self.get_input("Project name")
        
        if not email or not project:
            safe_print("❌ Email and project name are required")
            input("Press Enter to continue...")
            return
        
        command = f'python remote_data_manager.py --url {self.portal_url} --key {self.admin_key} upload "{database}" "{email}" "{project}"'
        
        success = self.run_command(command, "Pushing to portal")
        
        if success:
            safe_print(f"\n✅ Database pushed to portal successfully!")
        
        input("\nPress Enter to continue...")
    
    def remove_remote_project(self):
        """Remove project from portal."""
        print("\n🗑️ Remove Project from Portal")
        print("-" * 40)
        
        email = self.get_input("Customer email")
        project = self.get_input("Project name")
        
        if not email or not project:
            print("❌ Email and project name are required")
            input("Press Enter to continue...")
            return
        
        confirm = input(f"❓ Remove project '{project}' for {email}? (y/N): ").strip().lower()
        if confirm != 'y':
            print("❌ Cancelled")
            input("Press Enter to continue...")
            return
        
        command = f'python remote_data_manager.py --url {self.portal_url} --key {self.admin_key} remove-project "{email}" "{project}"'
        
        success = self.run_command(command, "Removing project from portal")
        
        if success:
            print(f"\n✅ Project removed successfully!")
        
        input("\nPress Enter to continue...")
    
    def remove_remote_customer(self):
        """Remove customer from portal."""
        print("\n🗑️ Remove Customer from Portal")
        print("-" * 40)
        print("⚠️ This will remove ALL projects for this customer!")
        
        email = self.get_input("Customer email")
        
        if not email:
            print("❌ Email is required")
            input("Press Enter to continue...")
            return
        
        confirm = input(f"❓ Remove customer {email} and ALL their data? (y/N): ").strip().lower()
        if confirm != 'y':
            print("❌ Cancelled")
            input("Press Enter to continue...")
            return
        
        confirm2 = input("❓ Are you absolutely sure? Type 'DELETE': ").strip()
        if confirm2 != 'DELETE':
            print("❌ Cancelled")
            input("Press Enter to continue...")
            return
        
        command = f'python remote_data_manager.py --url {self.portal_url} --key {self.admin_key} remove-customer "{email}"'
        
        success = self.run_command(command, "Removing customer from portal")
        
        if success:
            print(f"\n✅ Customer removed successfully!")
        
        input("\nPress Enter to continue...")
    
    def sync_to_portal(self):
        """Sync all local data to portal."""
        command = f'python remote_data_manager.py --url {self.portal_url} --key {self.admin_key} sync'
        self.run_command(command, "Syncing local data to portal")
        input("\nPress Enter to continue...")
    
    def deploy_update_railway(self):
        """Deploy or update the Railway site."""
        safe_print("\n🚂 Railway Deployment/Update")
        print("-" * 40)
        
        # Check Railway CLI
        try:
            import subprocess
            # Try different ways to find Railway CLI
            railway_commands = ['railway', 'railway.exe', 'npx railway']
            railway_found = False
            
            for cmd in railway_commands:
                try:
                    cmd_list = cmd.split() + ['--version']
                    result = subprocess.run(cmd_list, capture_output=True, text=True, timeout=10, shell=True)
                    if result.returncode == 0:
                        railway_found = True
                        self.railway_cmd = cmd.split()[0]  # Store the working command
                        break
                except:
                    continue
            
            if not railway_found:
                safe_print("❌ Railway CLI not found!")
                safe_print("💡 Install with: npm install -g @railway/cli")
                safe_print("🌐 Or visit: https://railway.app/cli")
                input("Press Enter to continue...")
                return
        except Exception as e:
            safe_print(f"❌ Error checking Railway CLI: {e}")
            input("Press Enter to continue...")
            return
        
        safe_print("✅ Railway CLI found")
        
        # Show deployment options
        safe_print("\n📋 Deployment Options:")
        print("   1. Quick Deploy (current code)")
        print("   2. Full Setup (create new project)")
        print("   3. Update existing deployment")
        print("   4. Manual deployment (step-by-step instructions)")
        print("   0. Cancel")
        
        try:
            deploy_choice = int(input("\nSelect option: "))
        except ValueError:
            safe_print("❌ Invalid selection")
            input("Press Enter to continue...")
            return
        
        if deploy_choice == 0:
            safe_print("❌ Deployment cancelled")
            input("Press Enter to continue...")
            return
        elif deploy_choice == 1:
            self.quick_railway_deploy()
        elif deploy_choice == 2:
            self.full_railway_setup()
        elif deploy_choice == 3:
            self.update_railway_deployment()
        elif deploy_choice == 4:
            self.show_manual_deployment()
        else:
            safe_print("❌ Invalid selection")
            input("Press Enter to continue...")
    
    def quick_railway_deploy(self):
        """Quick deployment to existing Railway project."""
        safe_print("\n🚀 Quick Railway Deploy")
        print("-" * 30)
        
        # Deploy current code
        safe_print("📤 Deploying current code to Railway...")
        success = self.run_command(f"{getattr(self, 'railway_cmd', 'railway')} up --detach", "Railway deployment")
        
        if success:
            safe_print("\n✅ Deployment initiated!")
            safe_print("🔍 Getting deployment URL...")
            
            # Try to get the URL
            try:
                import subprocess
                railway_cmd = getattr(self, 'railway_cmd', 'railway')
                result = subprocess.run([railway_cmd, 'domain'], capture_output=True, text=True, timeout=30, shell=True)
                if result.returncode == 0 and result.stdout.strip():
                    url = result.stdout.strip()
                    safe_print(f"🌐 Site URL: {url}")
                    
                    # Update the portal URL in the manager
                    if url.startswith('http'):
                        self.portal_url = url
                        safe_print(f"📍 Portal URL updated: {self.portal_url}")
                else:
                    safe_print("⚠️ Could not get URL automatically")
                    safe_print("🔍 Check Railway dashboard for deployment URL")
            except Exception as e:
                safe_print(f"⚠️ Error getting URL: {e}")
        
        input("\nPress Enter to continue...")
    
    def full_railway_setup(self):
        """Full Railway setup with new project."""
        safe_print("\n🚂 Full Railway Setup")
        print("-" * 30)
        
        safe_print("🔧 Running complete Railway setup...")
        success = self.run_command("python railway_deploy.py", "Railway setup")
        
        if success:
            safe_print("\n✅ Setup complete!")
            safe_print("📋 Next steps:")
            safe_print("   1. Check Railway dashboard for URL")
            safe_print("   2. Update portal URL in this manager")
            safe_print("   3. Test the deployed site")
        
        input("\nPress Enter to continue...")
    
    def update_railway_deployment(self):
        """Update existing Railway deployment."""
        safe_print("\n🔄 Update Railway Deployment")
        print("-" * 30)
        
        # Check if we're in a Railway project
        try:
            import subprocess
            railway_cmd = getattr(self, 'railway_cmd', 'railway')
            result = subprocess.run([railway_cmd, 'status'], capture_output=True, text=True, timeout=10, shell=True)
            if result.returncode != 0:
                safe_print("❌ Not in a Railway project!")
                safe_print("💡 Use 'Full Setup' option to create a new project")
                input("Press Enter to continue...")
                return
        except Exception as e:
            safe_print(f"❌ Error checking Railway status: {e}")
            input("Press Enter to continue...")
            return
        
        safe_print("✅ Railway project detected")
        
        # Update environment variables
        safe_print("⚙️ Updating environment variables...")
        railway_cmd = getattr(self, 'railway_cmd', 'railway')
        env_commands = [
            f'{railway_cmd} variables --set ADMIN_API_KEY="secure_admin_key_2024_changeme"',
            f'{railway_cmd} variables --set HOST="0.0.0.0"',
            f'{railway_cmd} variables --set PORT="8080"'
        ]
        
        for cmd in env_commands:
            self.run_command(cmd, "Setting environment variable")
        
        # Deploy
        safe_print("📤 Deploying updated code...")
        success = self.run_command(f"{railway_cmd} up --detach", "Railway deployment")
        
        if success:
            safe_print("\n✅ Update deployment initiated!")
            safe_print("⏱️ Check Railway dashboard for deployment progress")
        
        input("\nPress Enter to continue...")
    
    def show_manual_deployment(self):
        """Show manual deployment instructions."""
        safe_print("\n📋 Manual Railway Deployment")
        print("-" * 40)
        
        safe_print("🔧 Follow these steps in your terminal:")
        print()
        safe_print("1. 📤 Deploy Current Code:")
        print("   railway up --detach")
        print()
        safe_print("2. ⚙️ Set Environment Variables:")
        print('   railway variables --set ADMIN_API_KEY="secure_admin_key_2024_changeme"')
        print('   railway variables --set HOST="0.0.0.0"')
        print('   railway variables --set PORT="8080"')
        print()
        safe_print("3. 🌐 Get Site URL:")
        print("   railway domain")
        print()
        safe_print("4. 📊 Check Status:")
        print("   railway status")
        print("   railway logs")
        print()
        safe_print("💡 Tips:")
        print("   - Each command should be run separately")
        print("   - Wait for deployment to complete before checking status")
        print("   - Use 'railway logs' to debug any issues")
        print(f"   - Current portal URL: {self.portal_url}")
        
        input("\nPress Enter to continue...")
    
    def system_management_menu(self):
        """Handle system management operations."""
        while True:
            self.clear_screen()
            self.show_header()
            print("⚙️ SYSTEM MANAGEMENT")
            print("=" * 60)
            print("Options:")
            print("1. Run customer portal locally")
            print("2. Install GPU support")
            print("3. Deploy to Railway")
            print("4. Check system status")
            print("5. Clean up local data")
            print("0. Back to main menu")
            
            choice = input("\nEnter choice: ").strip()
            
            if choice == "0":
                break
            elif choice == "1":
                self.run_local_portal()
            elif choice == "2":
                self.install_gpu_support()
            elif choice == "3":
                self.deploy_to_railway()
            elif choice == "4":
                self.check_system_status()
            elif choice == "5":
                self.cleanup_local_data()
            else:
                safe_print("❌ Invalid choice")
                input("Press Enter to continue...")
    
    def run_local_portal(self):
        """Run the customer portal locally."""
        print("\n🌐 Starting Local Customer Portal")
        print("-" * 40)
        print("💡 Portal will run at http://127.0.0.1:5000")
        print("🔐 Use customers you've created to log in")
        print("⏹️ Press Ctrl+C to stop the portal")
        input("\nPress Enter to start (Ctrl+C to stop)...")
        
        command = "python customer_portal_lite.py"
        self.run_command(command, "Starting customer portal")
    
    def install_gpu_support(self):
        """Install GPU support."""
        command = "python install_gpu_support.py"
        self.run_command(command, "Installing GPU support")
        input("\nPress Enter to continue...")
    
    def deploy_to_railway(self):
        """Deploy to Railway."""
        print("\n🚂 Deploy to Railway")
        print("-" * 40)
        
        confirm = input("❓ Deploy current version to Railway? (y/N): ").strip().lower()
        if confirm != 'y':
            print("❌ Cancelled")
            input("Press Enter to continue...")
            return
        
        command = "railway up --detach"
        success = self.run_command(command, "Deploying to Railway")
        
        if success:
            print(f"\n✅ Deployment started!")
            print(f"🌐 Portal URL: {self.portal_url}")
        
        input("\nPress Enter to continue...")
    
    def check_system_status(self):
        """Check system status."""
        print("\n⚙️ System Status")
        print("-" * 40)
        
        # Check Python
        print(f"🐍 Python: {sys.version}")
        
        # Check virtual environment
        if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
            print("✅ Virtual environment: Active")
        else:
            print("⚠️ Virtual environment: Not active")
        
        # Check key files
        key_files = [
            "local_processor_lite.py",
            "customer_portal_lite.py", 
            "remote_data_manager.py",
            "upload_customer_data.py"
        ]
        
        for file in key_files:
            if Path(file).exists():
                print(f"✅ {file}: Found")
            else:
                print(f"❌ {file}: Missing")
        
        # Check directories
        key_dirs = ["input", "workspace", "templates"]
        for dir_name in key_dirs:
            if Path(dir_name).exists():
                print(f"✅ {dir_name}/: Found")
            else:
                print(f"❌ {dir_name}/: Missing")
        
        input("\nPress Enter to continue...")
    
    def cleanup_local_data(self):
        """Clean up local data."""
        command = "python data_manager.py cleanup"
        self.run_command(command, "Cleaning up local data")
        input("\nPress Enter to continue...")
    
    def local_project_management_menu(self):
        """Handle local project management."""
        while True:
            self.clear_screen()
            self.show_header()
            safe_print("🗑️ LOCAL PROJECT MANAGEMENT")
            print("=" * 60)
            
            # Show current local projects
            workspace_dir = Path("workspace/customers")
            if workspace_dir.exists():
                project_count = 0
                safe_print("📁 Current local projects:")
                for customer_dir in workspace_dir.iterdir():
                    if customer_dir.is_dir():
                        customer_name = customer_dir.name
                        safe_print(f"\n👤 {customer_name}")
                        for project_dir in customer_dir.iterdir():
                            if project_dir.is_dir():
                                project_count += 1
                                # Try to get project info from summary
                                summary_file = project_dir / "output" / "summary.json"
                                if summary_file.exists():
                                    try:
                                        import json
                                        with open(summary_file, 'r', encoding='utf-8') as f:
                                            summary = json.load(f)
                                        project_name = summary.get('project_name', project_dir.name)
                                        doc_count = summary.get('total_documents', 0)
                                        safe_print(f"  📊 {project_name} ({doc_count} docs)")
                                    except:
                                        safe_print(f"  📁 {project_dir.name}")
                                else:
                                    safe_print(f"  📁 {project_dir.name}")
                
                if project_count == 0:
                    safe_print("📂 No processed projects found")
                else:
                    safe_print(f"\n📈 Total: {project_count} projects")
            else:
                safe_print("📂 No workspace directory found")
            
            print("\nOptions:")
            print("1. 🗑️ Delete specific project")
            print("2. 🧹 Delete all local projects")
            print("3. 📋 Refresh project list")
            print("0. ⬅️ Back to main menu")
            
            choice = input("\nEnter choice: ").strip()
            
            if choice == "0":
                break
            elif choice == "1":
                self.delete_specific_project()
            elif choice == "2":
                self.delete_all_local_projects()
            elif choice == "3":
                continue  # Refresh by redisplaying menu
            else:
                safe_print("❌ Invalid choice")
                input("Press Enter to continue...")
    
    def delete_specific_project(self):
        """Delete a specific local project."""
        safe_print("\n🗑️ Delete Specific Project")
        print("-" * 40)
        
        workspace_dir = Path("workspace/customers")
        if not workspace_dir.exists():
            safe_print("❌ No workspace directory found")
            input("Press Enter to continue...")
            return
        
        # Build list of all projects
        projects = []
        for customer_dir in workspace_dir.iterdir():
            if customer_dir.is_dir():
                customer_name = customer_dir.name
                for project_dir in customer_dir.iterdir():
                    if project_dir.is_dir():
                        # Try to get project info
                        summary_file = project_dir / "output" / "summary.json"
                        if summary_file.exists():
                            try:
                                import json
                                with open(summary_file, 'r', encoding='utf-8') as f:
                                    summary = json.load(f)
                                project_name = summary.get('project_name', project_dir.name)
                                doc_count = summary.get('total_documents', 0)
                                display_name = f"{customer_name} → {project_name} ({doc_count} docs)"
                            except:
                                display_name = f"{customer_name} → {project_dir.name}"
                        else:
                            display_name = f"{customer_name} → {project_dir.name}"
                        
                        projects.append({
                            'path': project_dir,
                            'customer': customer_name,
                            'display': display_name
                        })
        
        if not projects:
            safe_print("❌ No projects found to delete")
            input("Press Enter to continue...")
            return
        
        # Show projects for selection
        safe_print("📋 Select project to delete:")
        for i, project in enumerate(projects, 1):
            print(f"   {i}. {project['display']}")
        
        try:
            choice = input("\nEnter project number (or 0 to cancel): ").strip()
            if choice == "0":
                return
            
            project_idx = int(choice) - 1
            if 0 <= project_idx < len(projects):
                selected_project = projects[project_idx]
                
                # Confirm deletion
                safe_print(f"\n⚠️ Are you sure you want to delete:")
                safe_print(f"   {selected_project['display']}")
                safe_print(f"   Path: {selected_project['path']}")
                
                confirm = input("\nType 'DELETE' to confirm: ").strip()
                if confirm == "DELETE":
                    import shutil
                    try:
                        shutil.rmtree(selected_project['path'])
                        safe_print(f"✅ Successfully deleted project")
                        
                        # Check if customer directory is now empty
                        customer_dir = selected_project['path'].parent
                        if customer_dir.exists() and not any(customer_dir.iterdir()):
                            customer_dir.rmdir()
                            safe_print(f"✅ Removed empty customer directory: {selected_project['customer']}")
                        
                    except Exception as e:
                        safe_print(f"❌ Error deleting project: {e}")
                else:
                    safe_print("❌ Deletion cancelled")
            else:
                safe_print("❌ Invalid project number")
        except ValueError:
            safe_print("❌ Invalid input")
        except Exception as e:
            safe_print(f"❌ Error: {e}")
        
        input("\nPress Enter to continue...")
    
    def delete_all_local_projects(self):
        """Delete all local projects."""
        safe_print("\n🧹 Delete All Local Projects")
        print("-" * 40)
        
        workspace_dir = Path("workspace/customers")
        if not workspace_dir.exists():
            safe_print("❌ No workspace directory found")
            input("Press Enter to continue...")
            return
        
        # Count projects
        project_count = 0
        for customer_dir in workspace_dir.iterdir():
            if customer_dir.is_dir():
                for project_dir in customer_dir.iterdir():
                    if project_dir.is_dir():
                        project_count += 1
        
        if project_count == 0:
            safe_print("❌ No projects found to delete")
            input("Press Enter to continue...")
            return
        
        safe_print(f"⚠️ This will delete ALL {project_count} local projects!")
        safe_print("⚠️ This action cannot be undone!")
        
        confirm1 = input("\nType 'DELETE ALL' to confirm: ").strip()
        if confirm1 == "DELETE ALL":
            confirm2 = input("Are you absolutely sure? Type 'YES' to proceed: ").strip()
            if confirm2 == "YES":
                try:
                    import shutil
                    shutil.rmtree(workspace_dir)
                    safe_print(f"✅ Successfully deleted all {project_count} projects")
                    safe_print("✅ Workspace directory cleaned")
                except Exception as e:
                    safe_print(f"❌ Error deleting projects: {e}")
            else:
                safe_print("❌ Deletion cancelled")
        else:
            safe_print("❌ Deletion cancelled")
        
        input("\nPress Enter to continue...")
    
    def show_main_menu(self):
        """Show the main menu."""
        self.clear_screen()
        self.show_header()
        safe_print("📄 GPU DOCUMENT PROCESSING")
        print("=" * 60)
        
        # Show available CSV files
        csv_files = self.list_csv_files()
        if csv_files:
            safe_print("📁 Available CSV files:")
            for i, file in enumerate(csv_files, 1):
                print(f"   {i}. {file}")
        else:
            safe_print("❌ No CSV files found in input/ directory")
        
        print("\nOptions:")
        print("1. 🚀 Process documents with GPU acceleration")
        print("2. 📋 List processed projects")
        print("3. 🗑️ Manage local projects")
        print("4. 👤 Customer Management") 
        print("5. 🌐 Remote Site Management")
        print("6. 📚 Quick Reference")
        print("0. 🚪 Exit")
        print("=" * 60)
    
    def show_quick_reference(self):
        """Show quick reference."""
        self.clear_screen()
        self.show_header()
        print("📚 QUICK REFERENCE")
        print("=" * 60)
        print("🔄 Simplified Workflow:")
        print("   1. Process documents → Main Menu → Option 1 (GPU Processing)")
        print("   2. Create customer → Customer Management → Create new customer")  
        print("   3. Upload to portal → Customer Management → Upload database")
        print("   4. Push to live site → Remote Management → Push database")
        print("")
        print("🌐 Portal Access:")
        print(f"   Live Site: {self.portal_url}")
        print("   Local: http://127.0.0.1:5000 (when running locally)")
        print("")
        print("📁 Important Directories:")
        print("   input/ - Place CSV files here")
        print("   workspace/ - Processed data and databases")
        print("   templates/ - Web interface templates")
        print("")
        print("🔧 Key Commands (if needed manually):")
        print("   Process: python local_processor_lite.py process input/file.csv")
        print("   Upload: python upload_customer_data.py upload db.db email project")
        print("   Remote: python remote_data_manager.py --url URL --key KEY command")
        
        input("\nPress Enter to continue...")
    
    def run(self):
        """Run the interactive manager."""
        try:
            while True:
                self.show_main_menu()
                choice = input("\nEnter choice: ").strip()
                
                if choice == "0":
                    print("\n👋 Goodbye!")
                    break
                elif choice == "1":
                    self.process_documents(gpu=True)
                elif choice == "2":
                    self.list_projects()
                elif choice == "3":
                    self.local_project_management_menu()
                elif choice == "4":
                    self.customer_management_menu()
                elif choice == "5":
                    self.remote_management_menu()
                elif choice == "6":
                    self.show_quick_reference()
                else:
                    safe_print("❌ Invalid choice")
                    input("Press Enter to continue...")
                    
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
            input("Press Enter to exit...")

if __name__ == "__main__":
    manager = InteractiveManager()
    manager.run()
