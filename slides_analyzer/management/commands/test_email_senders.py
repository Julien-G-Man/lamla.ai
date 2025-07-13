from django.core.management.base import BaseCommand
from django.conf import settings
from slides_analyzer.email_backend import send_email
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Test email sending functionality'

    def add_arguments(self, parser):
        parser.add_argument(
            '--to',
            type=str,
            default='contact.lamla1@gmail.com',
            help='Email address to send test email to'
        )

    def handle(self, *args, **options):
        test_email = options['to']
        
        self.stdout.write(f"Testing email sending to: {test_email}")
        self.stdout.write(f"Email backend: {getattr(settings, 'EMAIL_BACKEND', 'Not set')}")
        self.stdout.write(f"Default from email: {getattr(settings, 'DEFAULT_FROM_EMAIL', 'Not set')}")
        
        try:
            # Test basic email sending
            result = send_email(
                subject='Test Email from LAMLA AI',
                message='This is a test email to verify email functionality is working.',
                recipient_list=[test_email],
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'contact.lamla1@gmail.com'),
                fail_silently=False
            )
            
            if result:
                self.stdout.write(
                    self.style.SUCCESS('✅ Email sent successfully!')
                )
            else:
                self.stdout.write(
                    self.style.ERROR('❌ Email sending failed (returned False)')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Email sending failed with error: {e}')
            )
            self.stdout.write(f"Error type: {type(e).__name__}")
            
            # Check common email configuration issues
            self.stdout.write("\nChecking email configuration:")
            
            # Check if email credentials are set
            auth_user = getattr(settings, 'AUTH_EMAIL_HOST_USER', None)
            auth_pass = getattr(settings, 'AUTH_EMAIL_HOST_PASSWORD', None)
            welcome_user = getattr(settings, 'WELCOME_EMAIL_HOST_USER', None)
            welcome_pass = getattr(settings, 'WELCOME_EMAIL_HOST_PASSWORD', None)
            
            if auth_user and auth_pass and auth_pass != 'your_contact_app_password_here':
                self.stdout.write("✅ Auth email credentials configured")
            else:
                self.stdout.write("❌ Auth email credentials not properly configured")
                
            if welcome_user and welcome_pass and welcome_pass != 'your_julien_app_password_here':
                self.stdout.write("✅ Welcome email credentials configured")
            else:
                self.stdout.write("❌ Welcome email credentials not properly configured") 