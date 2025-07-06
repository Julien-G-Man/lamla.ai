from django.core.mail.backends.smtp import EmailBackend as SMTPEmailBackend
from django.core.mail import EmailMessage
from django.conf import settings
import os


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
            # Determine the appropriate from_email based on subject or other criteria
            from_email = self._get_from_email_for_message(message)
            message.from_email = from_email
            
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


def send_email_with_custom_from(subject, message, recipient_list, from_email=None, **kwargs):
    """
    Utility function to send emails with custom from_email.
    
    Args:
        subject: Email subject
        message: Email message content
        recipient_list: List of recipient email addresses
        from_email: Custom from_email (optional, will be determined automatically if not provided)
        **kwargs: Additional arguments for EmailMessage
    """
    if from_email is None:
        # Determine from_email based on subject
        subject_lower = subject.lower()
        
        # Email confirmations and password resets
        if any(keyword in subject_lower for keyword in [
            'confirm', 'verification', 'verify', 'password reset', 
            'password change', 'reset password', 'change password', 'reset request'
        ]):
            from_email = 'contact.lamla1@gmail.com'
        
        # Welcome emails and general notifications
        elif any(keyword in subject_lower for keyword in [
            'welcome', 'thank you', 'registration', 'signup', 'sign up',
            'account created', 'new account'
        ]):
            from_email = 'juliengmanana@gmail.com'
        
        # Default to contact.lamla1@gmail.com for security-related emails
        else:
            from_email = 'contact.lamla1@gmail.com'
    
    email = EmailMessage(
        subject=subject,
        body=message,
        from_email=from_email,
        to=recipient_list,
        **kwargs
    )
    
    return email.send() 