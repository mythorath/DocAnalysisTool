#!/usr/bin/env python3
"""
OpenAI Document Analyzer
========================

Uses OpenAI's API to extract meaningful titles, summaries, and metadata from documents.
Focuses on accuracy over speed for document processing enhancement.
"""

import os
import json
import time
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import logging

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None
    print("Warning: OpenAI package not installed. Run: pip install openai")

# Windows emoji compatibility
def safe_print(text):
    """Print text with emoji fallbacks for Windows."""
    if os.name == 'nt':  # Windows
        emoji_replacements = {
            '🤖': '[AI]',
            '📄': '[DOC]',
            '✨': '[ENHANCE]',
            '📝': '[TITLE]',
            '📊': '[SUMMARY]',
            '🔍': '[ANALYZE]',
            '💡': '[INSIGHT]',
            '⚡': '[FAST]',
            '🎯': '[TARGET]',
            '✅': '[OK]',
            '❌': '[ERROR]',
            '⚠️': '[WARN]',
        }
        for emoji, replacement in emoji_replacements.items():
            text = text.replace(emoji, replacement)
    print(text)

class OpenAIDocumentAnalyzer:
    """Analyzes documents using OpenAI to extract meaningful titles and metadata."""
    
    def __init__(self, api_key: str = None):
        """Initialize the OpenAI analyzer."""
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.client = None
        self.logger = self._setup_logger()
        
        if not self.api_key:
            safe_print("❌ OpenAI API key not provided. Set OPENAI_API_KEY environment variable.")
            return
            
        if OpenAI is None:
            safe_print("❌ OpenAI package not installed. Run: pip install openai")
            return
            
        try:
            self.client = OpenAI(api_key=self.api_key)
            safe_print("✅ OpenAI client initialized successfully")
        except Exception as e:
            safe_print(f"❌ Failed to initialize OpenAI client: {e}")
            self.client = None
    
    def _setup_logger(self):
        """Set up logging for the analyzer."""
        logger = logging.getLogger('openai_analyzer')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def is_available(self) -> bool:
        """Check if OpenAI analysis is available."""
        return self.client is not None
    
    def extract_document_title(self, content: str, original_filename: str = None) -> str:
        """
        Extract a meaningful title from document content using OpenAI.
        
        Args:
            content: The document text content
            original_filename: Original filename for context
            
        Returns:
            A meaningful document title
        """
        if not self.is_available():
            return self._fallback_title(original_filename)
        
        try:
            # Truncate content if too long (GPT has token limits)
            max_content_length = 3000  # Roughly 750-1000 tokens
            if len(content) > max_content_length:
                content = content[:max_content_length] + "..."
            
            prompt = f"""
Please analyze this document content and extract a clear, descriptive title that accurately represents the main topic or purpose of the document.

Document content:
{content}

Original filename: {original_filename or 'Not provided'}

Instructions:
1. Create a title that clearly describes what this document is about
2. Keep it concise but informative (ideally 5-15 words)
3. Use proper capitalization
4. Focus on the main subject, purpose, or key information
5. If it's a government document, include relevant agency/department info
6. If it's a regulation or policy, include the subject area

Return only the title, nothing else.
"""
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a document analysis expert who creates clear, descriptive titles for documents."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=100,
                temperature=0.3  # Lower temperature for more consistent results
            )
            
            title = response.choices[0].message.content.strip()
            
            # Clean up the title
            title = title.strip('"\'')  # Remove quotes
            if title and len(title) > 5:  # Ensure it's meaningful
                self.logger.info(f"OpenAI extracted title: {title}")
                return title
            else:
                return self._fallback_title(original_filename)
                
        except Exception as e:
            self.logger.error(f"OpenAI title extraction failed: {e}")
            return self._fallback_title(original_filename)
    
    def extract_document_summary(self, content: str, max_length: int = 200) -> str:
        """
        Extract a concise summary from document content using OpenAI.
        
        Args:
            content: The document text content
            max_length: Maximum summary length in characters
            
        Returns:
            A concise document summary
        """
        if not self.is_available():
            return self._fallback_summary(content, max_length)
        
        try:
            # Truncate content if too long
            max_content_length = 4000
            if len(content) > max_content_length:
                content = content[:max_content_length] + "..."
            
            prompt = f"""
Please create a concise summary of this document that captures its main purpose and key information.

Document content:
{content}

Instructions:
1. Summarize the main purpose and key points
2. Keep it under {max_length} characters
3. Focus on what someone searching would want to know
4. Include key topics, subjects, or regulatory areas if applicable
5. Write in clear, professional language

Return only the summary, nothing else.
"""
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a document analysis expert who creates concise, informative summaries."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150,
                temperature=0.3
            )
            
            summary = response.choices[0].message.content.strip()
            
            # Ensure summary isn't too long
            if len(summary) > max_length:
                summary = summary[:max_length-3] + "..."
            
            if summary and len(summary) > 20:  # Ensure it's meaningful
                self.logger.info(f"OpenAI extracted summary: {summary[:50]}...")
                return summary
            else:
                return self._fallback_summary(content, max_length)
                
        except Exception as e:
            self.logger.error(f"OpenAI summary extraction failed: {e}")
            return self._fallback_summary(content, max_length)
    
    def analyze_document_metadata(self, content: str, original_filename: str = None) -> Dict[str, str]:
        """
        Extract comprehensive metadata from document content using OpenAI.
        
        Args:
            content: The document text content
            original_filename: Original filename for context
            
        Returns:
            Dictionary with enhanced metadata
        """
        if not self.is_available():
            return self._fallback_metadata(content, original_filename)
        
        try:
            # Truncate content if too long
            max_content_length = 3500
            if len(content) > max_content_length:
                content = content[:max_content_length] + "..."
            
            prompt = f"""
Please analyze this document and extract key metadata in JSON format.

Document content:
{content}

Original filename: {original_filename or 'Not provided'}

Please return a JSON object with these fields:
- title: A clear, descriptive title
- summary: A concise summary (under 200 chars)
- document_type: Type of document (e.g., "Policy Document", "Regulation", "Report", "Memo", etc.)
- subject_area: Main subject or topic area
- key_topics: List of 3-5 key topics or themes (as array)
- organization: Relevant organization, agency, or department if mentioned
- date_references: Any dates mentioned (as string, or "None" if none)

Return only valid JSON, nothing else.
"""
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a document analysis expert. Always return valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.3
            )
            
            json_response = response.choices[0].message.content.strip()
            
            # Parse the JSON response
            try:
                metadata = json.loads(json_response)
                self.logger.info(f"OpenAI extracted metadata for: {metadata.get('title', 'Unknown')}")
                return metadata
            except json.JSONDecodeError:
                self.logger.error("OpenAI returned invalid JSON")
                return self._fallback_metadata(content, original_filename)
                
        except Exception as e:
            self.logger.error(f"OpenAI metadata extraction failed: {e}")
            return self._fallback_metadata(content, original_filename)
    
    def enhance_document_data(self, content: str, original_data: Dict) -> Dict:
        """
        Enhance existing document data with OpenAI analysis.
        
        Args:
            content: Document text content
            original_data: Original document metadata
            
        Returns:
            Enhanced document metadata
        """
        if not self.is_available():
            return original_data
        
        try:
            safe_print(f"🤖 Analyzing document with OpenAI: {original_data.get('filename', 'Unknown')}")
            
            # Get OpenAI enhancements
            ai_metadata = self.analyze_document_metadata(content, original_data.get('filename'))
            
            # Merge with original data, prioritizing AI results for key fields
            enhanced_data = original_data.copy()
            
            # Update title if AI provides better one
            if ai_metadata.get('title') and len(ai_metadata['title']) > 5:
                enhanced_data['title'] = ai_metadata['title']
                enhanced_data['filename'] = ai_metadata['title']  # Update display name
            
            # Add AI-generated fields
            enhanced_data.update({
                'ai_summary': ai_metadata.get('summary', ''),
                'document_type': ai_metadata.get('document_type', 'Document'),
                'subject_area': ai_metadata.get('subject_area', ''),
                'key_topics': ai_metadata.get('key_topics', []),
                'organization': ai_metadata.get('organization', ''),
                'date_references': ai_metadata.get('date_references', ''),
                'ai_enhanced': True
            })
            
            safe_print(f"✨ Enhanced: {enhanced_data.get('title', 'Unknown')}")
            return enhanced_data
            
        except Exception as e:
            self.logger.error(f"Document enhancement failed: {e}")
            safe_print(f"⚠️ Using original data for: {original_data.get('filename', 'Unknown')}")
            return original_data
    
    def _fallback_title(self, original_filename: str = None) -> str:
        """Generate fallback title when OpenAI is not available."""
        if original_filename:
            # Clean up filename
            title = original_filename.replace('_', ' ').replace('-', ' ')
            title = Path(title).stem  # Remove extension
            title = ' '.join(word.capitalize() for word in title.split())
            return title
        return "Document"
    
    def _fallback_summary(self, content: str, max_length: int = 200) -> str:
        """Generate fallback summary when OpenAI is not available."""
        if not content:
            return "No content available"
        
        # Take first few sentences up to max_length
        sentences = content.replace('\n', ' ').split('. ')
        summary = ""
        for sentence in sentences:
            if len(summary + sentence) < max_length - 10:
                summary += sentence + ". "
            else:
                break
        
        return summary.strip() or content[:max_length-3] + "..."
    
    def _fallback_metadata(self, content: str, original_filename: str = None) -> Dict[str, str]:
        """Generate fallback metadata when OpenAI is not available."""
        return {
            'title': self._fallback_title(original_filename),
            'summary': self._fallback_summary(content),
            'document_type': 'Document',
            'subject_area': 'General',
            'key_topics': [],
            'organization': '',
            'date_references': '',
            'ai_enhanced': False
        }

