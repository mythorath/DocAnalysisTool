#!/usr/bin/env python3
"""
GPU-Enhanced Document Processing Tool
Leverages RTX 3080 Ti for advanced OCR and document extraction.
"""

import os
import sys
import json
import uuid
import sqlite3
from datetime import datetime
from pathlib import Path
import argparse
import logging
import platform
import subprocess
from typing import List, Dict, Optional

# Standard imports
try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    import csv
    HAS_PANDAS = False

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

# GPU-enhanced imports
try:
    import torch
    HAS_TORCH = True
    CUDA_AVAILABLE = torch.cuda.is_available()
    if CUDA_AVAILABLE:
        print(f"🚀 CUDA detected: {torch.cuda.get_device_name(0)}")
except ImportError:
    HAS_TORCH = False
    CUDA_AVAILABLE = False

try:
    import easyocr
    HAS_EASYOCR = True
except ImportError:
    HAS_EASYOCR = False

try:
    from PIL import Image, ImageEnhance, ImageFilter
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

try:
    import pytesseract
    HAS_TESSERACT = True
except ImportError:
    HAS_TESSERACT = False

try:
    import fitz  # PyMuPDF
    HAS_PYMUPDF = True
except ImportError:
    HAS_PYMUPDF = False

try:
    from pdf2image import convert_from_path
    HAS_PDF2IMAGE = True
except ImportError:
    HAS_PDF2IMAGE = False

try:
    from docx import Document
    HAS_DOCX = True
except ImportError:
    HAS_DOCX = False


