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
                quiz_results = generate_questions_from_text(study_text, num_mcq, num_short, subject=subject)
                if not quiz_results or (not quiz_results.get('mcq_questions') and not quiz_results.get('short_questions')):
                    error_message = 'No questions could be generated. Please try with different or more detailed content.'
            except Exception as e:
                logger.error(f"Quiz generation error: {e}")
                error_message = f"Quiz generation failed: {str(e)}"
        if error_message:
            return render(request, 'slides_analyzer/custom_quiz.html', {
                'quiz_results': quiz_results,
                'error_message': error_message,
                'subject': subject,
                'num_mcq': num_mcq,
                'num_short': num_short,
                'study_text': study_text,
            })
        # Store questions in session and redirect to quiz page
        request.session['quiz_questions'] = quiz_results
        request.session['quiz_time'] = int(request.POST.get('quiz_time', 10))
        return redirect('quiz')
    else:
        return render(request, 'slides_analyzer/custom_quiz.html')

def custom_quiz(request):
    return render(request, 'slides_analyzer/custom_quiz.html')

def exam_analyzer(request):
    return render(request, 'slides_analyzer/exam_analyzer.html')

def quiz(request):
    quiz_questions = request.session.get('quiz_questions')
    quiz_time = request.session.get('quiz_time', 10)
    if not quiz_questions:
        messages.error(request, 'No quiz has been generated. Please create a quiz first.')
        return redirect('custom_quiz')
    return render(request, 'slides_analyzer/quiz.html', {
        'questions': quiz_questions,
        'quiz_time': quiz_time,
    })

