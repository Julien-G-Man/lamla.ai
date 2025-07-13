from django.core.management.base import BaseCommand
from django.conf import settings
import smtplib
import ssl

class Command(BaseCommand):
    help = 'Direct Gmail SMTP test'

    def handle(self, *args, **options):
        self.stdout.write("🔍 Direct Gmail SMTP Test")
        
        username = getattr(settings, 'AUTH_EMAIL_HOST_USER', None)
        password = getattr(settings, 'AUTH_EMAIL_HOST_PASSWORD', None)
        
        self.stdout.write(f"Username: {username}")
        self.stdout.write(f"Password: {'Set' if password else 'NOT SET'}")
        
        if not username or not password:
            self.stdout.write(self.style.ERROR("❌ Credentials not found"))
            return
        
        try:
            # Test 1: Basic connection
            self.stdout.write("\n1. Testing basic SMTP connection...")
            server = smtplib.SMTP('smtp.gmail.com', 587)
            self.stdout.write("✅ Connected to Gmail SMTP")
            
            # Test 2: EHLO
            self.stdout.write("\n2. Testing EHLO...")
            server.ehlo()
            self.stdout.write("✅ EHLO successful")
            
            # Test 3: STARTTLS
            self.stdout.write("\n3. Testing STARTTLS...")
            context = ssl.create_default_context()
            server.starttls(context=context)
            self.stdout.write("✅ STARTTLS successful")
            
            # Test 4: EHLO after STARTTLS
            self.stdout.write("\n4. Testing EHLO after STARTTLS...")
            server.ehlo()
            self.stdout.write("✅ EHLO after STARTTLS successful")
            
            # Test 5: Authentication
            self.stdout.write("\n5. Testing authentication...")
            server.login(username, password)
            self.stdout.write("✅ Authentication successful")
            
            # Test 6: Send test email
            self.stdout.write("\n6. Testing email send...")
            message = f"""From: {username}
To: juliengmanana@gmail.com
Subject: Test Email from LAMLA AI

This is a test email to verify SMTP functionality.
"""
            server.sendmail(username, 'juliengmanana@gmail.com', message)
            self.stdout.write("✅ Email sent successfully!")
            
            server.quit()
            self.stdout.write(self.style.SUCCESS("\n🎉 All tests passed! Email is working."))
            
        except smtplib.SMTPConnectError as e:
            self.stdout.write(self.style.ERROR(f"❌ Connection failed: {e}"))
            self.stdout.write("💡 This usually means Gmail is blocking the connection")
        except smtplib.SMTPAuthenticationError as e:
            self.stdout.write(self.style.ERROR(f"❌ Authentication failed: {e}"))
            self.stdout.write("💡 Check if the app password is correct")
        except smtplib.SMTPException as e:
            self.stdout.write(self.style.ERROR(f"❌ SMTP error: {e}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Unexpected error: {e}"))
            self.stdout.write(f"Error type: {type(e).__name__}")
        finally:
            try:
                server.quit()
            except:
                pass 