# Example usage and testing
if __name__ == "__main__":
    # Test the analyzer
    analyzer = OpenAIDocumentAnalyzer()
    
    if analyzer.is_available():
        safe_print("🤖 OpenAI Document Analyzer - Ready for testing")
        
        # Test with sample content
        sample_content = """
        Medicare Advantage Quality Bonus Payment Demonstration
        
        This document outlines the Medicare Advantage Quality Bonus Payment Demonstration program, 
        designed to improve quality of care for Medicare beneficiaries enrolled in Medicare Advantage plans.
        
        The demonstration will test whether quality bonus payments can incentivize plans to improve 
        performance on key quality measures including clinical care, patient safety, and member experience.
        
        Key objectives:
        1. Improve health outcomes for Medicare Advantage enrollees
        2. Enhance coordination of care
        3. Reduce unnecessary hospital readmissions
        4. Improve patient satisfaction scores
        """
        
        title = analyzer.extract_document_title(sample_content, "MA_Quality_Bonus_Demo.pdf")
        safe_print(f"📝 Extracted Title: {title}")
        
        summary = analyzer.extract_document_summary(sample_content)
        safe_print(f"📊 Extracted Summary: {summary}")
        
        metadata = analyzer.analyze_document_metadata(sample_content, "MA_Quality_Bonus_Demo.pdf")
        safe_print(f"🔍 Extracted Metadata: {json.dumps(metadata, indent=2)}")
        
    else:
        safe_print("❌ OpenAI not available - using fallback methods")
