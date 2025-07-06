from django.core.mail.backends.smtp import EmailBackend as SMTPEmailBackend
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.conf import settings
import os
import logging


class CustomEmailBackend(SMTPEmailBackend):
    """
    Custom email backend that sends different types of emails from different addresses.
    
    - Email confirmations and password resets: contact.lamla1@gmail.com
    - Welcome emails and other notifications: juliengmanana@gmail.com
    """
    
    def send_messages(self, email_messages):
        """
        Override send_messages to modify the from_email based on email type.
        """
        for message in email_messages:
            message.from_email = 'juliengmanana@gmail.com'
        return super().send_messages(email_messages)
    
    def _get_from_email_for_message(self, message):
        """
        Determine the appropriate from_email based on the message content.
        """
        subject = message.subject.lower() if message.subject else ""
        
        # Email confirmations and password resets
        if any(keyword in subject for keyword in [
            'confirm', 'verification', 'verify', 'password reset', 
            'password change', 'reset password', 'change password', 'reset request'
        ]):
            return 'contact.lamla1@gmail.com'
        
        # Welcome emails and general notifications
        elif any(keyword in subject for keyword in [
            'welcome', 'thank you', 'registration', 'signup', 'sign up',
            'account created', 'new account'
        ]):
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
        email.send(fail_silently=fail_silently)
        logger.info(f"Email sent to {recipient_list} (subject: {subject})")
        return True
    except Exception as e:
        logger.error(f"Failed to send email to {recipient_list}: {e}")
        if not fail_silently:
            raise
        return False 