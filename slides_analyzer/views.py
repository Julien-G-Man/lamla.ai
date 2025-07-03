from django.shortcuts import render, redirect
from django.core.files.storage import FileSystemStorage
from pptx import Presentation
from PyPDF2 import PdfReader
import os
import google.generativeai as genai
from django.conf import settings
import logging
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import Question, Quiz, Feedback, Subscription, Contact, UserProfile
from .question_generator import QuestionGenerator
from .flashcard_generator import FlashcardGenerator
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as auth_logout
from django.core.exceptions import ValidationError
import mimetypes
from django.views.decorators.csrf import csrf_exempt
from allauth.account.views import LoginView as AllauthLoginView
import json
import requests
from django.contrib import messages
from django.core.mail import send_mail
from django.db import IntegrityError
from django.core.validators import validate_email
from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils import timezone
import dj_database_url
from django.db import models

# Set up logging
logger = logging.getLogger(__name__)

# Initialize the question generator
try:
    question_generator = QuestionGenerator()
    logger.info("Question Generator initialized successfully")
except Exception as e:
    logger.error(f"Error initializing Question Generator: {e}")
    question_generator = None

# Initialize the flashcard generator
try:
    flashcard_generator = FlashcardGenerator()
    logger.info("Flashcard Generator initialized successfully")
except Exception as e:
    logger.error(f"Error initializing Flashcard Generator: {e}")
    flashcard_generator = None

# Configure Gemini API
try:
    if not hasattr(settings, 'GEMINI_API_KEY') or not settings.GEMINI_API_KEY:
        logger.warning("GEMINI_API_KEY is not set in settings.py")
    else:
        genai.configure(api_key=settings.GEMINI_API_KEY)
        logger.info("Gemini API configured successfully")
except Exception as e:
    logger.error(f"Error configuring Gemini API: {e}")

def validate_file_upload(file):
    """Validate uploaded file size and type"""
    # Check file size
    max_size = getattr(settings, 'MAX_UPLOAD_SIZE', 10 * 1024 * 1024)  # 10MB default
    if file.size > max_size:
        raise ValidationError(f"File size must be under {max_size // (1024*1024)}MB")
    
    # Check file type
    allowed_types = getattr(settings, 'ALLOWED_FILE_TYPES', ['.pdf', '.pptx'])
    file_ext = os.path.splitext(file.name)[1].lower()
    if file_ext not in allowed_types:
        raise ValidationError(f"File type {file_ext} is not allowed. Allowed types: {', '.join(allowed_types)}")

def test_token(request):
    """Test view to verify Hugging Face token is loaded correctly"""
    token = os.getenv('HUGGING_FACE_API_TOKEN')
    if token:
        # Show only first 4 and last 4 characters of token for security
        masked_token = f"{token[:4]}...{token[-4:]}" if len(token) > 8 else "***"
        return JsonResponse({
            'status': 'success',
            'message': 'Token is loaded',
            'token_preview': masked_token
        })
    else:
        return JsonResponse({
            'status': 'error',
            'message': 'Token not found in environment variables'
        }, status=500)

def extract_text_from_file(uploaded_file):
    """Extract text from pptx, pdf, or txt file-like object. Returns extracted text or raises Exception."""
    from io import TextIOWrapper
    file_name = uploaded_file.name
    fs = FileSystemStorage()
    filename = fs.save(uploaded_file.name, uploaded_file)
    file_path = fs.path(filename)
    extracted_text = ""
    try:
        if file_name.lower().endswith('.pptx'):
            prs = Presentation(file_path)
            for slide in prs.slides:
                for shape in slide.shapes:
                    if hasattr(shape, "text_frame") and shape.text_frame:
                        extracted_text += shape.text_frame.text + "\n"
        elif file_name.lower().endswith('.pdf'):
            reader = PdfReader(file_path)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    extracted_text += page_text + "\n"
        elif file_name.lower().endswith('.txt'):
            with open(file_path, 'r', encoding='utf-8') as f:
                extracted_text = f.read()
        else:
            raise Exception('Unsupported file type.')
    finally:
        try:
            fs.delete(filename)
        except Exception:
            pass
    return extracted_text

