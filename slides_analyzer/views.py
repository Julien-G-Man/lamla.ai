from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as auth_logout
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.exceptions import ValidationError
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_POST
from django.db import transaction
from django.utils import timezone
from django.core.paginator import Paginator
from django.db.models import Q
from allauth.account.views import LoginView as AllauthLoginView
from allauth.account.adapter import DefaultAccountAdapter
import json
import logging
import os
import tempfile
from datetime import datetime, timedelta
from .models import (
    Question, QuestionCache, Contact, Feedback, 
    Subscription, UserProfile, ChatbotKnowledge, ChatMessage
)
from .chatbot_service import chatbot_service
from .email_backend import send_email
from .question_generator import generate_questions_from_text
from .flashcard_generator import generate_flashcards_from_text
import PyPDF2
import docx
import io
import base64
from PIL import Image
import pytesseract
import re
from django.core.validators import validate_email
from django.core.exceptions import ValidationError as DjangoValidationError

# Custom allauth adapter to ensure correct email sender
class CustomAccountAdapter(DefaultAccountAdapter):
    def send_mail(self, template_prefix, email, context):
        """
        Override send_mail to use our custom email backend and correct sender
        """
        from django.core.mail import EmailMessage
        from django.template.loader import render_to_string
        from django.utils.html import strip_tags
        
        # Determine the correct sender based on email type
        if 'password_reset' in template_prefix or 'email_confirmation' in template_prefix:
            from_email = getattr(settings, 'SECURITY_EMAIL_SENDER', 'lamlaaiteam@gmail.com')
        else:
            from_email = getattr(settings, 'WELCOME_EMAIL_SENDER', 'juliengmanana@gmail.com')
        
        # Render email templates
        subject = render_to_string(f'{template_prefix}_subject.txt', context)
        subject = ''.join(subject.splitlines()).strip()
        if not subject.startswith('[Lamla AI]'):
            subject = f'[Lamla AI] {subject}'
        
        html_message = render_to_string(f'{template_prefix}_message.html', context)
        plain_message = render_to_string(f'{template_prefix}_message.txt', context)
        
        # Create email message
        msg = EmailMessage(
            subject=subject,
            body=plain_message,
            from_email=from_email,
            to=[email]
        )
        msg.content_subtype = "html"
        
        # Use our custom send_email function
        return send_email(
            subject=subject,
            message=plain_message,
            recipient_list=[email],
            from_email=from_email,
            html_message=html_message,
            fail_silently=False
        )

def home(request):
    return render(request, 'slides_analyzer/home.html')

def dashboard(request):
    return render(request, 'slides_analyzer/dashboard.html')

def user_profile(request):
    return render(request, 'slides_analyzer/user_profile.html')

def upload_slides(request):
    return render(request, 'slides_analyzer/upload.html')

def generate_questions(request):
    if request.method == 'POST':
        study_text = request.POST.get('extractedText', '').strip()
        num_mcq = int(request.POST.get('num_mcq', 5))
        num_short = int(request.POST.get('num_short', 3))
        subject = request.POST.get('subject', '')
        error_message = None
        quiz_results = None
        if not study_text or len(study_text) < 30:
            error_message = 'Please provide at least 30 characters of study material.'
        else:
            try:
                quiz_results = generate_questions_from_text(study_text, num_mcq, num_short)
                if not quiz_results or (not quiz_results.get('mcq_questions') and not quiz_results.get('short_questions')):
                    error_message = 'No questions could be generated. Please try with different or more detailed content.'
            except Exception as e:
                logger.error(f"Quiz generation error: {e}")
                error_message = f"Quiz generation failed: {str(e)}"
        return render(request, 'slides_analyzer/custom_quiz.html', {
            'quiz_results': quiz_results,
            'error_message': error_message,
            'subject': subject,
            'num_mcq': num_mcq,
            'num_short': num_short,
            'study_text': study_text,
        })
    else:
        return render(request, 'slides_analyzer/custom_quiz.html')

def custom_quiz(request):
    return render(request, 'slides_analyzer/custom_quiz.html')

def exam_analyzer(request):
    return render(request, 'slides_analyzer/exam_analyzer.html')

def quiz(request):
    return render(request, 'slides_analyzer/quiz.html')

def quiz_results(request):
    return render(request, 'slides_analyzer/quiz_results.html')

def flashcards(request):
    return render(request, 'slides_analyzer/flashcards.html')

def test_token(request):
    return HttpResponse('test_token stub')

def test_flashcard_generator(request):
    return HttpResponse('test_flashcard_generator stub')

def about(request):
    return render(request, 'slides_analyzer/about.html')