def quiz_results(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            user_answers = data.get('user_answers', {})
            quiz_questions = request.session.get('quiz_questions', {})
            mcq = quiz_questions.get('mcq_questions', [])
            short = quiz_questions.get('short_questions', [])
            all_questions = mcq + short
            results = {
                'total': len(all_questions),
                'correct': 0,
                'details': []
            }
            # Split user answers for MCQ and short
            user_mcq_answers = {}
            user_short_answers = {}
            for idx in range(len(mcq)):
                ans = user_answers.get(str(idx)) or user_answers.get(idx)
                user_mcq_answers[idx] = ans
            for idx in range(len(mcq), len(all_questions)):
                ans = user_answers.get(str(idx)) or user_answers.get(idx)
                user_short_answers[idx - len(mcq)] = ans
            # Grade MCQs
            for idx, q in enumerate(mcq):
                user_ans = user_mcq_answers.get(idx, '').strip().upper() if user_mcq_answers.get(idx) else ''
                correct_ans = q.get('answer', '').strip().upper()
                correct = user_ans == correct_ans
                results['details'].append({
                    'question': q.get('question'),
                    'user_answer': user_ans,
                    'correct_answer': correct_ans,
                    'is_correct': correct
                })
                if correct:
                    results['correct'] += 1
            # Store short answers (no grading)
            for idx, q in enumerate(short):
                user_ans = user_short_answers.get(idx, '')
                results['details'].append({
                    'question': q.get('question'),
                    'user_answer': user_ans,
                    'correct_answer': q.get('answer'),
                    'is_correct': None
                })
            # Store for results page
            request.session['quiz_results'] = results
            request.session['quiz_user_answers'] = user_answers
            return JsonResponse({'status': 'ok'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    else:
        results = request.session.get('quiz_results')
        quiz_questions = request.session.get('quiz_questions', {})
        user_answers = request.session.get('quiz_user_answers', {})
        mcq_questions = quiz_questions.get('mcq_questions', [])
        short_questions = quiz_questions.get('short_questions', [])
        total = results['total'] if results else 0
        score = results['correct'] if results else 0
        score_percent = (score / total * 100) if total else 0
        wrong_percent = (100 - score_percent) if total else 0
        context = {
            'score': score,
            'total': total,
            'score_percent': score_percent,
            'wrong_percent': wrong_percent,
            'mcq_questions': mcq_questions,
            'short_questions': short_questions,
            'user_answers': user_answers,
            'results': results
        }
        return render(request, 'slides_analyzer/quiz_results.html', context)

def flashcards(request):
    return render(request, 'slides_analyzer/flashcards.html')

def test_token(request):
    return HttpResponse('test_token stub')

def test_flashcard_generator(request):
    return render(request, 'slides_analyzer/test_flashcard_generator.html')

def test_chatbot(request):
    return render(request, 'test_chatbot.html')

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
    """Handle support request from chatbot"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            name = data.get('name', '').strip()
            email = data.get('email', '').strip()
            subject = data.get('subject', '').strip()
            message = data.get('message', '').strip()
            
            # Validate required fields
            if not all([name, email, subject, message]):
                return JsonResponse({
                    'status': 'error',
                    'message': 'All fields are required.'
                })
            
            # Save to Contact model
            Contact.objects.create(
                name=name,
                email=email,
                subject=subject,
                message=message
            )
            
            # Send notification to admin
            admin_subject = f"Chatbot Support Request: {subject}"
            admin_body = f"Name: {name}\nEmail: {email}\nSubject: {subject}\n\nMessage:\n{message}"
            admin_recipient = getattr(settings, 'WELCOME_EMAIL_HOST_USER', 'juliengmanana@gmail.com')
            
            try:
                send_email(
                    subject=admin_subject,
                    message=admin_body,
                    recipient_list=[admin_recipient],
                    from_email='lamlaaiteam@gmail.com',
                )
            except Exception as e:
                logger.error(f"Chatbot support request admin email error: {e}")
            
            return JsonResponse({
                'status': 'success',
                'message': 'Your support request has been sent successfully! We will get back to you soon.'
            })
            
        except json.JSONDecodeError:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid request data.'
            })
        except Exception as e:
            logger.error(f"Chatbot support request error: {e}")
            return JsonResponse({
                'status': 'error',
                'message': 'An error occurred while sending your request.'
            })
    
    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method.'
    })

def chatbot_message(request):
    """Handle chatbot message and generate response"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            message = data.get('message', '').strip()
            session_id = data.get('session_id', '')
            
            if not message:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Message is required.'
                })
            
            # Save user message to database
            user = request.user if request.user.is_authenticated else None
            ChatMessage.objects.create(
                user=user,
                session_id=session_id,
                message_type='user',
                content=message
            )
            
            # Get conversation history for context
            conversation_history = []
            if session_id:
                recent_messages = ChatMessage.objects.filter(
                    session_id=session_id
                ).order_by('-created_at')[:12]  # Last 12 messages
                conversation_history = [
                    {
                        'message_type': msg.message_type,
                        'content': msg.content
                    }
                    for msg in reversed(recent_messages)  # Reverse to get chronological order
                ]
            
            # Generate response using chatbot service
            response = chatbot_service.generate_response(message, conversation_history)
            
            # Save bot response to database
            ChatMessage.objects.create(
                user=user,
                session_id=session_id,
                message_type='bot',
                content=response
            )
            
            return JsonResponse({
                'status': 'success',
                'response': response
            })
            
        except json.JSONDecodeError:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid request data.'
            })
        except Exception as e:
            logger.error(f"Chatbot message error: {e}")
            return JsonResponse({
                'status': 'error',
                'message': 'An error occurred while processing your message.'
            })
    
    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method.'
    })

def chatbot_suggestions(request):
    """Get suggested questions for the chatbot"""
    try:
        suggestions = chatbot_service.get_suggested_questions()
        return JsonResponse({
            'status': 'success',
            'suggestions': suggestions
        })
    except Exception as e:
        logger.error(f"Chatbot suggestions error: {e}")
        return JsonResponse({
            'status': 'error',
            'message': 'Failed to load suggestions.'
        })

def chatbot_history(request):
    """Get chat history for a session"""
    if request.method == 'GET':
        session_id = request.GET.get('session_id', '')
        if not session_id:
            return JsonResponse({
                'status': 'error',
                'message': 'Session ID is required.'
            })
        
        try:
            messages = ChatMessage.objects.filter(
                session_id=session_id
            ).order_by('created_at')
            
            history = [
                {
                    'message_type': msg.message_type,
                    'content': msg.content,
                    'created_at': msg.created_at.isoformat()
                }
                for msg in messages
            ]
            
            return JsonResponse({
                'status': 'success',
                'history': history
            })
            
        except Exception as e:
            logger.error(f"Chatbot history error: {e}")
            return JsonResponse({
                'status': 'error',
                'message': 'Failed to load chat history.'
            })
    
    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method.'
    })
