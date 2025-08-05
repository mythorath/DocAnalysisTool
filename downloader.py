#!/usr/bin/env python3
"""
downloader.py - Downloads all linked documents from a CSV file

This module reads a CSV file containing document URLs and downloads all
linked files with proper error handling, retries, and progress tracking.
"""

import os
import re
import time
import logging
import argparse
from pathlib import Path
from urllib.parse import urlparse, unquote
from typing import List, Tuple, Optional

import pandas as pd
import requests
from tqdm import tqdm


def setup_logging(log_dir: str = "logs") -> None:
    """Set up logging configuration."""
    os.makedirs(log_dir, exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(f"{log_dir}/downloader.log"),
            logging.StreamHandler()
        ]
    )


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename by removing or replacing invalid characters.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename safe for filesystem
    """
    # Remove or replace invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    filename = re.sub(r'\s+', '_', filename)  # Replace spaces with underscores
    filename = filename.strip('.')  # Remove leading/trailing dots
    
    # Limit length to avoid filesystem issues
    if len(filename) > 200:
        name, ext = os.path.splitext(filename)
        filename = name[:190] + ext
    
    return filename


def extract_filename_from_url(url: str, document_id: str) -> str:
    """
    Extract filename from URL or generate one based on document ID.
    
    Args:
        url: Download URL
        document_id: Document ID from CSV
        
    Returns:
        Sanitized filename
    """
    # Always use document ID as base to ensure uniqueness
    base_name = sanitize_filename(document_id)
    
    # Try to determine file extension from URL
    parsed_url = urlparse(url)
    
    # First try to get extension from URL path
    ext = '.pdf'  # Default extension
    if parsed_url.path:
        path_lower = parsed_url.path.lower()
        if '.docx' in path_lower:
            ext = '.docx'
        elif '.doc' in path_lower:
            ext = '.doc'
        elif '.xlsx' in path_lower:
            ext = '.xlsx'
        elif '.xls' in path_lower:
            ext = '.xls'
        elif '.txt' in path_lower:
            ext = '.txt'
        elif '.pdf' in path_lower:
            ext = '.pdf'
    
    # Add attachment number if multiple files for same document
    attachment_match = re.search(r'attachment_(\d+)', url)
    if attachment_match:
        attachment_num = attachment_match.group(1)
        filename = f"{base_name}_attachment_{attachment_num}{ext}"
    else:
        filename = f"{base_name}{ext}"
    
    return filename


def validate_url(url: str) -> bool:
    """
    Validate if URL is properly formatted.
    
    Args:
        url: URL to validate
        
    Returns:
        True if URL is valid, False otherwise
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def download_file(url: str, filepath: str, max_retries: int = 3, timeout: int = 30) -> bool:
    """
    Download a file from URL with retry logic.
    
    Args:
        url: URL to download from
        filepath: Local filepath to save to
        max_retries: Maximum number of retry attempts
        timeout: Request timeout in seconds
        
    Returns:
        True if download successful, False otherwise
    """
    for attempt in range(max_retries):
        try:
            # Set headers to mimic a real browser
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=timeout, stream=True)
            response.raise_for_status()
            
            # Get file size if available
            file_size = int(response.headers.get('content-length', 0))
            
            # Download with progress bar if file size is known
            with open(filepath, 'wb') as f:
                if file_size > 0:
                    with tqdm(total=file_size, unit='B', unit_scale=True, desc=os.path.basename(filepath)) as pbar:
                        for chunk in response.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                                pbar.update(len(chunk))
                else:
                    # Download without progress bar if file size unknown
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
            
            logging.info(f"Successfully downloaded: {os.path.basename(filepath)}")
            return True
            
        except requests.exceptions.RequestException as e:
            logging.warning(f"Attempt {attempt + 1} failed for {url}: {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
            
        except Exception as e:
            logging.error(f"Unexpected error downloading {url}: {str(e)}")
            break
    
    logging.error(f"Failed to download after {max_retries} attempts: {url}")
    return False


def parse_attachment_urls(attachment_field: str) -> List[str]:
    """
    Parse attachment URLs from CSV field (may contain multiple URLs).
    
    Args:
        attachment_field: Content of attachment field from CSV
        
    Returns:
        List of URLs
    """
    if pd.isna(attachment_field) or not attachment_field.strip():
        return []
    
    # Split by comma for multiple URLs
    urls = [url.strip() for url in attachment_field.split(',')]
    
    # Filter out empty strings and validate URLs
    valid_urls = [url for url in urls if url and validate_url(url)]
    
    return valid_urls


def load_csv_data(csv_path: str) -> pd.DataFrame:
    """
    Load and validate CSV data.
    
    Args:
        csv_path: Path to CSV file
        
    Returns:
        Pandas DataFrame with CSV data
    """
    try:
        df = pd.read_csv(csv_path)
        
        # Validate required columns exist
        required_columns = ['Document ID', 'Attachment Files']
        for col in required_columns:
            if col not in df.columns:
                raise ValueError(f"Required column '{col}' not found in CSV")
        
        logging.info(f"Loaded CSV with {len(df)} rows")
        return df
        
    except Exception as e:
        logging.error(f"Error loading CSV file {csv_path}: {str(e)}")
        raise


def download_documents(csv_path: str, download_dir: str = "downloads", 
                      failed_log: str = "logs/failed_links.txt") -> Tuple[int, int]:
    """
    Main function to download all documents from CSV.
    
    Args:
        csv_path: Path to CSV file
        download_dir: Directory to save downloads
        failed_log: Path to log failed downloads
        
    Returns:
        Tuple of (successful_downloads, failed_downloads)
    """
    # Ensure download directory exists
    os.makedirs(download_dir, exist_ok=True)
    
    # Load CSV data
    df = load_csv_data(csv_path)
    
    # Collect all download tasks
    download_tasks = []
    for _, row in df.iterrows():
        document_id = str(row['Document ID']).strip()
        attachment_urls = parse_attachment_urls(row['Attachment Files'])
        
        for url in attachment_urls:
            filename = extract_filename_from_url(url, document_id)
            filepath = os.path.join(download_dir, filename)
            download_tasks.append((url, filepath, document_id))
    
    logging.info(f"Found {len(download_tasks)} files to download")
    
    # Track results
    successful_downloads = 0
    failed_downloads = 0
    failed_urls = []
    
    # Download all files with progress bar
    with tqdm(total=len(download_tasks), desc="Downloading files") as pbar:
        for url, filepath, document_id in download_tasks:
            # Skip if file already exists
            if os.path.exists(filepath):
                logging.info(f"Skipping existing file: {os.path.basename(filepath)}")
                pbar.update(1)
                continue
            
            # Download file
            if download_file(url, filepath):
                successful_downloads += 1
            else:
                failed_downloads += 1
                failed_urls.append(f"{document_id}: {url}")
            
            pbar.update(1)
    
    # Log failed downloads
    if failed_urls:
        os.makedirs(os.path.dirname(failed_log), exist_ok=True)
        with open(failed_log, 'w', encoding='utf-8') as f:
            f.write("Failed Downloads:\n")
            f.write("=" * 50 + "\n")
            for failed_url in failed_urls:
                f.write(f"{failed_url}\n")
        
        logging.warning(f"Logged {len(failed_urls)} failed downloads to {failed_log}")
    
    # Summary
    logging.info(f"Download complete: {successful_downloads} successful, {failed_downloads} failed")
    
    return successful_downloads, failed_downloads


def main():
    """Main entry point for CLI usage."""
    parser = argparse.ArgumentParser(description="Download documents from CSV file")
    parser.add_argument("csv_path", help="Path to CSV file containing document URLs")
    parser.add_argument("--download-dir", default="downloads", 
                       help="Directory to save downloads (default: downloads)")
    parser.add_argument("--failed-log", default="logs/failed_links.txt",
                       help="Path to log failed downloads (default: logs/failed_links.txt)")
    parser.add_argument("--log-dir", default="logs",
                       help="Directory for log files (default: logs)")
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.log_dir)
    
    try:
        # Validate input file exists
        if not os.path.exists(args.csv_path):
            raise FileNotFoundError(f"CSV file not found: {args.csv_path}")
        
        # Start download process
        logging.info(f"Starting download process from {args.csv_path}")
        successful, failed = download_documents(args.csv_path, args.download_dir, args.failed_log)
        
        print(f"\nDownload Summary:")
        print(f"Successful: {successful}")
        print(f"Failed: {failed}")
        
        if failed > 0:
            print(f"Failed downloads logged to: {args.failed_log}")
            
    except Exception as e:
        logging.error(f"Error in main process: {str(e)}")
        raise


if __name__ == "__main__":
    main()