#!/usr/bin/env python3
"""
OpenAI Setup Script
==================

Sets up OpenAI API key for enhanced document processing.
"""

import os
from pathlib import Path

# Windows emoji compatibility
def safe_print(text):
    """Print text with emoji fallbacks for Windows."""
    if os.name == 'nt':  # Windows
        emoji_replacements = {
            '🤖': '[AI]',
            '🔑': '[KEY]',
            '✅': '[OK]',
            '❌': '[ERROR]',
            '💡': '[TIP]',
            '⚠️': '[WARN]',
        }
        for emoji, replacement in emoji_replacements.items():
            text = text.replace(emoji, replacement)
    print(text)

def setup_openai_key():
    """Set up OpenAI API key."""
    safe_print("🤖 OpenAI API Key Setup")
    safe_print("=" * 30)
    
    # Check if key is already set
    current_key = os.getenv('OPENAI_API_KEY')
    if current_key:
        safe_print(f"✅ OpenAI API key already configured")
        safe_print(f"🔑 Current key: {current_key[:20]}...")
        
        response = input("\nWould you like to update it? (y/N): ").lower()
        if response != 'y':
            return
    
    safe_print("\n💡 You need an OpenAI API key for enhanced document analysis.")
    safe_print("   This enables:")
    safe_print("   • Better document title extraction")
    safe_print("   • Intelligent document summaries")
    safe_print("   • Enhanced metadata analysis")
    safe_print("   • Document type classification")
    
    print("\n🔑 Enter your OpenAI API key:")
    print("   (Get one at: https://platform.openai.com/api-keys)")
    
    # Get API key from user
    api_key = input("OpenAI API Key: ").strip()
    
    if not api_key:
        safe_print("❌ No API key provided - setup cancelled")
        return False
    
    if not api_key.startswith('sk-'):
        safe_print("⚠️ Warning: API key should start with 'sk-'")
        response = input("Continue anyway? (y/N): ").lower()
        if response != 'y':
            return False
    
    # Set environment variable for current session
    os.environ['OPENAI_API_KEY'] = api_key
    safe_print("✅ OpenAI API key set for current session")
    
    # Create/update .env file
    env_file = Path('.env')
    env_content = []
    
    if env_file.exists():
        with open(env_file, 'r') as f:
            env_content = f.readlines()
    
    # Remove existing OPENAI_API_KEY lines
    env_content = [line for line in env_content if not line.startswith('OPENAI_API_KEY=')]
    
    # Add new key
    env_content.append(f'OPENAI_API_KEY={api_key}\n')
    
    # Write back to .env
    with open(env_file, 'w') as f:
        f.writelines(env_content)
    
    safe_print(f"✅ OpenAI API key saved to {env_file}")
    
    # Test the key
    safe_print("\n🧪 Testing API key...")
    try:
        from openai_document_analyzer import OpenAIDocumentAnalyzer
        analyzer = OpenAIDocumentAnalyzer()
        
        if analyzer.is_available():
            safe_print("✅ OpenAI API key is working!")
            safe_print("🤖 Enhanced document analysis is now enabled")
        else:
            safe_print("❌ API key test failed")
            return False
            
    except Exception as e:
        safe_print(f"❌ Error testing API key: {e}")
        return False
    
    safe_print("\n💡 Next steps:")
    safe_print("   • Run document processing to see enhanced results")
    safe_print("   • Document titles will be more descriptive")
    safe_print("   • Better categorization and summaries")
    
    return True

if __name__ == "__main__":
    setup_openai_key()