class GPUEnhancedExtractor:
    """GPU-accelerated document text extraction using RTX 3080 Ti."""
    
    def __init__(self, use_gpu=True, logs_dir="logs"):
        self.logs_dir = Path(logs_dir)
        self.logs_dir.mkdir(exist_ok=True)
        self.use_gpu = use_gpu and CUDA_AVAILABLE
        
        # Setup logging with UTF-8 encoding for Windows compatibility
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.logs_dir / 'gpu_extractor.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Initialize GPU-based OCR
        self.gpu_ocr = None
        self.cpu_ocr_available = HAS_TESSERACT
        
        if self.use_gpu and HAS_EASYOCR:
            try:
                self.logger.info("🚀 Initializing GPU-accelerated OCR (EasyOCR)...")
                self.gpu_ocr = easyocr.Reader(['en'], gpu=True)
                self.logger.info("✅ GPU OCR initialized successfully")
            except Exception as e:
                self.logger.warning(f"⚠️ GPU OCR initialization failed: {e}")
                self.logger.info("💡 Run 'python install_gpu_support.py' if GPU dependencies are missing")
                self.gpu_ocr = None
        
        # Report capabilities
        self.logger.info(f"🔧 GPU Processing: {'✅ Enabled' if self.use_gpu else '❌ Disabled'}")
        self.logger.info(f"🔧 EasyOCR (GPU): {'✅ Available' if self.gpu_ocr else '❌ Not available'}")
        self.logger.info(f"🔧 Tesseract (CPU): {'✅ Available' if self.cpu_ocr_available else '❌ Not available'}")
        self.logger.info(f"🔧 PyMuPDF: {'✅ Available' if HAS_PYMUPDF else '❌ Not available'}")
        self.logger.info(f"🔧 PDF2Image: {'✅ Available' if HAS_PDF2IMAGE else '❌ Not available'}")
    
    def enhance_image_for_ocr(self, image_path):
        """Enhance image quality for better OCR results."""
        if not HAS_PIL:
            return image_path
        
        try:
            # Load and enhance image
            with Image.open(image_path) as img:
                # Convert to RGB if needed
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Enhance contrast and sharpness
                enhancer = ImageEnhance.Contrast(img)
                img = enhancer.enhance(1.5)
                
                enhancer = ImageEnhance.Sharpness(img)
                img = enhancer.enhance(1.2)
                
                # Apply slight blur reduction
                img = img.filter(ImageFilter.UnsharpMask(radius=1, percent=150, threshold=3))
                
                # Save enhanced version
                enhanced_path = image_path.parent / f"enhanced_{image_path.name}"
                img.save(enhanced_path, quality=95)
                return enhanced_path
                
        except Exception as e:
            self.logger.warning(f"Image enhancement failed: {e}")
            return image_path
    
    def extract_with_gpu_ocr(self, image_path):
        """Extract text using GPU-accelerated OCR."""
        if not self.gpu_ocr:
            return None
        
        try:
            # Enhance image first
            enhanced_path = self.enhance_image_for_ocr(image_path)
            
            # Run GPU OCR
            results = self.gpu_ocr.readtext(str(enhanced_path))
            
            # Extract text with confidence scores
            text_blocks = []
            for (bbox, text, confidence) in results:
                if confidence > 0.5:  # Filter low-confidence results
                    text_blocks.append(text.strip())
            
            # Clean up enhanced image
            if enhanced_path != image_path:
                try:
                    enhanced_path.unlink()
                except:
                    pass
            
            return "\n".join(text_blocks)
            
        except Exception as e:
            self.logger.error(f"GPU OCR failed: {e}")
            return None
    
    def extract_with_cpu_ocr(self, image_path):
        """Fallback CPU OCR using Tesseract."""
        if not self.cpu_ocr_available:
            return None
        
        try:
            # Enhance image first
            enhanced_path = self.enhance_image_for_ocr(image_path)
            
            # Configure Tesseract for better accuracy
            custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz!@#$%^&*()_+-=[]{}|;:,.<>?/~` '
            
            text = pytesseract.image_to_string(
                str(enhanced_path), 
                config=custom_config,
                lang='eng'
            )
            
            # Clean up enhanced image
            if enhanced_path != image_path:
                try:
                    enhanced_path.unlink()
                except:
                    pass
            
            return text.strip()
            
        except Exception as e:
            self.logger.error(f"CPU OCR failed: {e}")
            return None
    
    def extract_from_pdf(self, file_path):
        """Enhanced PDF text extraction with GPU-accelerated OCR fallback."""
        text_content = ""
        extraction_method = "unknown"
        
        try:
            # First try direct text extraction
            if HAS_PYMUPDF:
                doc = fitz.open(file_path)
                for page_num in range(len(doc)):
                    page = doc.load_page(page_num)
                    page_text = page.get_text()
                    
                    # If page has substantial text, use it
                    if len(page_text.strip()) > 50:
                        text_content += f"\n--- Page {page_num + 1} ---\n{page_text}\n"
                        extraction_method = "direct"
                    else:
                        # Page might be image-based, try OCR
                        self.logger.info(f"[IMAGE] Page {page_num + 1} appears to be image-based, using OCR...")
                        
                        # Convert page to image
                        pix = page.get_pixmap(matrix=fitz.Matrix(2.0, 2.0))  # Higher resolution
                        img_path = Path(f"temp_page_{page_num}.png")
                        pix.save(str(img_path))
                        
                        # Try GPU OCR first, then CPU OCR
                        ocr_text = None
                        if self.use_gpu:
                            ocr_text = self.extract_with_gpu_ocr(img_path)
                            if ocr_text:
                                extraction_method = "gpu_ocr"
                        
                        if not ocr_text:
                            ocr_text = self.extract_with_cpu_ocr(img_path)
                            if ocr_text:
                                extraction_method = "cpu_ocr"
                        
                        if ocr_text:
                            text_content += f"\n--- Page {page_num + 1} (OCR) ---\n{ocr_text}\n"
                        
                        # Clean up temp image
                        try:
                            img_path.unlink()
                        except:
                            pass
                
                doc.close()
            
            # Fallback: Convert entire PDF to images and OCR
            elif HAS_PDF2IMAGE and (self.gpu_ocr or self.cpu_ocr_available):
                self.logger.info("[PDF] Converting PDF to images for OCR...")
                
                images = convert_from_path(file_path, dpi=300)  # High DPI for better OCR
                
                for i, image in enumerate(images):
                    img_path = Path(f"temp_pdf_page_{i}.png")
                    image.save(img_path)
                    
                    # Try GPU OCR first, then CPU OCR
                    ocr_text = None
                    if self.use_gpu:
                        ocr_text = self.extract_with_gpu_ocr(img_path)
                        if ocr_text:
                            extraction_method = "gpu_ocr"
                    
                    if not ocr_text:
                        ocr_text = self.extract_with_cpu_ocr(img_path)
                        if ocr_text:
                            extraction_method = "cpu_ocr"
                    
                    if ocr_text:
                        text_content += f"\n--- Page {i + 1} (OCR) ---\n{ocr_text}\n"
                    
                    # Clean up temp image
                    try:
                        img_path.unlink()
                    except:
                        pass
        
        except Exception as e:
            self.logger.error(f"PDF extraction failed: {e}")
            return "", "error"
        
        return text_content.strip(), extraction_method
    
    def extract_from_image(self, file_path):
        """Extract text from image files using GPU-accelerated OCR."""
        try:
            # Try GPU OCR first
            if self.use_gpu:
                text = self.extract_with_gpu_ocr(Path(file_path))
                if text:
                    return text, "gpu_ocr"
            
            # Fallback to CPU OCR
            text = self.extract_with_cpu_ocr(Path(file_path))
            if text:
                return text, "cpu_ocr"
            
            return "", "ocr_failed"
            
        except Exception as e:
            self.logger.error(f"Image extraction failed: {e}")
            return "", "error"
    
    def extract_from_docx(self, file_path):
        """Extract text from DOCX files."""
        if not HAS_DOCX:
            return "", "no_docx_support"
        
        try:
            doc = Document(file_path)
            text_content = []
            
            for paragraph in doc.paragraphs:
                text_content.append(paragraph.text)
            
            return "\n".join(text_content), "direct"
            
        except Exception as e:
            self.logger.error(f"DOCX extraction failed: {e}")
            return "", "error"
    
    def extract_from_file(self, file_path):
        """Main extraction method that determines file type and uses appropriate extraction."""
        file_path = Path(file_path)
        file_ext = file_path.suffix.lower()
        
        self.logger.info(f"[EXTRACT] Processing file: {file_path.name}")
        
        if file_ext == '.pdf':
            return self.extract_from_pdf(file_path)
        elif file_ext in ['.png', '.jpg', '.jpeg', '.tiff', '.bmp']:
            return self.extract_from_image(file_path)
        elif file_ext in ['.docx']:
            return self.extract_from_docx(file_path)
        elif file_ext in ['.txt']:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read(), "direct"
            except Exception as e:
                self.logger.error(f"Text file read failed: {e}")
                return "", "error"
        else:
            self.logger.warning(f"Unsupported file type: {file_ext}")
            return "", "unsupported"


def main():
    """Main function to test GPU-enhanced extraction."""
    parser = argparse.ArgumentParser(description="GPU-Enhanced Document Processor")
    parser.add_argument("file_path", help="Path to document to process")
    parser.add_argument("--no-gpu", action="store_true", help="Disable GPU acceleration")
    
    args = parser.parse_args()
    
    # Initialize extractor
    extractor = GPUEnhancedExtractor(use_gpu=not args.no_gpu)
    
    # Extract text
    text, method = extractor.extract_from_file(args.file_path)
    
    print(f"\n📊 Extraction Results:")
    print(f"🔧 Method: {method}")
    print(f"📏 Length: {len(text)} characters")
    print(f"\n📄 Content Preview:")
    print("-" * 50)
    print(text[:500] + "..." if len(text) > 500 else text)


if __name__ == "__main__":
    main()
