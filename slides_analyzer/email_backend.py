from django.core.mail.backends.smtp import EmailBackend as SMTPEmailBackend
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.conf import settings
import os
import logging


class CustomEmailBackend(SMTPEmailBackend):
    """
    Custom email backend that sends different types of emails from different SMTP accounts.
    
    - Email confirmations and password resets: contact.lamla1@gmail.com SMTP
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
                
                # Create a new backend with the appropriate SMTP settings
                backend = SMTPEmailBackend(
                    host=smtp_config['host'],
                    port=smtp_config['port'],
                    username=smtp_config['username'],
                    password=smtp_config['password'],
                    use_tls=smtp_config['use_tls'],
                    fail_silently=getattr(message, 'fail_silently', False)
                )
                
                # Send the message using the appropriate backend
                backend.send_messages([message])
                backend.close()
                
                logger.info(f"Email sent successfully via {smtp_config['username']}")
                
            except Exception as e:
                logger.error(f"Failed to send email with subject '{message.subject}': {e}")
                if not getattr(message, 'fail_silently', False):
                    raise
    
    def _get_smtp_config_for_message(self, message):
        """
        Determine the appropriate SMTP configuration based on the message content.
        """
        subject = message.subject.lower() if message.subject else ""
        
        # Email confirmations and password resets - use contact.lamla1@gmail.com SMTP
        if any(keyword in subject for keyword in [
            'confirm', 'verification', 'verify', 'password reset', 
            'password change', 'reset password', 'change password', 'reset request'
        ]):
            return {
                'host': 'smtp.gmail.com',
                'port': 587,
                'username': getattr(settings, 'AUTH_EMAIL_HOST_USER', 'contact.lamla1@gmail.com'),
                'password': getattr(settings, 'AUTH_EMAIL_HOST_PASSWORD', ''),
                'use_tls': True
            }
        
        # Welcome emails and general notifications - use juliengmanana@gmail.com SMTP
        elif any(keyword in subject for keyword in [
            'welcome', 'thank you', 'registration', 'signup', 'sign up',
            'account created', 'new account'
        ]) and 'newsletter' not in subject and 'subscription' not in subject:
            return {
                'host': 'smtp.gmail.com',
                'port': 587,
                'username': getattr(settings, 'WELCOME_EMAIL_HOST_USER', 'juliengmanana@gmail.com'),
                'password': getattr(settings, 'WELCOME_EMAIL_HOST_PASSWORD', ''),
                'use_tls': True
            }
        
        # Newsletter subscription notifications - use juliengmanana@gmail.com SMTP
        elif any(keyword in subject for keyword in [
            'newsletter', 'subscription', 'subscribed'
        ]) and 'welcome' not in subject:
            return {
                'host': 'smtp.gmail.com',
                'port': 587,
                'username': getattr(settings, 'WELCOME_EMAIL_HOST_USER', 'juliengmanana@gmail.com'),
                'password': getattr(settings, 'WELCOME_EMAIL_HOST_PASSWORD', ''),
                'use_tls': True
            }
        
        # Contact form submissions - use contact.lamla1@gmail.com SMTP
        elif any(keyword in subject for keyword in [
            'contact form', 'lamlaai contact', 'contact submission'
        ]):
            return {
                'host': 'smtp.gmail.com',
                'port': 587,
                'username': getattr(settings, 'AUTH_EMAIL_HOST_USER', 'contact.lamla1@gmail.com'),
                'password': getattr(settings, 'AUTH_EMAIL_HOST_PASSWORD', ''),
                'use_tls': True
            }
        
        # Default to contact.lamla1@gmail.com SMTP for security-related emails
        else:
            return {
                'host': 'smtp.gmail.com',
                'port': 587,
                'username': getattr(settings, 'AUTH_EMAIL_HOST_USER', 'contact.lamla1@gmail.com'),
                'password': getattr(settings, 'AUTH_EMAIL_HOST_PASSWORD', ''),
                'use_tls': True
            }
    
    def _get_from_email_for_message(self, message):
        """
        Determine the appropriate from_email based on the message content.
        """
        subject = message.subject.lower() if message.subject else ""
        
        # Email confirmations and password resets - MUST come from contact.lamla1@gmail.com
        if any(keyword in subject for keyword in [
            'confirm', 'verification', 'verify', 'password reset', 
            'password change', 'reset password', 'change password', 'reset request'
        ]):
            return 'contact.lamla1@gmail.com'
        
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
        
        # Default to contact.lamla1@gmail.com for security-related emails
        else:
            return 'contact.lamla1@gmail.com'


def send_email(subject, message, recipient_list, from_email=None, html_message=None, fail_silently=False, **kwargs):
    """
    Reusable utility to send email with plain and HTML content, logging, and fallback.
    """
    logger = logging.getLogger(__name__)
    try:
        if from_email is None:
            from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'contact.lamla1@gmail.com')
        
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
        
        # Use the custom backend to send the email
        from django.core.mail import get_connection
        connection = get_connection()
        connection.send_messages([email])
        connection.close()
        
        logger.info(f"Email sent to {recipient_list} (subject: {subject}) from {from_email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email to {recipient_list}: {e}")
        if not fail_silently:
            raise
        return False 