#!/usr/bin/env python3
"""
Deployment Issue Fixer Script
This script helps identify and fix common deployment issues that cause
UI differences between local and production environments.
"""

import os
import sys
import hashlib
from pathlib import Path

def check_static_files():
    """Check static files and their hashes for version tracking"""
    print("🔍 Checking static files...")
    
    # Check main CSS file
    css_path = Path("static/slide_analyzer/css/main.css")
    if css_path.exists():
        file_size = css_path.stat().st_size
        print(f"   Main CSS: {file_size} bytes")
        
        # Calculate file hash
        with open(css_path, 'rb') as f:
            file_hash = hashlib.md5(f.read()).hexdigest()[:8]
        print(f"   CSS Hash: {file_hash}")
        
        # Check for version comments
        with open(css_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if '/* Version:' in content:
                print("   Version comment found in CSS")
            else:
                print("   No version comment in CSS")
    else:
        print("   Main CSS: Not found")

def check_templates():
    """Check template files for deployment-specific differences"""
    print("\n📄 Checking templates...")
    
    # Check base template
    base_template = Path("templates/base.html")
    if base_template.exists():
        with open(base_template, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Check for specific UI elements
        if 'Ask AI Assistant' in content:
            print("   Found: 'Ask AI Assistant' in base template")
        elif 'Ask AI' in content:
            print("   Found: 'Ask AI' in base template")
        else:
            print("   Warning: No chatbot toggle text found")
            
        # Check for CSS classes
        if 'chatbot-container' in content:
            print("   Found: chatbot-container class")
        if 'navbar' in content:
            print("   Found: navbar class")
        if 'sidebar' in content:
            print("   Found: sidebar class")
    else:
        print("   Base template: Not found")

def check_settings():
    """Check Django settings for deployment-specific configurations"""
    print("\n⚙️ Checking settings...")
    
    settings_file = Path("edtech_project/settings.py")
    if settings_file.exists():
        with open(settings_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Check DEBUG setting
        if 'DEBUG = True' in content:
            print("   DEBUG: Set to True (development)")
        elif 'DEBUG = False' in content:
            print("   DEBUG: Set to False (production)")
        elif 'DEBUG = os.getenv' in content:
            print("   DEBUG: Environment variable controlled")
        else:
            print("   DEBUG: Unknown setting")
            
        # Check static files configuration
        if 'STATIC_URL' in content:
            print("   STATIC_URL: Configured")
        if 'STATIC_ROOT' in content:
            print("   STATIC_ROOT: Configured")
        if 'STATICFILES_DIRS' in content:
            print("   STATICFILES_DIRS: Configured")
            
        # Check logging configuration
        if 'LOGGING' in content:
            print("   LOGGING: Configured")
        else:
            print("   LOGGING: Not configured")
    else:
        print("   Settings file: Not found")

def generate_version_file():
    """Generate a version file to track deployment changes"""
    print("\n📝 Generating version tracking...")
    
    version_info = {
        'timestamp': str(Path().cwd()),
        'static_files': {},
        'templates': {},
        'settings': {}
    }
    
    # Check static files
    static_dir = Path("static")
    if static_dir.exists():
        for file_path in static_dir.rglob("*"):
            if file_path.is_file():
                try:
                    file_hash = hashlib.md5(file_path.read_bytes()).hexdigest()[:8]
                    version_info['static_files'][str(file_path)] = {
                        'size': file_path.stat().st_size,
                        'hash': file_hash
                    }
                except Exception as e:
                    print(f"   Error reading {file_path}: {e}")
    
    # Check templates
    templates_dir = Path("templates")
    if templates_dir.exists():
        for file_path in templates_dir.rglob("*.html"):
            try:
                file_hash = hashlib.md5(file_path.read_bytes()).hexdigest()[:8]
                version_info['templates'][str(file_path)] = {
                    'size': file_path.stat().st_size,
                    'hash': file_hash
                }
            except Exception as e:
                print(f"   Error reading {file_path}: {e}")
    
    # Write version file
    version_file = Path("deployment_version.json")
    import json
    with open(version_file, 'w') as f:
        json.dump(version_info, f, indent=2)
    
    print(f"   Version file created: {version_file}")
    return version_file

def suggest_fixes():
    """Suggest fixes for common deployment issues"""
    print("\n🔧 Suggested fixes for deployment issues:")
    
    print("\n1. Static File Caching Issues:")
    print("   - Add version parameters to static URLs")
    print("   - Use django.contrib.staticfiles.storage.ManifestStaticFilesStorage")
    print("   - Clear browser cache and CDN cache")
    
    print("\n2. Template Differences:")
    print("   - Ensure all template changes are committed and deployed")
    print("   - Check for environment-specific template logic")
    print("   - Verify template inheritance is working correctly")
    
    print("\n3. Environment Variables:")
    print("   - Set DEBUG=False in production")
    print("   - Configure proper DATABASE_URL")
    print("   - Set STATIC_ROOT for production")
    
    print("\n4. Database Differences:")
    print("   - Ensure database migrations are applied")
    print("   - Check for different data between environments")
    print("   - Verify user sessions and profiles")

def main():
    """Main function to run all checks"""
    print("🚀 DEPLOYMENT ISSUE DIAGNOSTIC TOOL")
    print("=" * 50)
    
    check_static_files()
    check_templates()
    check_settings()
    
    version_file = generate_version_file()
    
    suggest_fixes()
    
    print(f"\n✅ Diagnostic complete. Version file saved to: {version_file}")
    print("\nNext steps:")
    print("1. Compare this version file with your deployment")
    print("2. Apply the suggested fixes")
    print("3. Clear caches and restart the deployment")

if __name__ == "__main__":
    main() 