def ajax_extract_text(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=405)

    if 'slide_file' not in request.FILES:
        return JsonResponse({'error': 'No file uploaded'}, status=400)

    file = request.FILES['slide_file']
    filename = file.name.lower()
    file_ext = os.path.splitext(filename)[1]
    max_size = 10 * 1024 * 1024  # 10MB
    if file.size > max_size:
        return JsonResponse({'error': 'File too large (max 10MB)'}, status=400)

    try:
        if file_ext == '.pdf':
            # PDF extraction
            pdf_reader = PyPDF2.PdfReader(file)
            text = ''
            for page in pdf_reader.pages:
                text += page.extract_text() or ''
        elif file_ext == '.docx':
            # DOCX extraction
            doc = docx.Document(file)
            text = '\n'.join([para.text for para in doc.paragraphs])
        elif file_ext == '.pptx':
            # PPTX extraction
            from pptx import Presentation
            prs = Presentation(file)
            text = ''
            for slide in prs.slides:
                for shape in slide.shapes:
                    if hasattr(shape, "text"):
                        text += shape.text + '\n'
        elif file_ext == '.txt':
            # TXT extraction
            text = file.read().decode('utf-8', errors='ignore')
        else:
            return JsonResponse({'error': 'Unsupported file type. Please upload PDF, DOCX, PPTX, or TXT.'}, status=400)

        # Clean up text
        text = text.strip()
        if not text:
            return JsonResponse({'error': 'No text could be extracted from the file.'}, status=400)
        # Optionally limit length for performance
        if len(text) > 20000:
            text = text[:20000] + '\n... [truncated]'
        return JsonResponse({'text': text})
    except Exception as e:
        logger.error(f"Text extraction error: {e}")
        return JsonResponse({'error': f'Failed to extract text: {str(e)}'}, status=500)

def submit_feedback(request):
    return JsonResponse({'result': 'submit_feedback stub'})

def subscribe_newsletter(request):
    return JsonResponse({'result': 'subscribe_newsletter stub'})

from allauth.account.views import LoginView as AllauthLoginView
class CustomLoginView(AllauthLoginView):
    template_name = 'account/login.html'

def custom_logout(request):
    auth_logout(request)
    return redirect('home')

def privacy_policy(request):
    return render(request, 'slides_analyzer/privacy_policy.html')

def terms_of_service(request):
    return render(request, 'slides_analyzer/terms_of_service.html')

def cookie_policy(request):
    return render(request, 'slides_analyzer/cookie_policy.html')

# Remove @csrf_exempt for production
# Add logging for submissions and errors
import logging
logger = logging.getLogger(__name__)

def contact(request):
    print("CONTACT VIEW CALLED")  # Debug: confirm view is called
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        subject = request.POST.get('subject', '').strip()
        message = request.POST.get('message', '').strip()
        errors = []

        # Validate fields
        if not name:
            errors.append('Name is required.')
        if not email:
            errors.append('Email is required.')
        else:
            try:
                validate_email(email)
            except DjangoValidationError:
                errors.append('Please enter a valid email address.')
        if not subject:
            errors.append('Subject is required.')
        if not message:
            errors.append('Message is required.')

        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'slides_analyzer/contact.html', {
                'name': name,
                'email': email,
                'subject': subject,
                'message': message,
            })

        # Save to Contact model with error handling
        try:
            Contact.objects.create(
                name=name,
                email=email,
                subject=subject,
                message=message
            )
            logger.info(f"Contact form submitted by {name} <{email}>: {subject}")
        except Exception as e:
            logger.error(f"Contact form DB save error: {e}")
            messages.error(request, 'There was an error saving your message. Please try again later.')
            return render(request, 'slides_analyzer/contact.html', {
                'name': name,
                'email': email,
                'subject': subject,
                'message': message,
            })
        
        # 1. Send notification to admin (Julien)
        admin_subject = f"Contact Form: {subject}"
        admin_body = f"Name: {name}\nEmail: {email}\nSubject: {subject}\n\nMessage:\n{message}"
        admin_recipient = getattr(settings, 'WELCOME_EMAIL_HOST_USER', 'juliengmanana@gmail.com')
        try:
            send_email(
                subject=admin_subject,
                message=admin_body,
                recipient_list=[admin_recipient],
                from_email='lamlaaiteam@gmail.com',
            )
            logger.info(f"Contact notification sent to admin: {admin_recipient}")
        except Exception as e:
            logger.error(f"Contact form admin email error: {e}")
            messages.error(request, 'There was an error sending your message to our team. Please try again later.')
            return render(request, 'slides_analyzer/contact.html', {
                'name': name,
                'email': email,
                'subject': subject,
                'message': message,
            })

        # 2. Send auto-response to user
        user_subject = "We received your message at Lamla AI!"
        user_body = (
            f"Hi {name},\n\n"
            "Thank you for contacting Lamla AI! Your message has been received and our team will get back to you as soon as possible.\n\n"
            "Here is a copy of your message:\n"
            f"Subject: {subject}\n"
            f"Message: {message}\n\n"
            "If you have any further questions, feel free to reply to this email.\n\n"
            "Best regards,\nThe Lamla AI Team"
        )
        try:
            send_email(
                subject=user_subject,
                message=user_body,
                recipient_list=[email],
                from_email='lamlaaiteam@gmail.com',
            )
            logger.info(f"Auto-response sent to user: {email}")
        except Exception as e:
            logger.error(f"Contact form auto-response error: {e}")
            # Don't block user on auto-response failure

        messages.success(request, 'Your message has been sent! We will get back to you soon.')
        return redirect('contact')
    else:
        return render(request, 'slides_analyzer/contact.html')
        
