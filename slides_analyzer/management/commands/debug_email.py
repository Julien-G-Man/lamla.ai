from django.core.management.base import BaseCommand
from django.conf import settings
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Debug email SMTP connection issues'

    def handle(self, *args, **options):
        self.stdout.write("🔍 Debugging Email SMTP Connection...")
        
        # Test 1: Auth email credentials
        self.stdout.write("\n1. Testing AUTH email credentials (contact.lamla1@gmail.com):")
        auth_user = getattr(settings, 'AUTH_EMAIL_HOST_USER', None)
        auth_pass = getattr(settings, 'AUTH_EMAIL_HOST_PASSWORD', None)
        
        if auth_user and auth_pass:
            self.stdout.write(f"   Username: {auth_user}")
            self.stdout.write(f"   Password: {'Set' if auth_pass else 'NOT SET'}")
            
            # Test SMTP connection
            try:
                context = ssl.create_default_context()
                with smtplib.SMTP('smtp.gmail.com', 587) as server:
                    server.starttls(context=context)
                    server.login(auth_user, auth_pass)
                    self.stdout.write(self.style.SUCCESS("   ✅ SMTP connection successful!"))
            except smtplib.SMTPAuthenticationError as e:
                self.stdout.write(self.style.ERROR(f"   ❌ Authentication failed: {e}"))
                self.stdout.write("   💡 This usually means the app password is incorrect or expired")
            except smtplib.SMTPConnectError as e:
                self.stdout.write(self.style.ERROR(f"   ❌ Connection failed: {e}"))
                self.stdout.write("   💡 This might be due to Gmail security settings")
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"   ❌ Unexpected error: {e}"))
        else:
            self.stdout.write(self.style.ERROR("   ❌ Auth credentials not configured"))
        
        # Test 2: Welcome email credentials
        self.stdout.write("\n2. Testing WELCOME email credentials (juliengmanana@gmail.com):")
        welcome_user = getattr(settings, 'WELCOME_EMAIL_HOST_USER', None)
        welcome_pass = getattr(settings, 'WELCOME_EMAIL_HOST_PASSWORD', None)
        
        if welcome_user and welcome_pass:
            self.stdout.write(f"   Username: {welcome_user}")
            self.stdout.write(f"   Password: {'Set' if welcome_pass else 'NOT SET'}")
            
            # Test SMTP connection
            try:
                context = ssl.create_default_context()
                with smtplib.SMTP('smtp.gmail.com', 587) as server:
                    server.starttls(context=context)
                    server.login(welcome_user, welcome_pass)
                    self.stdout.write(self.style.SUCCESS("   ✅ SMTP connection successful!"))
            except smtplib.SMTPAuthenticationError as e:
                self.stdout.write(self.style.ERROR(f"   ❌ Authentication failed: {e}"))
                self.stdout.write("   💡 This usually means the app password is incorrect or expired")
            except smtplib.SMTPConnectError as e:
                self.stdout.write(self.style.ERROR(f"   ❌ Connection failed: {e}"))
                self.stdout.write("   💡 This might be due to Gmail security settings")
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"   ❌ Unexpected error: {e}"))
        else:
            self.stdout.write(self.style.ERROR("   ❌ Welcome credentials not configured"))
        
        # Test 3: Default email credentials
        self.stdout.write("\n3. Testing DEFAULT email credentials:")
        default_user = getattr(settings, 'EMAIL_HOST_USER', None)
        default_pass = getattr(settings, 'EMAIL_HOST_PASSWORD', None)
        
        if default_user and default_pass:
            self.stdout.write(f"   Username: {default_user}")
            self.stdout.write(f"   Password: {'Set' if default_pass else 'NOT SET'}")
            
            # Test SMTP connection
            try:
                context = ssl.create_default_context()
                with smtplib.SMTP('smtp.gmail.com', 587) as server:
                    server.starttls(context=context)
                    server.login(default_user, default_pass)
                    self.stdout.write(self.style.SUCCESS("   ✅ SMTP connection successful!"))
            except smtplib.SMTPAuthenticationError as e:
                self.stdout.write(self.style.ERROR(f"   ❌ Authentication failed: {e}"))
                self.stdout.write("   💡 This usually means the app password is incorrect or expired")
            except smtplib.SMTPConnectError as e:
                self.stdout.write(self.style.ERROR(f"   ❌ Connection failed: {e}"))
                self.stdout.write("   💡 This might be due to Gmail security settings")
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"   ❌ Unexpected error: {e}"))
        else:
            self.stdout.write(self.style.ERROR("   ❌ Default credentials not configured"))
        
        self.stdout.write("\n📋 Troubleshooting Tips:")
        self.stdout.write("1. Make sure 2-Step Verification is enabled on both Gmail accounts")
        self.stdout.write("2. Generate new app passwords for 'Mail' in Google Account settings")
        self.stdout.write("3. Make sure the app passwords are 16 characters long")
        self.stdout.write("4. Check if Gmail is blocking less secure apps (should be disabled)")
        self.stdout.write("5. Try generating app passwords for 'Other' instead of 'Mail'") 