from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
from slides_analyzer.email_backend import send_email


class Command(BaseCommand):
    help = 'Test email sender configuration for different types of emails'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            type=str,
            help='Email address to send test emails to',
            required=True
        )

    def handle(self, *args, **options):
        test_email = options['email']
        
        self.stdout.write(
            self.style.SUCCESS(f'Testing email sender configuration for: {test_email}')
        )
        
        # Test 1: Email confirmation (should come from contact.lamla1@gmail.com)
        self.stdout.write('\n1. Testing email confirmation...')
        try:
            send_email(
                subject='Email Confirmation - LAMLA AI',
                message='This is a test email confirmation message.',
                recipient_list=[test_email],
                from_email=None  # Will be determined automatically
            )
            self.stdout.write(
                self.style.SUCCESS('✓ Email confirmation sent successfully')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'✗ Failed to send email confirmation: {e}')
            )
        
        # Test 2: Password reset (should come from contact.lamla1@gmail.com)
        self.stdout.write('\n2. Testing password reset...')
        try:
            send_email(
                subject='LAMLA AI - Password Reset Request',
                message='This is a test password reset message.',
                recipient_list=[test_email],
                from_email=None  # Will be determined automatically
            )
            self.stdout.write(
                self.style.SUCCESS('✓ Password reset email sent successfully')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'✗ Failed to send password reset email: {e}')
            )
        
        # Test 3: Welcome email (should come from juliengmanana@gmail.com)
        self.stdout.write('\n3. Testing welcome email...')
        try:
            send_email(
                subject='Welcome to LAMLA AI! 🎉',
                message='This is a test welcome email message.',
                recipient_list=[test_email],
                from_email=None  # Will be determined automatically
            )
            self.stdout.write(
                self.style.SUCCESS('✓ Welcome email sent successfully')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'✗ Failed to send welcome email: {e}')
            )
        
        # Test 4: General notification (should come from contact.lamla1@gmail.com)
        self.stdout.write('\n4. Testing general notification...')
        try:
            send_email(
                subject='General Notification - LAMLA AI',
                message='This is a test general notification message.',
                recipient_list=[test_email],
                from_email=None  # Will be determined automatically
            )
            self.stdout.write(
                self.style.SUCCESS('✓ General notification sent successfully')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'✗ Failed to send general notification: {e}')
            )
        
        self.stdout.write(
            self.style.SUCCESS('\n🎉 Email sender configuration test completed!')
        )
        self.stdout.write(
            '\nExpected results:'
        )
        self.stdout.write(
            '• Email confirmations and password resets: contact.lamla1@gmail.com'
        )
        self.stdout.write(
            '• Welcome emails: juliengmanana@gmail.com'
        )
        self.stdout.write(
            '• General notifications: contact.lamla1@gmail.com'
        ) 