@login_required
def upload_slides(request):
    extracted_text = ""
    if request.method == 'POST' and request.FILES.get('slide_file'):
        uploaded_file = request.FILES['slide_file']
        try:
            validate_file_upload(uploaded_file)
            extracted_text = extract_text_from_file(uploaded_file)
            request.session['extracted_text'] = extracted_text
        except ValidationError as e:
            return render(request, 'slides_analyzer/error.html', {'message': str(e)})
        except Exception as e:
            logger.error(f"File upload failed: {e}")
            return render(request, 'slides_analyzer/error.html', {'message': f'File upload failed: {str(e)}'})
        return render(request, 'slides_analyzer/display_text.html', {'text': extracted_text})
    return render(request, 'slides_analyzer/upload.html')

@require_http_methods(["POST"])
@login_required
def generate_questions(request):
    try:
        if not question_generator:
            return JsonResponse({
                'error': 'Question Generator not properly initialized'
            }, status=500)

        # Get the text content from the request
        text_content = request.POST.get('text', '')
        
        # If no text provided, try to get it from the file or session
        if not text_content:
            if request.FILES.get('slide_file'):
                uploaded_file = request.FILES['slide_file']
                
                try:
                    validate_file_upload(uploaded_file)
                except ValidationError as e:
                    return JsonResponse({'error': str(e)}, status=400)
                
                file_name = uploaded_file.name
                fs = FileSystemStorage()
                filename = fs.save(uploaded_file.name, uploaded_file)
                file_path = fs.path(filename)

                try:
                    extracted_text = ""
                    if file_name.lower().endswith('.pptx'):
                        prs = Presentation(file_path)
                        for slide in prs.slides:
                            for shape in slide.shapes:
                                if hasattr(shape, "text_frame") and shape.text_frame:
                                    extracted_text += shape.text_frame.text + "\n"
                    elif file_name.lower().endswith('.pdf'):
                        reader = PdfReader(file_path)
                        for page in reader.pages:
                            page_text = page.extract_text()
                            if page_text:
                                extracted_text += page_text + "\n"
                    
                    text_content = extracted_text
                    
                except Exception as e:
                    logger.error(f"Error processing file: {e}")
                    return JsonResponse({
                        'error': f'Error processing file: {str(e)}'
                    }, status=500)
                finally:
                    try:
                        fs.delete(filename)
                    except Exception as e:
                        logger.warning(f"Failed to delete temporary file: {e}")
            else:
                # Try to get text from session
                text_content = request.session.get('extracted_text', '')
        
        if not text_content:
            return JsonResponse({
                'error': 'No text content provided'
            }, status=400)

        # Get parameters from the request
        try:
            num_mcq = int(request.POST.get('num_mcq', 3))
            num_short = int(request.POST.get('num_short', 2))
            
            # Validate parameters
            if num_mcq < 0 or num_short < 0:
                return JsonResponse({
                    'error': 'Number of questions must be positive'
                }, status=400)
            if num_mcq > 10 or num_short > 10:
                return JsonResponse({
                    'error': 'Maximum 10 questions of each type allowed'
                }, status=400)
        except ValueError:
            return JsonResponse({
                'error': 'Invalid number of questions specified'
            }, status=400)
        
        # Generate questions using the QuestionGenerator
        try:
            questions = question_generator.generate_questions(
                text=text_content,
                num_mcq=num_mcq,
                num_short=num_short
            )
            
            if "error" in questions:
                return JsonResponse({
                    'error': questions["error"]
                }, status=500)
            
            # Ensure only the requested number of questions are stored
            if 'mcq_questions' in questions:
                questions['mcq_questions'] = questions['mcq_questions'][:num_mcq]
            if 'short_questions' in questions:
                questions['short_questions'] = questions['short_questions'][:num_short]
            
            # Debug print to check how many questions are being stored
            print('DEBUG: Storing MCQs:', len(questions.get('mcq_questions', [])), 'Short:', len(questions.get('short_questions', [])))
            # Clear old questions before storing new ones
            request.session['questions'] = None
            request.session['questions'] = questions
            
            # Redirect to the quiz page
            return redirect('quiz')

        except Exception as e:
            logger.error(f"Error generating questions: {str(e)}")
            return JsonResponse({
                'error': 'Failed to generate questions',
                'details': str(e)
            }, status=500)

    except Exception as e:
        logger.error(f"Error in generate_questions: {str(e)}")
        return JsonResponse({
            'error': 'An error occurred while generating questions',
            'details': str(e)
        }, status=500)

