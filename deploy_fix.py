#!/usr/bin/env python3
"""
Deployment Fix Script
This script helps fix common deployment issues that cause UI differences
between local and production environments.
"""

import os
import sys
import shutil
from pathlib import Path
import subprocess

def add_version_to_static_files():
    """Add version parameters to static file URLs to prevent caching issues"""
    print("🔧 Adding version parameters to static files...")
    
    # Update base template to include version parameters
    base_template = Path("templates/base.html")
    if base_template.exists():
        with open(base_template, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Add version parameter to CSS link
        if 'main.css' in content and '?v=' not in content:
            content = content.replace(
                'href="{% static \'slide_analyzer/css/main.css\' %}"',
                'href="{% static \'slide_analyzer/css/main.css\' %}?v=1.0.1"'
            )
            print("   Added version parameter to main.css")
        
        # Add version parameter to any other static files
        if 'font-awesome' in content and '?v=' not in content:
            content = content.replace(
                'href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css"',
                'href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css?v=1.0.1"'
            )
            print("   Added version parameter to Font Awesome")
        
        with open(base_template, 'w', encoding='utf-8') as f:
            f.write(content)
        print("   Updated base template with version parameters")

def update_settings_for_production():
    """Update Django settings for better production deployment"""
    print("\n⚙️ Updating settings for production...")
    
    settings_file = Path("edtech_project/settings.py")
    if settings_file.exists():
        with open(settings_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Add static files storage configuration
        if 'STATICFILES_STORAGE' not in content:
            static_storage_config = '''
# Static files storage for production
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'
'''
            # Find the static files section and add the storage config
            if 'STATIC_ROOT' in content:
                content = content.replace(
                    'STATIC_ROOT = BASE_DIR / "staticfiles"',
                    'STATIC_ROOT = BASE_DIR / "staticfiles"\n\n# Static files storage for production\nSTATICFILES_STORAGE = \'django.contrib.staticfiles.storage.ManifestStaticFilesStorage\''
                )
                print("   Added ManifestStaticFilesStorage configuration")
        
        # Add cache busting middleware
        if 'CacheBustingMiddleware' not in content:
            middleware_config = '''
# Cache busting middleware
class CacheBustingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if response.get('Content-Type', '').startswith('text/html'):
            # Add cache-busting headers for HTML
            response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'
        return response
'''
            # Add middleware class before MIDDLEWARE
            if 'MIDDLEWARE = [' in content:
                content = content.replace(
                    'MIDDLEWARE = [',
                    middleware_config + '\nMIDDLEWARE = ['
                )
                print("   Added cache busting middleware class")
        
        with open(settings_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print("   Updated settings for production")

def create_static_files_manifest():
    """Create a manifest file for static files to track versions"""
    print("\n📝 Creating static files manifest...")
    
    manifest = {
        'version': '1.0.1',
        'timestamp': str(Path().cwd()),
        'files': {}
    }
    
    # Scan static files
    static_dir = Path("static")
    if static_dir.exists():
        for file_path in static_dir.rglob("*"):
            if file_path.is_file():
                try:
                    import hashlib
                    file_hash = hashlib.md5(file_path.read_bytes()).hexdigest()[:8]
                    manifest['files'][str(file_path)] = {
                        'size': file_path.stat().st_size,
                        'hash': file_hash,
                        'version': '1.0.1'
                    }
                except Exception as e:
                    print(f"   Error processing {file_path}: {e}")
    
    # Write manifest
    manifest_file = Path("static_manifest.json")
    import json
    with open(manifest_file, 'w') as f:
        json.dump(manifest, f, indent=2)
    
    print(f"   Created static manifest: {manifest_file}")

def collect_static_files():
    """Collect static files for production"""
    print("\n📦 Collecting static files...")
    
    try:
        result = subprocess.run([
            'python', 'manage.py', 'collectstatic', '--noinput', '--clear'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("   Static files collected successfully")
            print(result.stdout)
        else:
            print("   Error collecting static files:")
            print(result.stderr)
    except Exception as e:
        print(f"   Error running collectstatic: {e}")

def create_deployment_checklist():
    """Create a deployment checklist"""
    print("\n📋 Creating deployment checklist...")
    
    checklist = """
# DEPLOYMENT CHECKLIST

## Before Deployment:
1. [x] Run: python manage.py collectstatic --noinput --clear
2. [x] Run: python manage.py migrate
3. [x] Set environment variables:
   - DEBUG=False
   - DATABASE_URL (if using external database)
   - All API keys (Azure OpenAI, Gemini, Hugging Face)

## After Deployment:
1. [x] Clear browser cache
2. [x] Clear CDN cache (if using CDN)
3. [x] Restart the application server
4. [x] Test the quiz functionality
5. [x] Check UI elements match local environment

## Common Issues to Check:
1. Static file caching - Clear browser cache
2. Template differences - Ensure all changes are deployed
3. Database migrations - Run migrations on production
4. Environment variables - Verify all are set correctly

## Files to Monitor:
- templates/base.html (for UI text changes)
- static/slide_analyzer/css/main.css (for styling changes)
- edtech_project/settings.py (for configuration changes)
"""
    
    with open("DEPLOYMENT_CHECKLIST.md", 'w', encoding='utf-8') as f:
        f.write(checklist)
    
    print("   Created DEPLOYMENT_CHECKLIST.md")

def main():
    """Main function to run all fixes"""
    print("🚀 DEPLOYMENT FIX SCRIPT")
    print("=" * 50)
    
    add_version_to_static_files()
    update_settings_for_production()
    create_static_files_manifest()
    collect_static_files()
    create_deployment_checklist()
    
    print("\n✅ Deployment fixes applied!")
    print("\nNext steps:")
    print("1. Commit these changes: git add . && git commit -m 'Fix deployment issues'")
    print("2. Push to deployment: git push origin main")
    print("3. Follow the DEPLOYMENT_CHECKLIST.md")
    print("4. Clear caches and restart the deployment")

if __name__ == "__main__":
    main() 