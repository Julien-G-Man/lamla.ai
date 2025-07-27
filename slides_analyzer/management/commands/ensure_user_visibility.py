from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from slides_analyzer.models import UserProfile
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Ensure ALL users are visible in admin dashboard and have proper profiles'

    def add_arguments(self, parser):
        parser.add_argument(
            '--fix-deleted',
            action='store_true',
            help='Automatically undelete users marked as deleted',
        )

    def handle(self, *args, **options):
        self.stdout.write("🔍 Ensuring all users are visible in admin dashboard...")
        
        users = User.objects.all()
        total_users = users.count()
        created_profiles = 0
        fixed_deleted = 0
        
        self.stdout.write(f"📊 Processing {total_users} users...")
        
        for user in users:
            # Ensure every user has a profile
            profile, created = UserProfile.objects.get_or_create(
                user=user,
                defaults={'is_deleted': False}
            )
            
            if created:
                created_profiles += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Created profile for user: {user.username}')
                )
                logger.info(f"Created missing profile for user {user.username} (ID: {user.id})")
            
            # Check if user is marked as deleted
            if profile.is_deleted:
                if options['fix_deleted']:
                    profile.is_deleted = False
                    profile.save()
                    fixed_deleted += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'🔓 Restored user: {user.username} (was marked as deleted)')
                    )
                    logger.warning(f"Auto-restored user {user.username} from deleted status")
                else:
                    self.stdout.write(
                        self.style.WARNING(f'⚠️  User {user.username} is marked as deleted (use --fix-deleted to restore)')
                    )
        
        # Summary
        self.stdout.write("\n" + "="*50)
        self.stdout.write(f"📈 SUMMARY:")
        self.stdout.write(f"   Total users processed: {total_users}")
        self.stdout.write(f"   Profiles created: {created_profiles}")
        self.stdout.write(f"   Users restored: {fixed_deleted}")
        
        if created_profiles == 0 and fixed_deleted == 0:
            self.stdout.write(self.style.SUCCESS("✅ All users already have proper profiles and visibility"))
        else:
            self.stdout.write(self.style.SUCCESS("✅ User visibility issues have been fixed"))
        
        # Final verification
        active_users = User.objects.filter(is_active=True).count()
        deleted_profiles = UserProfile.objects.filter(is_deleted=True).count()
        
        self.stdout.write(f"\n📊 CURRENT STATUS:")
        self.stdout.write(f"   Active users: {active_users}")
        self.stdout.write(f"   Users marked as deleted: {deleted_profiles}")
        
        if deleted_profiles > 0:
            self.stdout.write(
                self.style.WARNING(f"⚠️  {deleted_profiles} users are still marked as deleted. Run with --fix-deleted to restore them.")
            )
        
        self.stdout.write(self.style.SUCCESS("\n🎉 User visibility check completed!"))