@login_required
def custom_quiz(request):
    if request.method == 'POST':
        extracted_text = request.POST.get('extractedText', '').strip()
        try:
            num_mcq = int(request.POST.get('num_mcq', 5))
            num_short = int(request.POST.get('num_short', 3))
            quiz_time = int(request.POST.get('quiz_time', 10))
        except Exception:
            num_mcq = 5
            num_short = 3
            quiz_time = 10
        if not extracted_text:
            error_message = 'No extracted text provided.'
            return render(request, 'slides_analyzer/custom_quiz.html', {
                'user_authenticated': request.user.is_authenticated,
                'quiz_results': None,
                'error_message': error_message
            })
        else:
            try:
                questions = question_generator.generate_questions(
                    text=extracted_text,
                    num_mcq=num_mcq,
                    num_short=num_short
                )
                # Ensure only the requested number of questions are stored
                if 'mcq_questions' in questions:
                    questions['mcq_questions'] = questions['mcq_questions'][:num_mcq]
                if 'short_questions' in questions:
                    questions['short_questions'] = questions['short_questions'][:num_short]
                print('DEBUG: Generated questions:', questions)
                if 'error' in questions and questions['error']:
                    error_message = (
                        'Sorry, we could not generate questions at this time. Reason: ' + str(questions['error']) +
                        '<br>Possible causes: API quota exceeded, invalid API key, or service unavailable.'
                    )
                    return render(request, 'slides_analyzer/custom_quiz.html', {
                        'user_authenticated': request.user.is_authenticated,
                        'quiz_results': None,
                        'error_message': error_message
                    })
                request.session['quiz_time'] = quiz_time
                request.session['questions'] = questions
                return redirect('quiz')
            except Exception as e:
                error_message = f'Error generating questions: {str(e)}'
                return render(request, 'slides_analyzer/custom_quiz.html', {
                    'user_authenticated': request.user.is_authenticated,
                    'quiz_results': None,
                    'error_message': error_message
                })
    return render(request, 'slides_analyzer/custom_quiz.html', {
        'user_authenticated': request.user.is_authenticated,
        'quiz_results': None,
        'error_message': None
    })

