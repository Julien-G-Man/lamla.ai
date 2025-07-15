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
    return HttpResponse('generate_questions stub')

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
    return JsonResponse({'result': 'ajax_extract_text stub'})

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

def contact(request):
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
    return JsonResponse({'result': 'get_subscribers_data stub'})

def toggle_subscription_status(request):
    return JsonResponse({'result': 'toggle_subscription_status stub'})

def download_users_csv(request):
    return HttpResponse('download_users_csv stub')

def get_users_data(request):
    return JsonResponse({'result': 'get_users_data stub'})

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
