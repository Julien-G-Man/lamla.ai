from django.core.management.base import BaseCommand
import smtplib
import ssl

class Command(BaseCommand):
    help = 'Test direct SMTP connectivity to smtp.gmail.com:587 and smtp.gmail.com:465'

    def handle(self, *args, **options):
        self.stdout.write('Testing SMTP connection to smtp.gmail.com:587...')
        try:
            context = ssl.create_default_context()
            with smtplib.SMTP('smtp.gmail.com', 587, timeout=10) as server:
                server.ehlo()
                server.starttls(context=context)
                server.ehlo()
            self.stdout.write(self.style.SUCCESS('✅ Successfully connected to smtp.gmail.com:587 and started TLS.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Failed to connect: {e}'))
        
        self.stdout.write('\nTesting SMTP connection to smtp.gmail.com:465 (SSL)...')
        try:
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=10, context=context) as server:
                server.ehlo()
            self.stdout.write(self.style.SUCCESS('✅ Successfully connected to smtp.gmail.com:465 using SSL.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Failed to connect: {e}')) 