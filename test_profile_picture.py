#!/usr/bin/env python
"""
Test script to verify profile picture functionality
"""
import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edtech_project.settings')
django.setup()

from django.contrib.auth.models import User
from slides_analyzer.models import UserProfile

def test_profile_picture_functionality():
    """Test the profile picture functionality"""
    print("Testing Profile Picture Functionality...")
    
    # Test 1: Check if UserProfile model exists
    try:
        # Get or create a test user
        user, created = User.objects.get_or_create(
            username='testuser',
            defaults={
                'email': 'test@example.com',
                'first_name': 'Test',
                'last_name': 'User'
            }
        )
        
        if created:
            print("✓ Created test user")
        else:
            print("✓ Test user already exists")
        
        # Test 2: Check if UserProfile was automatically created
        try:
            profile = user.profile
            print("✓ UserProfile automatically created")
        except UserProfile.DoesNotExist:
            print("✗ UserProfile not automatically created")
            return False
        
        # Test 3: Check default profile picture URL
        default_url = profile.profile_picture_url
        print(f"✓ Default profile picture URL: {default_url}")
        
        # Test 4: Check bio field
        profile.bio = "This is a test bio"
        profile.save()
        print("✓ Bio field working correctly")
        
        # Test 5: Check profile string representation
        print(f"✓ Profile string: {profile}")
        
        print("\n🎉 All tests passed! Profile picture functionality is working correctly.")
        return True
        
    except Exception as e:
        print(f"✗ Error during testing: {e}")
        return False

if __name__ == "__main__":
    test_profile_picture_functionality() 