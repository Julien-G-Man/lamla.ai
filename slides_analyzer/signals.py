from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from .email_backend import send_email
from allauth.account.signals import email_confirmed


@receiver(post_save, sender=User)
def send_welcome_email(sender, instance, created, **kwargs):
    """
    Send welcome email when a new user is created.
    """
    if created and instance.email:
        # Send welcome email from juliengmanana@gmail.com
        subject = "Welcome to LAMLA AI! 🎉"
        
        # Create welcome email content
        context = {
            'user': instance,
            'site_name': 'LAMLA AI',
            'site_domain': getattr(settings, 'SITE_DOMAIN', 'lamla-ai.onrender.com'),
        }
        
        # Render email templates
        html_message = render_to_string('emails/welcome_email.html', context)
        plain_message = render_to_string('emails/welcome_email.txt', context)
        
        # Send email using custom backend
        send_email(
            subject=subject,
            message=plain_message,
            recipient_list=[instance.email],
            from_email='juliengmanana@gmail.com',
            html_message=html_message
        )


@receiver(email_confirmed)
def send_welcome_email_after_confirmation(request, email_address, **kwargs):
    """
    Send a welcome email after the user confirms their email address.
    """
    user = email_address.user
    if user and user.email:
        subject = "Welcome to LAMLA AI! 🎉"
        context = {
            'user': user,
            'site_name': 'LAMLA AI',
            'site_domain': getattr(settings, 'SITE_DOMAIN', 'lamla-ai.onrender.com'),
        }
        html_message = render_to_string('emails/welcome_email.html', context)
        plain_message = render_to_string('emails/welcome_email.txt', context)
        send_email(
            subject=subject,
            message=plain_message,
            recipient_list=[user.email],
            from_email='juliengmanana@gmail.com',
            html_message=html_message
        )


def send_notification_email(user_email, subject, template_name, context, from_email=None):
    """
    Utility function to send notification emails with the correct sender.
    
    Args:
        user_email: Recipient email address
        subject: Email subject
        template_name: Template name for the email
        context: Context data for the template
        from_email: Custom from_email (optional)
    """
    if from_email is None:
        # Determine from_email based on subject
        subject_lower = subject.lower()
        
        # Security-related emails
        if any(keyword in subject_lower for keyword in [
            'confirm', 'verification', 'verify', 'password reset', 
            'password change', 'reset password', 'change password'
        ]):
            from_email = 'contact.lamla1@gmail.com'
        
        # Welcome and general notifications
        elif any(keyword in subject_lower for keyword in [
            'welcome', 'thank you', 'registration', 'signup', 'sign up',
            'account created', 'new account'
        ]):
            from_email = 'juliengmanana@gmail.com'
        
        # Default to contact.lamla1@gmail.com
        else:
            from_email = 'contact.lamla1@gmail.com'
    
    # Render email templates
    html_message = render_to_string(f'emails/{template_name}.html', context)
    plain_message = render_to_string(f'emails/{template_name}.txt', context)
    
    # Send email using custom backend
    return send_email(
        subject=subject,
        message=plain_message,
        recipient_list=[user_email],
        from_email=from_email,
        html_message=html_message
    ) 