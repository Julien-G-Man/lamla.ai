from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from slides_analyzer.models import UserProfile
from django.utils import timezone
from datetime import timedelta

class Command(BaseCommand):
    help = 'Check user registration status and display recent signups'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=7,
            help='Number of days to look back for recent signups (default: 7)',
        )
        parser.add_argument(
            '--show-all',
            action='store_true',
            help='Show all users, not just recent ones',
        )

    def handle(self, *args, **options):
        days = options['days']
        show_all = options['show_all']
        
        # Get user counts
        total_users = User.objects.count()
        total_profiles = UserProfile.objects.count()
        
        self.stdout.write(f"\n📊 USER REGISTRATION STATUS")
        self.stdout.write("=" * 50)
        self.stdout.write(f"Total Users: {total_users}")
        self.stdout.write(f"Total User Profiles: {total_profiles}")
        
        # Check for users without profiles
        users_without_profiles = User.objects.filter(profile__isnull=True).count()
        if users_without_profiles > 0:
            self.stdout.write(
                self.style.WARNING(f"⚠️  Users without profiles: {users_without_profiles}")
            )
        else:
            self.stdout.write(
                self.style.SUCCESS("✅ All users have profiles")
            )
        
        # Show recent signups
        if show_all:
            recent_users = User.objects.all().order_by('-date_joined')
            self.stdout.write(f"\n👥 ALL USERS:")
        else:
            cutoff_date = timezone.now() - timedelta(days=days)
            recent_users = User.objects.filter(date_joined__gte=cutoff_date).order_by('-date_joined')
            self.stdout.write(f"\n🆕 RECENT SIGNUPS (last {days} days):")
        
        self.stdout.write("-" * 50)
        
        if recent_users.exists():
            for user in recent_users:
                profile_status = "✅" if hasattr(user, 'profile') else "❌"
                active_status = "🟢" if user.is_active else "🔴"
                staff_status = "👑" if user.is_staff else "👤"
                
                self.stdout.write(
                    f"{profile_status} {active_status} {staff_status} {user.username} "
                    f"({user.email}) - {user.date_joined.strftime('%Y-%m-%d %H:%M')}"
                )
        else:
            if show_all:
                self.stdout.write("No users found.")
            else:
                self.stdout.write(f"No new signups in the last {days} days.")
        
        # Check admin users
        admin_users = User.objects.filter(is_staff=True).count()
        superusers = User.objects.filter(is_superuser=True).count()
        
        self.stdout.write(f"\n🔐 ADMIN STATUS:")
        self.stdout.write("-" * 50)
        self.stdout.write(f"Staff users: {admin_users}")
        self.stdout.write(f"Superusers: {superusers}")
        
        # Show any orphaned profiles
        orphaned_profiles = UserProfile.objects.filter(user__isnull=True).count()
        if orphaned_profiles > 0:
            self.stdout.write(
                self.style.WARNING(f"⚠️  Orphaned profiles (no user): {orphaned_profiles}")
            )
        
        self.stdout.write(f"\n✨ Check complete!")