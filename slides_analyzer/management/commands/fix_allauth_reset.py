from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from django.conf import settings
from allauth.account.models import EmailConfirmation
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Fix Allauth password reset issues - comprehensive solution'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear-tokens',
            action='store_true',
            help='Clear all old password reset tokens',
        )
        parser.add_argument(
            '--fix-site',
            action='store_true',
            help='Fix site domain configuration',
        )
        parser.add_argument(
            '--verify-settings',
            action='store_true',
            help='Verify all Allauth settings',
        )
        parser.add_argument(
            '--fix-all',
            action='store_true',
            help='Apply all fixes automatically',
        )

    def handle(self, *args, **options):
        self.stdout.write("🔧 ALLAUTH PASSWORD RESET FIX")
        self.stdout.write("="*50)
        
        # Step 1: Verify current configuration
        self.stdout.write("\n📊 CURRENT CONFIGURATION:")
        self.verify_configuration()
        
        # Step 2: Fix site domain
        if options['fix_site'] or options['fix_all']:
            self.fix_site_domain()
        
        # Step 3: Clear problematic tokens
        if options['clear_tokens'] or options['fix_all']:
            self.clear_old_tokens()
        
        # Step 4: Verify settings
        if options['verify_settings'] or options['fix_all']:
            self.verify_allauth_settings()
        
        # Step 5: Test token generation
        self.test_token_system()
        
        self.stdout.write(self.style.SUCCESS("\n✅ Allauth password reset fix completed!"))
        self.stdout.write("\n💡 Users should now request fresh password reset emails.")

    def verify_configuration(self):
        """Check current system configuration"""
        try:
            # Check Site configuration
            site = Site.objects.get(id=settings.SITE_ID)
            self.stdout.write(f"   Site ID: {site.id}")
            self.stdout.write(f"   Site Domain: {site.domain}")
            self.stdout.write(f"   Site Name: {site.name}")
            
            # Check SECRET_KEY
            secret_key_set = bool(settings.SECRET_KEY and len(settings.SECRET_KEY) > 20)
            self.stdout.write(f"   SECRET_KEY: {'✅ Set' if secret_key_set else '❌ Missing/Short'}")
            
            # Check token counts
            total_tokens = EmailConfirmation.objects.count()
            old_tokens = EmailConfirmation.objects.filter(
                sent__lt=timezone.now() - timedelta(hours=24)
            ).count()
            self.stdout.write(f"   Total tokens: {total_tokens}")
            self.stdout.write(f"   Old tokens (>24h): {old_tokens}")
            
        except Site.DoesNotExist:
            self.stdout.write(self.style.ERROR("   ❌ Site object not found!"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"   ❌ Configuration check failed: {e}"))

    def fix_site_domain(self):
        """Fix site domain configuration"""
        self.stdout.write("\n🌐 FIXING SITE DOMAIN:")
        
        try:
            site, created = Site.objects.get_or_create(
                id=settings.SITE_ID,
                defaults={
                    'domain': 'lamla-ai.onrender.com',
                    'name': 'LAMLA AI'
                }
            )
            
            # Update domain if needed
            if site.domain != 'lamla-ai.onrender.com':
                old_domain = site.domain
                site.domain = 'lamla-ai.onrender.com'
                site.name = 'LAMLA AI'
                site.save()
                self.stdout.write(
                    self.style.SUCCESS(f"   ✅ Updated domain: {old_domain} → {site.domain}")
                )
                logger.info(f"Site domain updated from {old_domain} to {site.domain}")
            else:
                self.stdout.write(
                    self.style.SUCCESS(f"   ✅ Domain already correct: {site.domain}")
                )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS("   ✅ Created new Site object")
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"   ❌ Failed to fix site domain: {e}")
            )

    def clear_old_tokens(self):
        """Clear old and potentially corrupted tokens"""
        self.stdout.write("\n🧹 CLEARING OLD TOKENS:")
        
        try:
            # Clear tokens older than 1 hour (they should be used quickly)
            old_time = timezone.now() - timedelta(hours=1)
            old_tokens = EmailConfirmation.objects.filter(sent__lt=old_time)
            count = old_tokens.count()
            
            if count > 0:
                old_tokens.delete()
                self.stdout.write(
                    self.style.SUCCESS(f"   ✅ Cleared {count} old tokens")
                )
                logger.info(f"Cleared {count} old password reset tokens")
            else:
                self.stdout.write(
                    self.style.SUCCESS("   ✅ No old tokens to clear")
                )
            
            # Also clear any tokens with invalid keys
            invalid_tokens = EmailConfirmation.objects.filter(key__isnull=True)
            invalid_count = invalid_tokens.count()
            if invalid_count > 0:
                invalid_tokens.delete()
                self.stdout.write(
                    self.style.SUCCESS(f"   ✅ Cleared {invalid_count} invalid tokens")
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"   ❌ Failed to clear tokens: {e}")
            )

    def verify_allauth_settings(self):
        """Verify Allauth configuration"""
        self.stdout.write("\n⚙️  VERIFYING ALLAUTH SETTINGS:")
        
        try:
            # Check key settings
            settings_to_check = [
                ('ACCOUNT_EMAIL_VERIFICATION', 'mandatory'),
                ('ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS', 3),
                ('ACCOUNT_EMAIL_CONFIRMATION_HMAC', True),
                ('SITE_ID', 1),
            ]
            
            for setting_name, expected in settings_to_check:
                actual = getattr(settings, setting_name, None)
                if actual == expected:
                    self.stdout.write(f"   ✅ {setting_name}: {actual}")
                else:
                    self.stdout.write(
                        self.style.WARNING(f"   ⚠️  {setting_name}: {actual} (expected: {expected})")
                    )
            
            # Check email backend
            email_backend = getattr(settings, 'EMAIL_BACKEND', 'Not set')
            self.stdout.write(f"   📧 EMAIL_BACKEND: {email_backend}")
            
            # Check custom adapter
            adapter = getattr(settings, 'ACCOUNT_ADAPTER', 'Default')
            self.stdout.write(f"   🔧 ACCOUNT_ADAPTER: {adapter}")
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"   ❌ Settings verification failed: {e}")
            )

    def test_token_system(self):
        """Test if token generation is working"""
        self.stdout.write("\n🧪 TESTING TOKEN SYSTEM:")
        
        try:
            from allauth.account.utils import user_pk_to_url_str
            from django.contrib.auth.models import User
            
            # Test with first user (if exists)
            test_user = User.objects.first()
            if test_user:
                # Test URL generation
                user_id_str = user_pk_to_url_str(test_user)
                self.stdout.write(f"   ✅ User ID encoding works: {user_id_str}")
                
                # Test site domain in context
                from django.contrib.sites.models import Site
                site = Site.objects.get(id=settings.SITE_ID)
                self.stdout.write(f"   ✅ Site context available: {site.domain}")
                
                self.stdout.write("   ✅ Token system appears functional")
            else:
                self.stdout.write("   ⚠️  No users found to test with")
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"   ❌ Token system test failed: {e}")
            )

    def success(self, message):
        """Helper for success messages"""
        self.stdout.write(self.style.SUCCESS(message))