def home(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        
        if not email:
            messages.error(request, "Please enter a valid email address.")
            return redirect('home')
        
        try:
            # Validate email format
            validate_email(email)
            
            # Check if already subscribed
            existing_subscription = Subscription.objects.filter(email=email).first()
            if existing_subscription:
                if existing_subscription.is_active:
                    messages.info(request, "You're already subscribed to our newsletter!")
                else:
                    existing_subscription.is_active = True
                    existing_subscription.save()
                    messages.success(request, "Welcome back! Your subscription has been reactivated.")
            else:
                # Create new subscription
                subscription = Subscription.objects.create(email=email)
                messages.success(request, "Thank you for subscribing! You'll receive updates about new features and study tips.")
                
                # Send email notification to admin
                try:
                    send_mail(
                        subject='New Newsletter Subscription',
                        message=f'A new student has subscribed to the newsletter:\n\nEmail: {email}\nDate: {subscription.created_at.strftime("%Y-%m-%d %H:%M:%S")}',
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[settings.ADMIN_EMAIL] if hasattr(settings, 'ADMIN_EMAIL') else ['admin@lamla.ai'],
                        fail_silently=True,
                    )
                except Exception as e:
                    logger.warning(f"Failed to send subscription notification email: {e}")
                    
        except DjangoValidationError:
            messages.error(request, "Please enter a valid email address.")
        except IntegrityError:
            messages.error(request, "This email is already subscribed.")
        except Exception as e:
            logger.error(f"Error processing subscription: {e}")
            messages.error(request, "Sorry, there was an error processing your subscription. Please try again.")
        
        return redirect('home')
    
    return render(request, 'slides_analyzer/home.html', {'user_authenticated': request.user.is_authenticated})

@login_required
def exam_analyzer(request):
    if request.method == 'POST':
        subject = request.POST.get('subject', '').strip()
        extracted_text = request.POST.get('extractedText', '').strip()
        if not extracted_text:
            error_message = 'No extracted text provided.'
            return render(request, 'slides_analyzer/exam_analyzer.html', {
                'user_authenticated': request.user.is_authenticated,
                'analyzer_results': None,
                'error_message': error_message
            })
        else:
            try:
                num_mcq = int(request.POST.get('num_mcq', 5))
                num_short = int(request.POST.get('num_short', 3))
                questions = question_generator.generate_questions(
                    text=extracted_text,
                    num_mcq=num_mcq,
                    num_short=num_short
                )
                if 'error' in questions and questions['error']:
                    error_message = (
                        'Sorry, we could not generate questions at this time. Reason: ' + str(questions['error']) +
                        '<br>Possible causes: API quota exceeded, invalid API key, or service unavailable.'
                    )
                    return render(request, 'slides_analyzer/exam_analyzer.html', {
                        'user_authenticated': request.user.is_authenticated,
                        'analyzer_results': None,
                        'error_message': error_message
                    })
                request.session['questions'] = questions
                return redirect('quiz')
            except Exception as e:
                error_message = f'Error analyzing text: {str(e)}'
                return render(request, 'slides_analyzer/exam_analyzer.html', {
                    'user_authenticated': request.user.is_authenticated,
                    'analyzer_results': None,
                    'error_message': error_message
                })
    return render(request, 'slides_analyzer/exam_analyzer.html', {
        'user_authenticated': request.user.is_authenticated,
        'analyzer_results': None,
        'error_message': None
    })

@login_required
def quiz(request):
    # Get questions from session
    questions = request.session.get('questions', {})
    print('DEBUG: Session questions:', questions)
    quiz_time = request.session.get('quiz_time', 10)
    if not questions or (not questions.get('mcq_questions') and not questions.get('short_questions')):
        return redirect('custom_quiz')
    return render(request, 'slides_analyzer/quiz.html', {'questions': questions, 'user_authenticated': request.user.is_authenticated, 'quiz_time': quiz_time})

@login_required
def flashcards(request):
    flashcard_results = None
    error_message = None
    flashcard_type = 'general'
    
    if request.method == 'POST':
        extracted_text = request.POST.get('extractedText', '').strip()
        flashcard_type = request.POST.get('flashcard_type', 'general')
        try:
            num_flashcards = int(request.POST.get('num_flashcards', 10))
        except Exception:
            num_flashcards = 10
            
        if not extracted_text:
            error_message = 'No extracted text provided.'
        else:
            try:
                if not flashcard_generator:
                    error_message = 'Flashcard generator not properly initialized.'
                else:
                    # Generate flashcards based on type
                    if flashcard_type == 'concepts':
                        result = flashcard_generator.generate_concept_flashcards(
                            text=extracted_text, 
                            num_flashcards=num_flashcards
                        )
                    elif flashcard_type == 'processes':
                        result = flashcard_generator.generate_process_flashcards(
                            text=extracted_text, 
                            num_flashcards=num_flashcards
                        )
                    else:  # general
                        result = flashcard_generator.generate_flashcards(
                            text=extracted_text, 
                            num_flashcards=num_flashcards
                        )
                    
                    if 'error' in result:
                        error_message = result['error']
                    else:
                        flashcard_results = result.get('flashcards', [])
                        
            except Exception as e:
                error_message = f'Error generating flashcards: {str(e)}'
                
    return render(request, 'slides_analyzer/flashcards.html', {
        'user_authenticated': request.user.is_authenticated,
        'flashcard_results': flashcard_results,
        'error_message': error_message,
        'flashcard_type': flashcard_type
    })

@login_required
def display_questions(request):
    # Get questions from session or context
    questions = request.session.get('questions', {})
    return render(request, 'slides_analyzer/display_questions.html', {'questions': questions, 'user_authenticated': request.user.is_authenticated})

@login_required
def display_text(request):
    # Get text from session or context
    text = request.session.get('extracted_text', '')
    return render(request, 'slides_analyzer/display_text.html', {'text': text, 'user_authenticated': request.user.is_authenticated})

def error(request, message="An error occurred"):
    return render(request, 'slides_analyzer/error.html', {'message': message, 'user_authenticated': request.user.is_authenticated})

def about(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        subject = request.POST.get('subject', '').strip()
        message = request.POST.get('message', '').strip()
        
        # Validate all fields
        if not all([name, email, subject, message]):
            messages.error(request, "All fields are required. Please fill in all the information.")
            return redirect('about')
        
        try:
            # Validate email format
            validate_email(email)
            
            # Create contact submission
            contact = Contact.objects.create(
                name=name,
                email=email,
                subject=subject,
                message=message
            )
            
            messages.success(request, "Thank you for your message! We'll get back to you soon.")
            
            # Send email notification to admin
            try:
                admin_message = f"""
New contact form submission from a student:

Name: {name}
Email: {email}
Subject: {subject}
Message: {message}

Submitted on: {contact.created_at.strftime("%Y-%m-%d %H:%M:%S")}

You can view and manage all submissions in the Django admin panel.
"""
                send_mail(
                    subject=f'New Contact Form Submission: {subject}',
                    message=admin_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[settings.ADMIN_EMAIL] if hasattr(settings, 'ADMIN_EMAIL') else ['admin@lamla.ai'],
                    fail_silently=True,
                )
            except Exception as e:
                logger.warning(f"Failed to send contact notification email: {e}")
                
        except DjangoValidationError:
            messages.error(request, "Please enter a valid email address.")
        except Exception as e:
            logger.error(f"Error processing contact form: {e}")
            messages.error(request, "Sorry, there was an error sending your message. Please try again.")
        
        return redirect('about')
    
    return render(request, 'slides_analyzer/about.html')

@csrf_exempt
@login_required
def ajax_extract_text(request):
    if request.method == 'POST' and request.FILES.get('slide_file'):
        uploaded_file = request.FILES['slide_file']
        try:
            validate_file_upload(uploaded_file)
            extracted_text = extract_text_from_file(uploaded_file)
            return JsonResponse({'text': extracted_text})
        except ValidationError as e:
            return JsonResponse({'error': str(e)}, status=400)
        except Exception as e:
            return JsonResponse({'error': f'File upload failed: {str(e)}'}, status=400)
    return JsonResponse({'error': 'No file uploaded'}, status=400)

class CustomLoginView(AllauthLoginView):
    def dispatch(self, request, *args, **kwargs):
        # Always show the login form, even if authenticated
        return super(AllauthLoginView, self).dispatch(request, *args, **kwargs)

def custom_logout(request):
    auth_logout(request)
    return redirect('account_login')

@csrf_exempt
def quiz_results(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            user_answers = data.get('user_answers', {})
            request.session['user_answers'] = user_answers
            return JsonResponse({'status': 'ok'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    questions = request.session.get('questions', {})
    user_answers = request.session.get('user_answers', {})
    if not questions or (not questions.get('mcq_questions') and not questions.get('short_questions')):
        # Instead of redirecting to custom_quiz (which requires login), show a message
        return render(request, 'slides_analyzer/quiz_results.html', {
            'score': 0,
            'total': 0,
            'wrong': 0,
            'mcq_questions': [],
            'short_questions': [],
            'user_answers': {},
            'user_authenticated': request.user.is_authenticated,
            'no_quiz_message': 'No quiz data found. Please take a quiz first.'
        })
    
    # Calculate score for MCQ questions
    score = 0
    total = 0
    mcq_questions = questions.get('mcq_questions', [])
    for idx, q in enumerate(mcq_questions):
        total += 1
        user_ans = user_answers.get(str(idx))
        correct_ans = q.get('answer', '').upper()
        if user_ans and user_ans.upper() == correct_ans:
            score += 1
    
    # Short answer questions are for review only (not auto-graded)
    short_questions = questions.get('short_questions', [])
    
    # Calculate number of incorrect answers
    wrong = total - score if total is not None and score is not None else 0

    # Calculate percentages for bar chart, avoid division by zero
    if total:
        score_percent = (score / total) * 100
        wrong_percent = (wrong / total) * 100
    else:
        score_percent = 0
        wrong_percent = 0

    context = {
        'score': score,
        'total': total,
        'wrong': wrong,
        'score_percent': score_percent,
        'wrong_percent': wrong_percent,
        'mcq_questions': mcq_questions,
        'short_questions': short_questions,
        'user_answers': user_answers,
        'user_authenticated': request.user.is_authenticated,
    }
    return render(request, 'slides_analyzer/quiz_results.html', context)

@csrf_exempt
def submit_feedback(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user = request.user if request.user.is_authenticated else None
            feedback = Feedback.objects.create(
                user=user,
                rating=data.get('rating', 0),
                feedback_text=data.get('feedback', ''),
                feedback_type=data.get('feedback_type', 'general'),
                page_url=data.get('page_url', ''),
            )
            return JsonResponse({'status': 'success', 'message': 'Feedback submitted successfully'})
        except Exception as e:
            logger.error(f"Error submitting feedback: {e}")
            return JsonResponse({'status': 'error', 'message': 'Failed to submit feedback'}, status=500)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

# Legal page views
def privacy_policy(request):
    """Render the Privacy Policy page"""
    return render(request, 'slides_analyzer/privacy_policy.html')

def terms_of_service(request):
    """Render the Terms of Service page"""
    return render(request, 'slides_analyzer/terms_of_service.html')

def cookie_policy(request):
    """Render the Cookie Policy page"""
    return render(request, 'slides_analyzer/cookie_policy.html')

@login_required
def dashboard(request):
    """User dashboard showing statistics and recent activity"""
    user = request.user
    
    # Get user statistics
    from django.db.models import Count, Q
    from datetime import datetime, timedelta
    
    # Recent activity (last 30 days)
    thirty_days_ago = timezone.now() - timedelta(days=30)
    
    # Get user's feedback submissions
    user_feedback = Feedback.objects.filter(user=user).order_by('-created_at')[:5]
    
    # Get user's contact submissions
    user_contacts = Contact.objects.filter(email=user.email).order_by('-created_at')[:5]
    
    # Count total feedback submissions
    total_feedback = Feedback.objects.filter(user=user).count()
    
    # Count total contact submissions
    total_contacts = Contact.objects.filter(email=user.email).count()
    
    # Get recent questions from session (if any)
    recent_questions = request.session.get('recent_questions', [])
    
    # Get user's subscription status
    subscription = Subscription.objects.filter(email=user.email, is_active=True).first()
    
    # Calculate user engagement metrics
    recent_feedback_count = Feedback.objects.filter(
        user=user, 
        created_at__gte=thirty_days_ago
    ).count()
    
    recent_contacts_count = Contact.objects.filter(
        email=user.email, 
        created_at__gte=thirty_days_ago
    ).count()
    
    # Get user's join date
    days_since_joined = (timezone.now() - user.date_joined).days
    
    # Get or create user profile
    profile, created = UserProfile.objects.get_or_create(user=user)
    
    context = {
        'user': user,
        'profile': profile,
        'user_feedback': user_feedback,
        'user_contacts': user_contacts,
        'total_feedback': total_feedback,
        'total_contacts': total_contacts,
        'recent_questions': recent_questions[:5],  # Show last 5 questions
        'subscription': subscription,
        'thirty_days_ago': thirty_days_ago,
        'recent_feedback_count': recent_feedback_count,
        'recent_contacts_count': recent_contacts_count,
        'days_since_joined': days_since_joined,
    }
    
    return render(request, 'slides_analyzer/dashboard.html', context)

@csrf_exempt
@login_required
def subscribe_newsletter(request):
    """Handle newsletter subscription via AJAX"""
    if request.method == 'POST':
        try:
            email = request.user.email
            if not email:
                return JsonResponse({
                    'success': False,
                    'message': 'Email address not found in your profile'
                }, status=400)
            
            # Check if already subscribed
            existing_subscription = Subscription.objects.filter(email=email).first()
            if existing_subscription:
                if existing_subscription.is_active:
                    return JsonResponse({
                        'success': False,
                        'message': 'You are already subscribed to our newsletter'
                    }, status=400)
                else:
                    # Reactivate subscription
                    existing_subscription.is_active = True
                    existing_subscription.save()
                    return JsonResponse({
                        'success': True,
                        'message': 'Newsletter subscription reactivated successfully!'
                    })
            
            # Create new subscription
            subscription = Subscription.objects.create(
                email=email,
                is_active=True
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Successfully subscribed to our newsletter!'
            })
            
        except Exception as e:
            logger.error(f"Newsletter subscription error: {e}")
            return JsonResponse({
                'success': False,
                'message': 'An error occurred while subscribing. Please try again.'
            }, status=500)
    
    return JsonResponse({
        'success': False,
        'message': 'Invalid request method'
    }, status=405)

@login_required
def user_profile(request):
    """User profile view for viewing and editing profile information"""
    user = request.user
    
    if request.method == 'POST':
        # Handle profile updates
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        bio = request.POST.get('bio', '').strip()
        
        # Basic validation
        if not email:
            messages.error(request, 'Email is required.')
        elif not first_name:
            messages.error(request, 'First name is required.')
        else:
            try:
                # Update user information
                user.first_name = first_name
                user.last_name = last_name
                user.email = email
                user.save()
                
                # Update or create user profile
                profile, created = UserProfile.objects.get_or_create(user=user)
                profile.bio = bio
                
                # Handle profile picture upload
                if 'profile_picture' in request.FILES:
                    profile_picture = request.FILES['profile_picture']
                    
                    # Validate file size (5MB limit)
                    if profile_picture.size > 5 * 1024 * 1024:
                        messages.error(request, 'Profile picture must be under 5MB.')
                    else:
                        # Validate file type
                        allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif']
                        if profile_picture.content_type in allowed_types:
                            # Delete old profile picture if it exists
                            if profile.profile_picture:
                                profile.profile_picture.delete(save=False)
                            
                            profile.profile_picture = profile_picture
                            messages.success(request, 'Profile picture updated successfully!')
                        else:
                            messages.error(request, 'Please upload a valid image file (JPG, PNG, or GIF).')
                
                profile.save()
                messages.success(request, 'Profile updated successfully!')
                return redirect('user_profile')
                
            except Exception as e:
                logger.error(f"Profile update error: {e}")
                messages.error(request, 'An error occurred while updating your profile.')
    
    # Get user statistics for profile
    total_feedback = Feedback.objects.filter(user=user).count()
    total_contacts = Contact.objects.filter(email=user.email).count()
    subscription = Subscription.objects.filter(email=user.email, is_active=True).first()
    
    # Get or create user profile
    profile, created = UserProfile.objects.get_or_create(user=user)
    
    context = {
        'user': user,
        'profile': profile,
        'total_feedback': total_feedback,
        'total_contacts': total_contacts,
        'subscription': subscription,
    }
    
    return render(request, 'slides_analyzer/user_profile.html', context)

@login_required
def feedback_analytics(request):
    """Admin view to see star ratings and feedback analytics"""
    # Check if user is staff/admin
    if not request.user.is_staff:
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('home')
    
    # Get all feedback with ratings
    feedback_with_ratings = Feedback.objects.filter(rating__isnull=False).order_by('-created_at')
    
    # Calculate statistics
    total_ratings = feedback_with_ratings.count()
    avg_rating = feedback_with_ratings.aggregate(avg=models.Avg('rating'))['avg'] or 0
    
    # Rating distribution
    rating_distribution = {}
    for i in range(1, 6):
        count = feedback_with_ratings.filter(rating=i).count()
        percentage = (count / total_ratings * 100) if total_ratings > 0 else 0
        rating_distribution[i] = {'count': count, 'percentage': round(percentage, 1)}
    
    # Recent feedback
    recent_feedback = feedback_with_ratings[:10]
    
    # Page analytics
    page_analytics = feedback_with_ratings.values('page_url').annotate(
        count=models.Count('id'),
        avg_rating=models.Avg('rating')
    ).order_by('-count')
    
    context = {
        'total_ratings': total_ratings,
        'avg_rating': round(avg_rating, 1),
        'rating_distribution': rating_distribution,
        'recent_feedback': recent_feedback,
        'page_analytics': page_analytics,
    }
    
    return render(request, 'slides_analyzer/feedback_analytics.html', context)

DATABASES = {
    'default': dj_database_url.config(default='sqlite:///db.sqlite3')
}
