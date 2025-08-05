#!/usr/bin/env python3
"""
indexer.py - Create and search a full-text index of extracted documents

This module builds a SQLite FTS5 full-text search index of all extracted text files
and provides comprehensive search functionality with ranked results.
"""

import os
import re
import sqlite3
import logging
import argparse
import json
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Any
from datetime import datetime

import pandas as pd
from tqdm import tqdm


def setup_logging(log_dir: str = "logs") -> None:
    """Set up logging configuration."""
    os.makedirs(log_dir, exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(f"{log_dir}/indexer.log"),
            logging.StreamHandler()
        ]
    )


class DocumentSearchIndex:
    """Full-text search index for document collection."""
    
    def __init__(self, db_path: str = "output/document_index.db"):
        """
        Initialize the search index.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.conn = None
        self._create_database()
    
    def _create_database(self) -> None:
        """Create SQLite database with FTS5 tables."""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row  # Enable column access by name
        
        cursor = self.conn.cursor()
        
        # Create metadata table for document information
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS document_metadata (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT UNIQUE NOT NULL,
                document_id TEXT,
                source_url TEXT,
                organization TEXT,
                category TEXT,
                file_type TEXT,
                character_count INTEGER,
                extraction_method TEXT,
                indexed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create FTS5 virtual table for full-text search
        cursor.execute('''
            CREATE VIRTUAL TABLE IF NOT EXISTS document_fts USING fts5(
                filename,
                document_id,
                content
            )
        ''')
        
        self.conn.commit()
        logging.info(f"Database initialized: {self.db_path}")
    
    def _load_source_metadata(self, csv_path: str = "input/comment_links.csv") -> Dict[str, Dict]:
        """
        Load source metadata from original CSV file.
        
        Args:
            csv_path: Path to original CSV file
            
        Returns:
            Dictionary mapping document IDs to metadata
        """
        metadata = {}
        
        if not os.path.exists(csv_path):
            logging.warning(f"Source CSV not found: {csv_path}")
            return metadata
        
        try:
            df = pd.read_csv(csv_path)
            for _, row in df.iterrows():
                doc_id = str(row['Document ID']).strip()
                metadata[doc_id] = {
                    'organization': str(row.get('Organization Name', '')).strip(),
                    'category': str(row.get('Category', '')).strip(),
                    'source_url': str(row.get('Attachment Files', '')).strip(),
                    'comment': str(row.get('Comment', '')).strip()
                }
            
            logging.info(f"Loaded metadata for {len(metadata)} documents from CSV")
            
        except Exception as e:
            logging.error(f"Error loading source metadata: {str(e)}")
        
        return metadata
    
    def _extract_document_id_from_filename(self, filename: str) -> str:
        """
        Extract document ID from filename.
        
        Args:
            filename: Document filename
            
        Returns:
            Document ID or filename if no ID found
        """
        # Try to extract CMS document ID pattern
        match = re.search(r'(CMS-\d{4}-\d{4}-\d{4})', filename)
        if match:
            return match.group(1)
        
        # Fallback to filename without extension
        return Path(filename).stem
    
    def add_document(self, text_file_path: str, source_metadata: Dict[str, Dict] = None) -> bool:
        """
        Add a document to the search index.
        
        Args:
            text_file_path: Path to extracted text file
            source_metadata: Optional metadata from source CSV
            
        Returns:
            True if document was added successfully
        """
        try:
            filename = os.path.basename(text_file_path)
            document_id = self._extract_document_id_from_filename(filename)
            
            # Read text content
            with open(text_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if not content.strip():
                logging.warning(f"Empty content in {filename}")
                return False
            
            # Get metadata from source CSV if available
            metadata = source_metadata.get(document_id, {}) if source_metadata else {}
            
            # Determine file type and extraction method from content
            file_type = 'pdf'
            extraction_method = 'unknown'
            
            if filename.endswith('.docx'):
                file_type = 'docx'
                extraction_method = 'docx_parser'
            elif 'OCR EXTRACTION FAILED' in content:
                extraction_method = 'ocr_failed'
            elif 'PAGE BREAK' in content:
                extraction_method = 'ocr'
            else:
                extraction_method = 'direct_pdf_text'
            
            # Insert into metadata table
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO document_metadata 
                (filename, document_id, source_url, organization, category, file_type, 
                 character_count, extraction_method)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                filename,
                document_id,
                metadata.get('source_url', ''),
                metadata.get('organization', ''),
                metadata.get('category', ''),
                file_type,
                len(content),
                extraction_method
            ))
            
            # Insert into FTS table with content
            cursor.execute('''
                INSERT INTO document_fts (filename, document_id, content)
                VALUES (?, ?, ?)
            ''', (filename, document_id, content))
            
            self.conn.commit()
            
            logging.debug(f"Indexed document: {filename} ({len(content)} chars)")
            return True
            
        except Exception as e:
            logging.error(f"Error adding document {text_file_path}: {str(e)}")
            return False
    
    def build_index(self, text_dir: str = "text", csv_path: str = "input/comment_links.csv") -> Dict[str, int]:
        """
        Build the complete search index from text files.
        
        Args:
            text_dir: Directory containing extracted text files
            csv_path: Path to original CSV file with metadata
            
        Returns:
            Statistics about indexing process
        """
        # Load source metadata
        source_metadata = self._load_source_metadata(csv_path)
        
        # Find all text files
        text_files = list(Path(text_dir).glob("*.txt"))
        
        if not text_files:
            logging.warning(f"No text files found in {text_dir}")
            return {'total_files': 0, 'indexed': 0, 'failed': 0}
        
        logging.info(f"Building index for {len(text_files)} documents")
        
        # Clear existing index
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM document_fts")
        cursor.execute("DELETE FROM document_metadata")
        self.conn.commit()
        
        # Index all documents
        indexed_count = 0
        failed_count = 0
        
        for text_file in tqdm(text_files, desc="Indexing documents"):
            if self.add_document(str(text_file), source_metadata):
                indexed_count += 1
            else:
                failed_count += 1
        
        # Optimize FTS index
        cursor.execute("INSERT INTO document_fts(document_fts) VALUES('optimize')")
        self.conn.commit()
        
        stats = {
            'total_files': len(text_files),
            'indexed': indexed_count,
            'failed': failed_count,
            'database_path': self.db_path
        }
        
        logging.info(f"Index building complete: {indexed_count} indexed, {failed_count} failed")
        return stats
    
    def search(self, query: str, limit: int = 20, highlight: bool = True) -> List[Dict[str, Any]]:
        """
        Search the document index.
        
        Args:
            query: Search query (supports FTS5 syntax)
            limit: Maximum number of results to return
            highlight: Whether to include highlighted snippets
            
        Returns:
            List of search results with metadata and snippets
        """
        try:
            cursor = self.conn.cursor()
            
            # Prepare the search query - escape special characters for basic searches
            search_query = query.strip()
            
            # For phrase searches, wrap in quotes if not already
            if ' ' in search_query and not (search_query.startswith('"') and search_query.endswith('"')):
                # Check if it looks like a phrase search
                if not any(op in search_query.upper() for op in ['AND', 'OR', 'NOT', '*']):
                    search_query = f'"{search_query}"'
            
            # Execute FTS search with ranking
            sql_query = '''
                SELECT 
                    m.filename,
                    m.document_id,
                    m.source_url,
                    m.organization,
                    m.category,
                    m.file_type,
                    m.character_count,
                    m.extraction_method,
                    rank as rank,
                    snippet(document_fts, 2, '<mark>', '</mark>', '...', 64) as snippet
                FROM document_fts 
                JOIN document_metadata m ON m.filename = document_fts.filename
                WHERE document_fts MATCH ?
                ORDER BY rank
                LIMIT ?
            '''
            
            cursor.execute(sql_query, (search_query, limit))
            results = cursor.fetchall()
            
            # Convert to list of dictionaries
            search_results = []
            for row in results:
                result = dict(row)
                
                # Clean up snippet if highlighting is disabled
                if not highlight:
                    result['snippet'] = re.sub(r'</?mark>', '', result['snippet'])
                
                search_results.append(result)
            
            logging.info(f"Search for '{query}' returned {len(search_results)} results")
            return search_results
            
        except Exception as e:
            logging.error(f"Search error for query '{query}': {str(e)}")
            return []
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get index statistics.
        
        Returns:
            Dictionary with index statistics
        """
        try:
            cursor = self.conn.cursor()
            
            # Get document counts
            cursor.execute("SELECT COUNT(*) FROM document_metadata")
            total_docs = cursor.fetchone()[0]
            
            # Get total character count
            cursor.execute("SELECT SUM(character_count) FROM document_metadata")
            total_chars = cursor.fetchone()[0] or 0
            
            # Get file type distribution
            cursor.execute("""
                SELECT file_type, COUNT(*) as count 
                FROM document_metadata 
                GROUP BY file_type
            """)
            file_types = dict(cursor.fetchall())
            
            # Get extraction method distribution
            cursor.execute("""
                SELECT extraction_method, COUNT(*) as count 
                FROM document_metadata 
                GROUP BY extraction_method
            """)
            extraction_methods = dict(cursor.fetchall())
            
            # Get database file size
            db_size = os.path.getsize(self.db_path) if os.path.exists(self.db_path) else 0
            
            return {
                'total_documents': total_docs,
                'total_characters': total_chars,
                'file_types': file_types,
                'extraction_methods': extraction_methods,
                'database_size_bytes': db_size,
                'database_path': self.db_path
            }
            
        except Exception as e:
            logging.error(f"Error getting statistics: {str(e)}")
            return {}
    
    def close(self) -> None:
        """Close database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None


def build_search_index(text_dir: str = "text", csv_path: str = "input/comment_links.csv",
                      db_path: str = "output/document_index.db") -> Dict[str, int]:
    """
    Build the document search index.
    
    Args:
        text_dir: Directory containing extracted text files
        csv_path: Path to original CSV file with metadata
        db_path: Path to SQLite database file
        
    Returns:
        Statistics about indexing process
    """
    index = DocumentSearchIndex(db_path)
    try:
        stats = index.build_index(text_dir, csv_path)
        return stats
    finally:
        index.close()


def search_documents(query: str, limit: int = 20, highlight: bool = True,
                    db_path: str = "output/document_index.db") -> List[Dict[str, Any]]:
    """
    Search the document index.
    
    Args:
        query: Search query
        limit: Maximum number of results
        highlight: Whether to highlight search terms
        db_path: Path to SQLite database file
        
    Returns:
        List of search results
    """
    index = DocumentSearchIndex(db_path)
    try:
        results = index.search(query, limit, highlight)
        return results
    finally:
        index.close()


def print_search_results(results: List[Dict[str, Any]], query: str) -> None:
    """
    Print search results in a formatted way.
    
    Args:
        results: Search results from search_documents()
        query: Original search query
    """
    if not results:
        print(f"\nNo results found for: '{query}'")
        return
    
    print(f"\nSearch Results for: '{query}'")
    print("=" * 60)
    
    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result['filename']}")
        
        if result['organization']:
            print(f"   Organization: {result['organization']}")
        
        if result['category']:
            print(f"   Category: {result['category']}")
        
        print(f"   Document ID: {result['document_id']}")
        print(f"   File Type: {result['file_type'].upper()}")
        print(f"   Size: {result['character_count']:,} characters")
        
        if result['source_url']:
            print(f"   Source: {result['source_url']}")
        
        # Show snippet
        if result['snippet']:
            print(f"   Snippet: {result['snippet']}")
        
        print(f"   Relevance Score: {result['rank']:.4f}")


def main():
    """Main entry point for CLI usage."""
    parser = argparse.ArgumentParser(description="Document search index management")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Build index command
    build_parser = subparsers.add_parser('build', help='Build search index')
    build_parser.add_argument('--text-dir', default='text',
                             help='Directory containing extracted text files (default: text)')
    build_parser.add_argument('--csv-path', default='input/comment_links.csv',
                             help='Path to original CSV file (default: input/comment_links.csv)')
    build_parser.add_argument('--db-path', default='output/document_index.db',
                             help='Path to database file (default: output/document_index.db)')
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Search documents')
    search_parser.add_argument('query', help='Search query')
    search_parser.add_argument('--limit', type=int, default=20,
                              help='Maximum number of results (default: 20)')
    search_parser.add_argument('--no-highlight', action='store_true',
                              help='Disable search term highlighting')
    search_parser.add_argument('--db-path', default='output/document_index.db',
                              help='Path to database file (default: output/document_index.db)')
    search_parser.add_argument('--json', action='store_true',
                              help='Output results as JSON')
    
    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Show index statistics')
    stats_parser.add_argument('--db-path', default='output/document_index.db',
                             help='Path to database file (default: output/document_index.db)')
    
    args = parser.parse_args()
    
    # Setup logging with default directory
    setup_logging('logs')
    
    try:
        if args.command == 'build':
            logging.info("Building search index...")
            stats = build_search_index(args.text_dir, args.csv_path, args.db_path)
            
            print(f"\nIndex Building Complete:")
            print(f"  Total files: {stats['total_files']}")
            print(f"  Successfully indexed: {stats['indexed']}")
            print(f"  Failed: {stats['failed']}")
            print(f"  Database: {stats['database_path']}")
            
        elif args.command == 'search':
            if not os.path.exists(args.db_path):
                raise FileNotFoundError(f"Index database not found: {args.db_path}")
            
            results = search_documents(
                args.query, 
                args.limit, 
                not args.no_highlight, 
                args.db_path
            )
            
            if args.json:
                print(json.dumps(results, indent=2, default=str))
            else:
                print_search_results(results, args.query)
                
        elif args.command == 'stats':
            if not os.path.exists(args.db_path):
                raise FileNotFoundError(f"Index database not found: {args.db_path}")
            
            index = DocumentSearchIndex(args.db_path)
            try:
                stats = index.get_statistics()
                
                print(f"\nIndex Statistics:")
                print(f"  Database: {stats['database_path']}")
                print(f"  Total documents: {stats['total_documents']:,}")
                print(f"  Total characters: {stats['total_characters']:,}")
                print(f"  Database size: {stats['database_size_bytes']:,} bytes")
                
                print(f"\n  File types:")
                for file_type, count in stats['file_types'].items():
                    print(f"    {file_type}: {count}")
                
                print(f"\n  Extraction methods:")
                for method, count in stats['extraction_methods'].items():
                    print(f"    {method}: {count}")
                    
            finally:
                index.close()
                
        else:
            parser.print_help()
            
    except Exception as e:
        logging.error(f"Error in main process: {str(e)}")
        raise


if __name__ == "__main__":
    main()