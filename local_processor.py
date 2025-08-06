#!/usr/bin/env python3
"""
Local Document Processing Tool
For processing customer documents on your local machine before uploading to their online database.
"""

import os
import sys
import json
import uuid
import sqlite3
from datetime import datetime
from pathlib import Path
import argparse
import pandas as pd

# Import our analysis modules
try:
    from downloader import download_documents
    from extractor import extract_document_text, setup_logging  
    from indexer import DocumentSearchIndex
    from grouper import DocumentGrouper
    FULL_MODULES_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Some modules not available: {e}")
    print("🚀 Using lite processor instead...")
    from local_processor_lite import LocalProcessorLite
    FULL_MODULES_AVAILABLE = False

class LocalProcessor:
    """Handles local document processing for customers."""
    
    def __init__(self, workspace_dir="workspace"):
        self.workspace = Path(workspace_dir)
        self.workspace.mkdir(exist_ok=True)
        
        # Setup directories
        self.downloads_dir = self.workspace / "downloads"
        self.text_dir = self.workspace / "text"
        self.output_dir = self.workspace / "output"
        self.logs_dir = self.workspace / "logs"
        
        for directory in [self.downloads_dir, self.text_dir, self.output_dir, self.logs_dir]:
            directory.mkdir(exist_ok=True)
        
        # Setup logging
        setup_logging(str(self.logs_dir))
        
        print(f"📁 Workspace: {self.workspace.absolute()}")
    
    def process_customer_batch(self, csv_file, customer_name, project_name):
        """Process a complete customer batch from CSV to searchable database."""
        
        print(f"\n🔥 Processing batch for {customer_name}")
        print(f"📊 Project: {project_name}")
        print(f"📄 CSV: {csv_file}")
        print("=" * 60)
        
        # Validate CSV
        try:
            df = pd.read_csv(csv_file)
            if 'Document ID' not in df.columns or 'URL' not in df.columns:
                print("❌ CSV must have 'Document ID' and 'URL' columns")
                return None
            
            total_docs = len(df)
            print(f"📈 Found {total_docs} documents to process")
            
        except Exception as e:
            print(f"❌ CSV Error: {e}")
            return None
        
        # Create customer-specific directories
        customer_id = customer_name.lower().replace(" ", "_")
        project_id = f"{customer_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        project_dir = self.workspace / "customers" / customer_id / project_id
        project_downloads = project_dir / "downloads"
        project_text = project_dir / "text"
        project_output = project_dir / "output"
        
        for directory in [project_dir, project_downloads, project_text, project_output]:
            directory.mkdir(parents=True, exist_ok=True)
        
        print(f"📁 Project directory: {project_dir}")
        
        # Step 1: Download documents
        print("\n📥 Step 1: Downloading documents...")
        downloader = DocumentDownloader(
            downloads_dir=str(project_downloads),
            logs_dir=str(self.logs_dir)
        )
        
        download_results = downloader.download_from_csv(csv_file)
        print(f"✅ Downloaded: {download_results['successful']}/{total_docs}")
        
        if download_results['failed'] > 0:
            print(f"⚠️ Failed: {download_results['failed']} documents")
        
        # Step 2: Extract text
        print("\n📝 Step 2: Extracting text...")
        extracted_files = []
        
        for file_path in project_downloads.glob('*'):
            if file_path.is_file() and file_path.suffix.lower() in ['.pdf', '.docx']:
                success, output_path, metadata = extract_document_text(
                    str(file_path), 
                    str(project_text)
                )
                if success:
                    extracted_files.append({
                        'input_file': str(file_path),
                        'output_file': output_path,
                        'metadata': metadata
                    })
        
        print(f"✅ Extracted: {len(extracted_files)} documents")
        
        # Step 3: Build searchable database
        print("\n🔍 Step 3: Building search database...")
        db_path = project_output / f"{project_id}.db"
        indexer = IndexerDB(str(db_path))
        
        # Create metadata map from CSV
        metadata_map = {}
        for _, row in df.iterrows():
            doc_id = str(row.get('Document ID', ''))
            metadata_map[doc_id] = {
                'source_url': row.get('URL', ''),
                'organization': row.get('Organization', ''),
                'category': row.get('Category', ''),
            }
        
        # Index all documents
        indexed_count = 0
        for item in extracted_files:
            if os.path.exists(item['output_file']):
                with open(item['output_file'], 'r', encoding='utf-8') as f:
                    content = f.read()
                
                filename = os.path.basename(item['input_file'])
                doc_id = os.path.splitext(filename)[0]
                doc_metadata = metadata_map.get(doc_id, {})
                
                indexer.add_document(
                    filename=filename,
                    document_id=doc_id,
                    content=content,
                    source_url=doc_metadata.get('source_url', ''),
                    organization=doc_metadata.get('organization', ''),
                    category=doc_metadata.get('category', ''),
                    file_type=item['metadata'].get('file_type', ''),
                    character_count=item['metadata'].get('character_count', 0),
                    extraction_method=item['metadata'].get('extraction_method', '')
                )
                indexed_count += 1
        
        print(f"✅ Indexed: {indexed_count} documents")
        
        # Step 4: Optional clustering
        print("\n🎯 Step 4: Document clustering...")
        try:
            text_files = list(project_text.glob('*.txt'))
            if text_files:
                grouper = Grouper()
                
                documents = []
                filenames = []
                
                for text_file in text_files:
                    try:
                        with open(text_file, 'r', encoding='utf-8') as f:
                            content = f.read().strip()
                            if content:
                                documents.append(content)
                                filenames.append(text_file.stem)
                    except Exception:
                        continue
                
                if documents:
                    clustering_results = grouper.cluster_documents(
                        documents, 
                        filenames,
                        method='tfidf'
                    )
                    
                    # Save clustering results
                    results_path = project_output / 'clustering_results.json'
                    with open(results_path, 'w', encoding='utf-8') as f:
                        json.dump(clustering_results, f, indent=2, ensure_ascii=False)
                    
                    print(f"✅ Clustering completed")
                
        except Exception as e:
            print(f"⚠️ Clustering failed: {e}")
        
        # Step 5: Create summary
        summary = {
            'customer_name': customer_name,
            'project_name': project_name,
            'project_id': project_id,
            'processed_date': datetime.now().isoformat(),
            'total_documents': total_docs,
            'downloaded_documents': download_results['successful'],
            'extracted_documents': len(extracted_files),
            'indexed_documents': indexed_count,
            'database_path': str(db_path),
            'project_directory': str(project_dir)
        }
        
        summary_path = project_output / 'summary.json'
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2)
        
        print("\n" + "=" * 60)
        print(f"🎉 Processing Complete!")
        print(f"📊 Summary: {indexed_count}/{total_docs} documents processed")
        print(f"💾 Database: {db_path}")
        print(f"📋 Summary: {summary_path}")
        print(f"📁 All files: {project_dir}")
        
        return {
            'success': True,
            'database_path': str(db_path),
            'summary': summary,
            'project_directory': str(project_dir)
        }
    
    def list_customer_projects(self):
        """List all processed customer projects."""
        customers_dir = self.workspace / "customers"
        
        if not customers_dir.exists():
            print("📭 No customer projects found")
            return
        
        print("\n📋 Customer Projects:")
        print("=" * 60)
        
        for customer_dir in customers_dir.iterdir():
            if customer_dir.is_dir():
                customer_name = customer_dir.name.replace("_", " ").title()
                print(f"\n👤 {customer_name}")
                
                for project_dir in customer_dir.iterdir():
                    if project_dir.is_dir():
                        summary_file = project_dir / "output" / "summary.json"
                        if summary_file.exists():
                            try:
                                with open(summary_file, 'r') as f:
                                    summary = json.load(f)
                                
                                print(f"  📊 {summary['project_name']}")
                                print(f"      Date: {summary['processed_date'][:10]}")
                                print(f"      Documents: {summary['indexed_documents']}")
                                print(f"      Database: {summary['database_path']}")
                            except:
                                print(f"  📁 {project_dir.name}")
    
    def test_search(self, database_path, query):
        """Test search functionality on a database."""
        if not os.path.exists(database_path):
            print(f"❌ Database not found: {database_path}")
            return
        
        print(f"\n🔍 Testing search: '{query}'")
        print(f"💾 Database: {database_path}")
        
        try:
            indexer = IndexerDB(database_path)
            results = indexer.search_documents(query, limit=5)
            
            if results:
                print(f"\n✅ Found {len(results)} results:")
                for i, result in enumerate(results, 1):
                    print(f"\n{i}. {result.get('filename', 'Unknown')}")
                    if result.get('organization'):
                        print(f"   Organization: {result['organization']}")
                    if result.get('snippet'):
                        print(f"   Snippet: {result['snippet'][:200]}...")
            else:
                print("📭 No results found")
                
        except Exception as e:
            print(f"❌ Search error: {e}")

def main():
    """Main CLI interface."""
    if not FULL_MODULES_AVAILABLE:
        print("🚀 Redirecting to lite processor...")
        print("   (Some advanced modules are not available)")
        
        # Import and run lite processor instead
        from local_processor_lite import main as lite_main
        lite_main()
        return
    
    parser = argparse.ArgumentParser(description="Local Document Processing Tool")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Process command
    process_parser = subparsers.add_parser('process', help='Process customer documents')
    process_parser.add_argument('csv_file', help='CSV file with document URLs')
    process_parser.add_argument('--customer', required=True, help='Customer name')
    process_parser.add_argument('--project', required=True, help='Project name')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List customer projects')
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Test search on database')
    search_parser.add_argument('database', help='Path to database file')
    search_parser.add_argument('query', help='Search query')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    processor = LocalProcessor()
    
    if args.command == 'process':
        result = processor.process_customer_batch(
            args.csv_file, 
            args.customer, 
            args.project
        )
        
        if result and result['success']:
            print(f"\n🚀 Next step: Upload {result['database_path']} to customer's online access")
    
    elif args.command == 'list':
        processor.list_customer_projects()
    
    elif args.command == 'search':
        processor.test_search(args.database, args.query)

if __name__ == "__main__":
    main()

