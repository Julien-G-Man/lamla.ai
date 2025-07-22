from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from slides_analyzer.models import UserProfile
from django.db import transaction
import uuid

class Command(BaseCommand):
    help = 'Test user creation process to ensure it works properly'

    def add_arguments(self, parser):
        parser.add_argument(
            '--create-test-user',
            action='store_true',
            help='Create a test user to verify the process',
        )
        parser.add_argument(
            '--cleanup',
            action='store_true',
            help='Remove test users created by this command',
        )

    def handle(self, *args, **options):
        if options['cleanup']:
            self.cleanup_test_users()
            return

        if options['create_test_user']:
            self.create_test_user()
            return

        self.stdout.write("Use --create-test-user to create a test user or --cleanup to remove test users")

    def create_test_user(self):
        """Create a test user to verify the signup process"""
        test_username = f"test_user_{uuid.uuid4().hex[:8]}"
        test_email = f"{test_username}@example.com"
        
        try:
            with transaction.atomic():
                # Create user (simulating the signup process)
                user = User.objects.create_user(
                    username=test_username,
                    email=test_email,
                    password='testpassword123',
                    first_name='Test',
                    last_name='User'
                )
                
                self.stdout.write(f"✅ Created test user: {user.username}")
                self.stdout.write(f"   Email: {user.email}")
                self.stdout.write(f"   Date joined: {user.date_joined}")
                
                # Check if profile was created automatically
                try:
                    profile = user.profile
                    self.stdout.write(f"✅ UserProfile created automatically: {profile}")
                except UserProfile.DoesNotExist:
                    self.stdout.write(self.style.WARNING("⚠️  UserProfile was NOT created automatically"))
                    # Create it manually
                    profile = UserProfile.objects.create(user=user)
                    self.stdout.write(f"✅ UserProfile created manually: {profile}")
                
                # Verify the user appears in admin queries
                admin_query_count = User.objects.filter(username=test_username).count()
                self.stdout.write(f"✅ User appears in admin queries: {admin_query_count == 1}")
                
                self.stdout.write(f"\n🎉 Test user creation successful!")
                self.stdout.write(f"You should now be able to see this user in the Django admin under 'Users'")
                self.stdout.write(f"Username: {test_username}")
                self.stdout.write(f"Password: testpassword123")
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Error creating test user: {str(e)}"))

    def cleanup_test_users(self):
        """Remove test users created by this command"""
        test_users = User.objects.filter(username__startswith='test_user_')
        count = test_users.count()
        
        if count > 0:
            test_users.delete()
            self.stdout.write(f"🧹 Removed {count} test users")
        else:
            self.stdout.write("No test users found to cleanup")