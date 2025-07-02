#!/usr/bin/env python3
"""
Environment Setup Script for LAMLA-AI
This script helps you set up your API keys for the LAMLA-AI project.
"""

import os
import sys
from pathlib import Path

def create_env_file():
    """Create a .env file with API key placeholders"""
    
    env_content = """# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# API Keys (Replace with your actual keys)
# Get your keys from:
# - Gemini: https://makersuite.google.com/app/apikey
# - Azure OpenAI: https://portal.azure.com/#view/Microsoft_Azure_ProjectOxford/CognitiveServicesHub/~/OpenAI
# - Hugging Face: https://huggingface.co/settings/tokens

GEMINI_API_KEY=your_gemini_api_key_here
AZURE_OPENAI_API_KEY=your_azure_openai_api_key_here
AZURE_OPENAI_ENDPOINT=your_azure_openai_endpoint_here
HUGGING_FACE_API_TOKEN=your_huggingface_token_here

# Gemini Model (Optional - uses default if not set)
GEMINI_MODEL=models/gemini-1.5-pro-latest
"""
    
    env_path = Path('.env')
    
    if env_path.exists():
        print("⚠️  .env file already exists!")
        response = input("Do you want to overwrite it? (y/N): ")
        if response.lower() != 'y':
            print("Setup cancelled.")
            return False
    
    try:
        with open(env_path, 'w') as f:
            f.write(env_content)
        print("✅ .env file created successfully!")
        print("\n📝 Next steps:")
        print("1. Edit the .env file and add your actual API keys")
        print("2. At least one API key is required for question generation")
        print("3. Run 'python manage.py check_apis' to test your configuration")
        return True
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")
        return False

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = [
        'django',
        'google-generativeai',
        'openai',
        'requests',
        'transformers',
        'torch'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n💡 Install missing packages with:")
        print("   pip install -r requirements.txt")
        return False
    else:
        print("✅ All required packages are installed")
        return True

def main():
    print("🚀 LAMLA-AI Environment Setup")
    print("=" * 40)
    
    # Check dependencies
    print("\n1. Checking dependencies...")
    if not check_dependencies():
        sys.exit(1)
    
    # Create .env file
    print("\n2. Setting up environment variables...")
    if create_env_file():
        print("\n🎉 Setup completed successfully!")
        print("\n📚 For more information, see README.md")
    else:
        print("\n❌ Setup failed!")
        sys.exit(1)

if __name__ == "__main__":
    main() 