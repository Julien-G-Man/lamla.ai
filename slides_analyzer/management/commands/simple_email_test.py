from django.core.management.base import BaseCommand
from django.conf import settings
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class Command(BaseCommand):
    help = 'Simple email test to isolate SMTP issues'

    def handle(self, *args, **options):
        self.stdout.write("🧪 Simple Email Test")
        
        # Test with contact.lamla1@gmail.com credentials
        username = getattr(settings, 'AUTH_EMAIL_HOST_USER', None)
        password = getattr(settings, 'AUTH_EMAIL_HOST_PASSWORD', None)
        
        self.stdout.write(f"Username: {username}")
        self.stdout.write(f"Password: {'Set' if password else 'NOT SET'}")
        
        if not username or not password:
            self.stdout.write(self.style.ERROR("❌ Credentials not found"))
            return
        
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = username
            msg['To'] = 'juliengmanana@gmail.com'
            msg['Subject'] = 'Test Email from LAMLA AI'
            
            body = "This is a simple test email to verify SMTP connection."
            msg.attach(MIMEText(body, 'plain'))
            
            # Create SMTP connection
            self.stdout.write("Connecting to Gmail SMTP...")
            context = ssl.create_default_context()
            
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                self.stdout.write("Starting TLS...")
                server.starttls(context=context)
                
                self.stdout.write("Logging in...")
                server.login(username, password)
                
                self.stdout.write("Sending email...")
                text = msg.as_string()
                server.sendmail(username, 'juliengmanana@gmail.com', text)
                
                self.stdout.write(self.style.SUCCESS("✅ Email sent successfully!"))
                
        except smtplib.SMTPAuthenticationError as e:
            self.stdout.write(self.style.ERROR(f"❌ Authentication failed: {e}"))
            self.stdout.write("💡 Check if the app password is correct")
        except smtplib.SMTPConnectError as e:
            self.stdout.write(self.style.ERROR(f"❌ Connection failed: {e}"))
            self.stdout.write("💡 This might be due to Gmail security settings")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Unexpected error: {e}"))
            self.stdout.write(f"Error type: {type(e).__name__}") 