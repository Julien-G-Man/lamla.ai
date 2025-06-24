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
from .models import Question, Quiz
from .question_generator import QuestionGenerator
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.core.exceptions import ValidationError
import mimetypes

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

@login_required
def upload_slides(request):
    extracted_text = ""
    if request.method == 'POST' and request.FILES.get('slide_file'):
        uploaded_file = request.FILES['slide_file']
        
        try:
            # Validate file
            validate_file_upload(uploaded_file)
            
            file_name = uploaded_file.name
            fs = FileSystemStorage()
            
            filename = fs.save(uploaded_file.name, uploaded_file)
            file_path = fs.path(filename)
            
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
                
                # Store extracted text in session
                request.session['extracted_text'] = extracted_text
                
            except Exception as e:
                logger.error(f"Error processing file {file_name}: {e}")
                return render(request, 'slides_analyzer/error.html', {
                    'message': f'Error processing file: {str(e)}'
                })
            finally:
                # Clean up temporary file
                try:
                    fs.delete(filename)
                except Exception as e:
                    logger.warning(f"Failed to delete temporary file {filename}: {e}")
            
            return render(request, 'slides_analyzer/display_text.html', {'text': extracted_text})
            
        except ValidationError as e:
            return render(request, 'slides_analyzer/error.html', {'message': str(e)})
        except Exception as e:
            logger.error(f"File upload failed: {e}")
            return render(request, 'slides_analyzer/error.html', {'message': f'File upload failed: {str(e)}'})
    
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
    return render(request, 'slides_analyzer/custom_quiz.html', {'user_authenticated': request.user.is_authenticated})

def home(request):
    return render(request, 'slides_analyzer/home.html', {'user_authenticated': request.user.is_authenticated})

@login_required
def exam_analyzer(request):
    return render(request, 'slides_analyzer/exam_analyzer.html', {'user_authenticated': request.user.is_authenticated})

@login_required
def quiz(request):
    # Get questions from session
    questions = request.session.get('questions', {})
    if not questions or (not questions.get('mcq_questions') and not questions.get('short_questions')):
        return redirect('custom_quiz')
    return render(request, 'slides_analyzer/quiz.html', {'questions': questions, 'user_authenticated': request.user.is_authenticated})

@login_required
def flashcards(request):
    # View for the flashcards page
    return render(request, 'slides_analyzer/flashcards.html', {'user_authenticated': request.user.is_authenticated})

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
