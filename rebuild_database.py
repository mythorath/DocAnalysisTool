#!/usr/bin/env python3
"""Rebuild a database to fix FTS issues."""

import sqlite3
import os
from pathlib import Path

def rebuild_database(old_db_path, new_db_path):
    """Rebuild database with proper FTS structure."""
    
    # Create new database with corrected structure
    new_conn = sqlite3.connect(new_db_path)
    new_conn.row_factory = sqlite3.Row
    
    # Create tables with corrected structure
    new_conn.execute('''
        CREATE TABLE document_metadata (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            document_id TEXT NOT NULL,
            source_url TEXT,
            organization TEXT,
            category TEXT,
            file_type TEXT,
            character_count INTEGER,
            extraction_method TEXT,
            indexed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ai_summary TEXT,
            document_type TEXT,
            subject_area TEXT,
            key_topics TEXT,
            date_references TEXT,
            ai_enhanced BOOLEAN DEFAULT 0
        )
    ''')
    
    new_conn.execute('''
        CREATE VIRTUAL TABLE document_fts USING fts5(
            filename,
            document_id,
            content
        )
    ''')
    
    # Open old database
    old_conn = sqlite3.connect(old_db_path)
    old_conn.row_factory = sqlite3.Row
    
    # Get the original text files to rebuild content
    old_cursor = old_conn.cursor()
    old_cursor.execute('SELECT * FROM document_metadata')
    metadata_rows = old_cursor.fetchall()
    
    print(f"Found {len(metadata_rows)} documents to rebuild")
    
    # Find the text directory (should be in same project folder)
    db_dir = Path(old_db_path).parent.parent
    text_dir = db_dir / "text"
    
    print(f"Looking for text files in: {text_dir}")
    
    if not text_dir.exists():
        print("Text directory not found!")
        return False
    
    # Rebuild database with content
    new_cursor = new_conn.cursor()
    rebuilt_count = 0
    
    for row in metadata_rows:
        doc_id = row['document_id']
        
        # Find corresponding text file
        text_file = text_dir / f"{doc_id}.txt"
        if not text_file.exists():
            # Try alternative filename patterns
            for pattern in [f"{row['filename']}.txt", f"{Path(row['filename']).stem}.txt"]:
                alt_file = text_dir / pattern
                if alt_file.exists():
                    text_file = alt_file
                    break
        
        if text_file.exists():
            # Read content
            with open(text_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Insert metadata
            new_cursor.execute('''
                INSERT INTO document_metadata 
                (filename, document_id, source_url, organization, category, 
                 file_type, character_count, extraction_method, ai_summary, 
                 document_type, subject_area, key_topics, date_references, ai_enhanced)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                row['filename'], row['document_id'], row['source_url'], 
                row['organization'], row['category'], row['file_type'], 
                len(content), row['extraction_method'], row['ai_summary'], 
                row['document_type'], row['subject_area'], row['key_topics'], 
                row['date_references'], row['ai_enhanced']
            ))
            
            # Insert into FTS
            new_cursor.execute('''
                INSERT INTO document_fts (filename, document_id, content)
                VALUES (?, ?, ?)
            ''', (row['filename'], row['document_id'], content))
            
            rebuilt_count += 1
            print(f"Rebuilt: {doc_id} ({len(content)} chars)")
        else:
            print(f"Text file not found for: {doc_id}")
    
    new_conn.commit()
    old_conn.close()
    new_conn.close()
    
    print(f"Rebuilt {rebuilt_count} documents successfully")
    return rebuilt_count > 0

if __name__ == "__main__":
    old_db = "workspace/customers/kathyb@upwork.com/kathyb@upwork.com_20250806_160005/output/kathyb@upwork.com_20250806_160005.db"
    new_db = "workspace/customers/kathyb@upwork.com/kathyb@upwork.com_20250806_160005/output/kathyb@upwork.com_20250806_160005_fixed.db"
    
    if rebuild_database(old_db, new_db):
        print(f"Database rebuilt successfully: {new_db}")
        # Replace old database
        os.replace(new_db, old_db)
        print("Database replaced")
    else:
        print("Failed to rebuild database")