def feedback_analytics(request):
    return render(request, 'slides_analyzer/feedback_analytics.html')

def view_subscribers(request):
    return render(request, 'slides_analyzer/subscribers.html')

def view_users(request):
    return render(request, 'slides_analyzer/users.html')

def download_subscribers_csv(request):
    return HttpResponse('download_subscribers_csv stub')

def get_subscribers_data(request):
    """
    Return JSON data for all newsletter subscribers, including stats.
    """
    if not request.user.is_staff:
        return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)
    from .models import Subscription
    subs = Subscription.objects.all().order_by('-created_at')
    data = []
    active_count = 0
    inactive_count = 0
    for sub in subs:
        data.append({
            'id': sub.id,
            'email': sub.email,
            'created_at': sub.created_at.strftime('%Y-%m-%d %H:%M'),
            'is_active': sub.is_active,
        })
        if sub.is_active:
            active_count += 1
        else:
            inactive_count += 1
    stats = {
        'total_subscribers': subs.count(),
        'active_subscribers': active_count,
        'inactive_subscribers': inactive_count,
    }
    return JsonResponse({'success': True, 'subscribers': data, 'stats': stats})


def get_users_data(request):
    """
    Return JSON data for all users, including stats.
    """
    if not request.user.is_staff:
        return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)
    from django.contrib.auth.models import User
    users = User.objects.all().order_by('-date_joined')
    data = []
    active_count = 0
    inactive_count = 0
    for user in users:
        # Try to get profile, handle if missing
        try:
            profile = user.profile
            is_deleted = profile.is_deleted
        except Exception:
            is_deleted = False
        if is_deleted:
            continue  # Skip deleted users
        full_name = f"{user.first_name} {user.last_name}".strip() or user.username
        role = 'Admin' if user.is_staff or user.is_superuser else 'User'
        is_active = user.is_active
        if is_active:
            active_count += 1
        else:
            inactive_count += 1
        # 2FA placeholder (customize if you have 2FA field)
        two_fa = 'Enabled' if hasattr(user, 'two_fa_enabled') and user.two_fa_enabled else 'Disabled'
        data.append({
            'id': user.id,
            'full_name': full_name,
            'email': user.email,
            'role': role,
            'is_active': is_active,
            'date_joined': user.date_joined.strftime('%Y-%m-%d %H:%M'),
            'two_fa': two_fa,
        })
    stats = {
        'total_users': len(data),
        'active_users': active_count,
        'inactive_users': inactive_count,
    }
    return JsonResponse({'success': True, 'users': data, 'stats': stats})

def toggle_subscription_status(request):
    return JsonResponse({'result': 'toggle_subscription_status stub'})

def download_users_csv(request):
    return HttpResponse('download_users_csv stub')

def delete_user(request):
    return JsonResponse({'result': 'delete_user stub'})

def restore_user(request):
    return JsonResponse({'result': 'restore_user stub'})

def toggle_user_status(request):
    return JsonResponse({'result': 'toggle_user_status stub'})

def view_deleted_users(request):
    return render(request, 'slides_analyzer/deleted_users.html')

def get_deleted_users_data(request):
    return JsonResponse({'result': 'get_deleted_users_data stub'})

def chatbot_support_request(request):
    return JsonResponse({'result': 'chatbot_support_request stub'})

def chatbot_message(request):
    return JsonResponse({'result': 'chatbot_message stub'})

def chatbot_suggestions(request):
    return JsonResponse({'result': 'chatbot_suggestions stub'})

def chatbot_history(request):
    return JsonResponse({'result': 'chatbot_history stub'})
