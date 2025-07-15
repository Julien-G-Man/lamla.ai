from django.core.mail.backends.smtp import EmailBackend as SMTPEmailBackend
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.conf import settings
import os
import logging
import smtplib
import ssl


class CustomEmailBackend(SMTPEmailBackend):
    """
    Custom email backend that sends different types of emails from different SMTP accounts.
    
    - Email confirmations and password resets: lamlaaiteam@gmail.com SMTP
    - Welcome emails and general notifications: juliengmanana@gmail.com SMTP
    """
    
    def send_messages(self, email_messages):
        """
        Override send_messages to use different SMTP configurations based on email type.
        """
        logger = logging.getLogger(__name__)
        for message in email_messages:
            try:
                # Determine which SMTP to use based on email type
                smtp_config = self._get_smtp_config_for_message(message)
                
                logger.info(f"Using SMTP config for subject '{message.subject}': {smtp_config['username']}")
                
                # Send using direct SMTP connection
                self._send_with_smtp_config(message, smtp_config)
                
                logger.info(f"Email sent successfully via {smtp_config['username']}")
                
            except Exception as e:
                logger.error(f"Failed to send email with subject '{message.subject}': {e}")
                if not getattr(message, 'fail_silently', False):
                    raise
    
    def _send_with_smtp_config(self, message, smtp_config):
        """
        Send email using the specified SMTP configuration.
        """
        logger = logging.getLogger(__name__)
        logger.info(f"Attempting to send email with username: {smtp_config['username']}")
        logger.info(f"Password length: {len(smtp_config['password'])} characters")
        
        # Convert EmailMultiAlternatives to EmailMessage to avoid get_all() compatibility issue
        if hasattr(message, 'alternatives') and message.alternatives:
            # Create a new EmailMessage with the HTML content
            html_content = message.alternatives[0][0]
            email_message = EmailMessage(
                subject=message.subject,
                body=html_content,
                from_email=message.from_email,
                to=message.to,
                headers=message.extra_headers
            )
            email_message.content_subtype = "html"
        else:
            # Use the original message if no alternatives
            email_message = message
        
        if smtp_config.get('use_ssl', False):
            # Use SSL connection
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(smtp_config['host'], smtp_config['port'], context=context) as server:
                server.login(smtp_config['username'], smtp_config['password'])
                server.sendmail(
                    email_message.from_email,
                    email_message.to,
                    email_message.message().as_string()
                )
        else:
            # Use TLS connection
            with smtplib.SMTP(smtp_config['host'], smtp_config['port']) as server:
                server.starttls()
                server.login(smtp_config['username'], smtp_config['password'])
                server.sendmail(
                    email_message.from_email,
                    email_message.to,
                    email_message.message().as_string()
                )
    
    def _get_smtp_config_for_message(self, message):
        """
        Determine the appropriate SMTP configuration based on the message content.
        """
        subject = message.subject.lower() if message.subject else ""
        
        # Add debug logging
        logger = logging.getLogger(__name__)
        logger.info(f"Determining SMTP config for subject: '{subject}'")
        
        # Email confirmations and password resets - use lamlaaiteam@gmail.com SMTP
        if any(keyword in subject for keyword in [
            'confirm', 'verification', 'verify', 'password reset', 
            'password change', 'reset password', 'change password', 'reset request'
        ]):
            config = {
                'host': 'smtp.gmail.com',
                'port': 465,
                'username': getattr(settings, 'AUTH_EMAIL_HOST_USER', 'lamlaaiteam@gmail.com'),
                'password': getattr(settings, 'AUTH_EMAIL_HOST_PASSWORD', ''),
                'use_tls': False,
                'use_ssl': True
            }
            logger.info(f"Using AUTH config: {config['username']}")
            return config
        
        # Welcome emails and general notifications - use juliengmanana@gmail.com SMTP
        elif any(keyword in subject for keyword in [
            'welcome', 'thank you', 'registration', 'signup', 'sign up',
            'account created', 'new account'
        ]) and 'newsletter' not in subject and 'subscription' not in subject:
            return {
                'host': 'smtp.gmail.com',
                'port': 465,
                'username': getattr(settings, 'WELCOME_EMAIL_HOST_USER', 'juliengmanana@gmail.com'),
                'password': getattr(settings, 'WELCOME_EMAIL_HOST_PASSWORD', ''),
                'use_tls': False,
                'use_ssl': True
            }
        
        # Newsletter subscription notifications - use juliengmanana@gmail.com SMTP
        elif any(keyword in subject for keyword in [
            'newsletter', 'subscription', 'subscribed'
        ]) and 'welcome' not in subject:
            return {
                'host': 'smtp.gmail.com',
                'port': 465,
                'username': getattr(settings, 'WELCOME_EMAIL_HOST_USER', 'juliengmanana@gmail.com'),
                'password': getattr(settings, 'WELCOME_EMAIL_HOST_PASSWORD', ''),
                'use_tls': False,
                'use_ssl': True
            }
        
        # Contact form submissions - use lamlaaiteam@gmail.com SMTP
        elif any(keyword in subject for keyword in [
            'contact form', 'lamlaai contact', 'contact submission'
        ]):
            return {
                'host': 'smtp.gmail.com',
                'port': 465,
                'username': getattr(settings, 'AUTH_EMAIL_HOST_USER', 'lamlaaiteam@gmail.com'),
                'password': getattr(settings, 'AUTH_EMAIL_HOST_PASSWORD', ''),
                'use_tls': False,
                'use_ssl': True
            }
        
        # Default to lamlaaiteam@gmail.com SMTP for security-related emails
        else:
            return {
                'host': 'smtp.gmail.com',
                'port': 465,
                'username': getattr(settings, 'AUTH_EMAIL_HOST_USER', 'lamlaaiteam@gmail.com'),
                'password': getattr(settings, 'AUTH_EMAIL_HOST_PASSWORD', ''),
                'use_tls': False,
                'use_ssl': True
            }
    
    def _get_from_email_for_message(self, message):
        """
        Determine the appropriate from_email based on the message content.
        """
        subject = message.subject.lower() if message.subject else ""
        
        # Email confirmations and password resets - MUST come from lamlaaiteam@gmail.com
        if any(keyword in subject for keyword in [
            'confirm', 'verification', 'verify', 'password reset', 
            'password change', 'reset password', 'change password', 'reset request'
        ]):
            return 'lamlaaiteam@gmail.com'
        
        # Welcome emails and general notifications - come from juliengmanana@gmail.com
        elif any(keyword in subject for keyword in [
            'welcome', 'thank you', 'registration', 'signup', 'sign up',
            'account created', 'new account'
        ]) and 'newsletter' not in subject and 'subscription' not in subject:
            return 'juliengmanana@gmail.com'
        
        # Newsletter subscription notifications - come from juliengmanana@gmail.com
        elif any(keyword in subject for keyword in [
            'newsletter', 'subscription', 'subscribed'
        ]) and 'welcome' not in subject:
            return 'juliengmanana@gmail.com'
        
        # Default to lamlaaiteam@gmail.com for security-related emails
        else:
            return 'lamlaaiteam@gmail.com'


def send_email(subject, message, recipient_list, from_email=None, html_message=None, fail_silently=False, **kwargs):
    """
    Reusable utility to send email with plain and HTML content, logging, and fallback.
    """
    logger = logging.getLogger(__name__)
    try:
        if from_email is None:
            from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'lamlaaiteam@gmail.com')
        
        # Create the email message
        if html_message:
            email = EmailMultiAlternatives(
                subject=subject,
                body=message,
                from_email=from_email,
                to=recipient_list,
                **kwargs
            )
            email.attach_alternative(html_message, "text/html")
        else:
            email = EmailMessage(
                subject=subject,
                body=message,
                from_email=from_email,
                to=recipient_list,
                **kwargs
            )
        
        # Use the custom backend explicitly
        from django.core.mail import get_connection
        connection = get_connection(backend='slides_analyzer.email_backend.CustomEmailBackend')
        connection.send_messages([email])
        connection.close()
        
        logger.info(f"Email sent to {recipient_list} (subject: {subject}) from {from_email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email to {recipient_list}: {e}")
        if not fail_silently:
            raise
        return False 