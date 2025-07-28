from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from slides_analyzer.models import UserProfile
from allauth.account.models import EmailAddress
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'BULLETPROOF user visibility system - guarantees ALL users are visible in admin'

    def add_arguments(self, parser):
        parser.add_argument(
            '--fix-all',
            action='store_true',
            help='Fix all user visibility issues automatically',
        )
        parser.add_argument(
            '--restore-deleted',
            action='store_true',
            help='Restore all users marked as deleted',
        )
        parser.add_argument(
            '--verify-emails',
            action='store_true',
            help='Verify all user emails automatically',
        )
        parser.add_argument(
            '--show-details',
            action='store_true',
            help='Show detailed information for each user',
        )

    def handle(self, *args, **options):
        self.stdout.write("🛡️ BULLETPROOF USER VISIBILITY SYSTEM")
        self.stdout.write("="*60)
        
        # Get all users
        users = User.objects.all().order_by('-date_joined')
        total_users = users.count()
        
        # Counters
        missing_profiles = 0
        deleted_users = 0
        unverified_emails = 0
        fixed_profiles = 0
        restored_users = 0
        verified_emails = 0
        
        self.stdout.write(f"📊 Processing {total_users} users...")
        
        for user in users:
            if options['show_details']:
                self.stdout.write(f"\n👤 User: {user.username} (ID: {user.id})")
                self.stdout.write(f"   Email: {user.email}")
                self.stdout.write(f"   Active: {user.is_active}")
                self.stdout.write(f"   Joined: {user.date_joined}")
            
            # STEP 1: Ensure UserProfile exists
            try:
                profile = user.profile
                if options['show_details']:
                    self.stdout.write(f"   Profile: is_deleted = {profile.is_deleted}")
            except UserProfile.DoesNotExist:
                missing_profiles += 1
                if options['fix_all']:
                    profile = UserProfile.objects.create(user=user, is_deleted=False)
                    fixed_profiles += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'✅ Created profile for {user.username}')
                    )
                    logger.info(f"BULLETPROOF: Created missing profile for user {user.username}")
                else:
                    self.stdout.write(
                        self.style.WARNING(f'⚠️  {user.username} missing profile (use --fix-all)')
                    )
                    continue
            
            # STEP 2: Check for deleted users
            if hasattr(user, 'profile') and user.profile.is_deleted:
                deleted_users += 1
                if options['restore_deleted'] or options['fix_all']:
                    user.profile.is_deleted = False
                    user.profile.save()
                    restored_users += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'🔓 Restored {user.username}')
                    )
                    logger.warning(f"BULLETPROOF: Restored user {user.username}")
                else:
                    self.stdout.write(
                        self.style.WARNING(f'⚠️  {user.username} marked as deleted (use --restore-deleted)')
                    )
            
            # STEP 3: Check email verification
            try:
                email_obj = EmailAddress.objects.get(user=user, email=user.email)
                if not email_obj.verified:
                    unverified_emails += 1
                    if options['verify_emails'] or options['fix_all']:
                        email_obj.verified = True
                        email_obj.primary = True
                        email_obj.save()
                        verified_emails += 1
                        if options['show_details']:
                            self.stdout.write(
                                self.style.SUCCESS(f'   ✅ Verified email for {user.username}')
                            )
                    elif options['show_details']:
                        self.stdout.write(
                            self.style.WARNING(f'   ⚠️  Email not verified (use --verify-emails)')
                        )
            except EmailAddress.DoesNotExist:
                if options['verify_emails'] or options['fix_all']:
                    EmailAddress.objects.create(
                        user=user,
                        email=user.email,
                        verified=True,
                        primary=True
                    )
                    verified_emails += 1
                    if options['show_details']:
                        self.stdout.write(
                            self.style.SUCCESS(f'   ✅ Created verified email record for {user.username}')
                        )
        
        # SUMMARY REPORT
        self.stdout.write("\n" + "="*60)
        self.stdout.write("📈 BULLETPROOF SYSTEM REPORT")
        self.stdout.write("="*60)
        self.stdout.write(f"📊 Total users processed: {total_users}")
        self.stdout.write(f"👤 Missing profiles found: {missing_profiles}")
        self.stdout.write(f"🗑️  Users marked as deleted: {deleted_users}")
        self.stdout.write(f"📧 Unverified emails found: {unverified_emails}")
        
        if options['fix_all'] or options['restore_deleted'] or options['verify_emails']:
            self.stdout.write("\n🔧 FIXES APPLIED:")
            self.stdout.write(f"✅ Profiles created: {fixed_profiles}")
            self.stdout.write(f"🔓 Users restored: {restored_users}")
            self.stdout.write(f"📧 Emails verified: {verified_emails}")
        
        # FINAL STATUS
        current_active = User.objects.filter(is_active=True).count()
        current_deleted = UserProfile.objects.filter(is_deleted=True).count()
        
        self.stdout.write(f"\n📊 CURRENT STATUS:")
        self.stdout.write(f"   Active users: {current_active}")
        self.stdout.write(f"   Users marked as deleted: {current_deleted}")
        
        if missing_profiles > 0 or deleted_users > 0 or unverified_emails > 0:
            if not (options['fix_all'] or options['restore_deleted'] or options['verify_emails']):
                self.stdout.write(f"\n💡 RECOMMENDATIONS:")
                if missing_profiles > 0:
                    self.stdout.write(f"   Run with --fix-all to create {missing_profiles} missing profiles")
                if deleted_users > 0:
                    self.stdout.write(f"   Run with --restore-deleted to restore {deleted_users} deleted users")
                if unverified_emails > 0:
                    self.stdout.write(f"   Run with --verify-emails to verify {unverified_emails} emails")
        else:
            self.stdout.write(self.style.SUCCESS("\n🎉 ALL USERS ARE PROPERLY CONFIGURED!"))
        
        self.stdout.write(self.style.SUCCESS("\n🛡️ Bulletproof user visibility check completed!"))
        
        # Log summary
        logger.info(f"BULLETPROOF REPORT: {total_users} users, {fixed_profiles} profiles created, {restored_users} users restored, {verified_emails} emails verified")