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
from .models import Question, Quiz, Feedback
from .question_generator import QuestionGenerator
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as auth_logout
from django.core.exceptions import ValidationError
import mimetypes
from django.views.decorators.csrf import csrf_exempt
from allauth.account.views import LoginView as AllauthLoginView
import json

# Set up logging
logger = logging.getLogger(__name__)

# Initialize the question generator
try:
    question_generator = QuestionGenerator()
    logger.info("Question Generator initialized successfully")
except Exception as e:
    logger.error(f"Error initializing Question Generator: {e}")
    question_generator = None

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
            
            # Store questions in session for the quiz view
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
    if request.method == 'POST':
        extracted_text = request.POST.get('extractedText', '').strip()
        try:
            num_flashcards = int(request.POST.get('num_flashcards', 10))
        except Exception:
            num_flashcards = 10
        if not extracted_text:
            error_message = 'No extracted text provided.'
        else:
            try:
                # If you have a flashcard generator, use it here. Otherwise, use question_generator for demo.
                # flashcards = flashcard_generator.generate_flashcards(text=extracted_text, num=num_flashcards)
                flashcards = question_generator.generate_questions(
                    text=extracted_text,
                    num_mcq=0,
                    num_short=num_flashcards
                )
                flashcard_results = flashcards.get('short_questions', [])
            except Exception as e:
                error_message = f'Error generating flashcards: {str(e)}'
    return render(request, 'slides_analyzer/flashcards.html', {
        'user_authenticated': request.user.is_authenticated,
        'flashcard_results': flashcard_results,
        'error_message': error_message
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
    
    context = {
        'score': score,
        'total': total,
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
            feedback = Feedback.objects.create(
                rating=data.get('rating', 0),
                feedback_text=data.get('feedback', ''),
                quiz_score=data.get('quiz_score', 0),
                user_email=data.get('email', '')
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
