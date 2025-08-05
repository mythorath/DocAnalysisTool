#!/usr/bin/env python3
"""
main.py - Main entry point for the Public Comment Analysis CLI Tool

This tool provides a modular approach to downloading, processing, and analyzing
public comment documents from CSV files containing URLs.
"""

import sys
import argparse
import os
from pathlib import Path
import numpy as np

# Import modules (will be implemented progressively)
try:
    import downloader
except ImportError as e:
    print(f"Error importing downloader module: {e}")
    sys.exit(1)


def setup_directories():
    """Ensure all required directories exist."""
    required_dirs = ['input', 'downloads', 'text', 'logs', 'output']
    for dir_name in required_dirs:
        os.makedirs(dir_name, exist_ok=True)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Public Comment Analysis Tool",
        epilog="Example usage: python main.py download input/comment_links.csv"
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Download command
    download_parser = subparsers.add_parser(
        'download', 
        help='Download documents from CSV file'
    )
    download_parser.add_argument(
        'csv_path', 
        help='Path to CSV file containing document URLs'
    )
    download_parser.add_argument(
        '--download-dir', 
        default='downloads',
        help='Directory to save downloads (default: downloads)'
    )
    
    # Extract command (placeholder for future implementation)
    extract_parser = subparsers.add_parser(
        'extract',
        help='Extract text from downloaded PDFs (OCR if needed)'
    )
    extract_parser.add_argument(
        '--input-dir',
        default='downloads',
        help='Directory containing PDFs to process (default: downloads)'
    )
    extract_parser.add_argument(
        '--output-dir',
        default='text',
        help='Directory to save extracted text (default: text)'
    )
    
    # Index command (placeholder for future implementation)
    index_parser = subparsers.add_parser(
        'index',
        help='Create searchable index of text files'
    )
    index_parser.add_argument(
        '--text-dir',
        default='text',
        help='Directory containing text files to index (default: text)'
    )
    
    # Search command (placeholder for future implementation)
    search_parser = subparsers.add_parser(
        'search',
        help='Search indexed documents'
    )
    search_parser.add_argument(
        'query',
        help='Search query (keyword or phrase)'
    )
    search_parser.add_argument(
        '--limit',
        type=int,
        default=20,
        help='Maximum number of results to return (default: 20)'
    )
    
    # Group command (placeholder for future implementation)
    group_parser = subparsers.add_parser(
        'group',
        help='Group documents by keywords/topics'
    )
    group_parser.add_argument(
        '--method',
        choices=['tfidf_kmeans', 'bertopic', 'lda'],
        default='tfidf_kmeans',
        help='Grouping method (default: tfidf_kmeans)'
    )
    group_parser.add_argument(
        '--clusters',
        type=int,
        help='Number of clusters (auto-detected if not specified)'
    )
    
    args = parser.parse_args()
    
    # Setup directories
    setup_directories()
    
    # Route to appropriate module
    if args.command == 'download':
        try:
            print(f"Starting download from: {args.csv_path}")
            successful, failed = downloader.download_documents(
                args.csv_path, 
                args.download_dir
            )
            print(f"\nDownload completed:")
            print(f"  Successful: {successful}")
            print(f"  Failed: {failed}")
            
        except Exception as e:
            print(f"Error during download: {e}")
            sys.exit(1)
    
    elif args.command == 'extract':
        try:
            import extractor
            print(f"Starting text extraction from: {args.input_dir}")
            stats = extractor.process_documents(
                args.input_dir,
                args.output_dir
            )
            print(f"\nExtraction completed:")
            print(f"  Total files: {stats['total_files']}")
            print(f"  Successful: {stats['successful']}")
            print(f"  Failed: {stats['failed']}")
            print(f"  Total characters: {stats['total_characters']:,}")
            
            if stats['failed'] > 0:
                print(f"  Failed extractions logged to: logs/extraction_failures.txt")
                
        except Exception as e:
            print(f"Error during text extraction: {e}")
            sys.exit(1)
        
    elif args.command == 'index':
        try:
            import indexer
            print(f"Building search index from: {args.text_dir}")
            stats = indexer.build_search_index(
                args.text_dir,
                'input/comment_links.csv',
                'output/document_index.db'
            )
            print(f"\nIndex building completed:")
            print(f"  Total files: {stats['total_files']}")
            print(f"  Successfully indexed: {stats['indexed']}")
            print(f"  Failed: {stats['failed']}")
            print(f"  Database: {stats['database_path']}")
            
        except Exception as e:
            print(f"Error during indexing: {e}")
            sys.exit(1)
        
    elif args.command == 'search':
        try:
            import indexer
            
            # Check if index exists
            db_path = 'output/document_index.db'
            if not os.path.exists(db_path):
                print(f"Search index not found: {db_path}")
                print("Please run 'python main.py index' first to build the search index.")
                sys.exit(1)
            
            print(f"Searching for: '{args.query}'")
            results = indexer.search_documents(args.query, limit=args.limit)
            
            if results:
                indexer.print_search_results(results, args.query)
                print(f"\nFound {len(results)} matching documents.")
            else:
                print(f"No results found for: '{args.query}'")
                
        except Exception as e:
            print(f"Error during search: {e}")
            sys.exit(1)
        
    elif args.command == 'group':
        try:
            import grouper
            
            print(f"Grouping documents using: {args.method}")
            
            # Prepare clustering parameters
            kwargs = {}
            if args.method in ['tfidf_kmeans', 'lda']:
                if args.clusters:
                    kwargs['n_clusters' if args.method == 'tfidf_kmeans' else 'n_topics'] = args.clusters
                else:
                    # Auto-detect optimal number of clusters
                    text_files = list(Path('text').glob("*.txt"))
                    n_docs = len(text_files)
                    optimal_k = max(3, min(8, int(np.sqrt(n_docs / 2))))
                    kwargs['n_clusters' if args.method == 'tfidf_kmeans' else 'n_topics'] = optimal_k
                    print(f"Auto-selected {optimal_k} clusters for {n_docs} documents")
            
            output_file = grouper.group_documents(
                text_dir='text',
                csv_path='input/comment_links.csv',
                method=args.method,
                output_path=f'output/{args.method}_results.csv',
                **kwargs
            )
            
            print(f"\nGrouping completed successfully!")
            print(f"Results saved to: {output_file}")
            print(f"Detailed results: {output_file.replace('.csv', '_detailed.json')}")
            
        except Exception as e:
            print(f"Error during document grouping: {e}")
            sys.exit(1)
        
    else:
        parser.print_help()


if __name__ == "__main__":
    main()