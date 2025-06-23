from django.shortcuts import render, redirect
from django.core.files.storage import FileSystemStorage
from pptx import Presentation
from PyPDF2 import PdfReader
import os
import google.generativeai as genai
from django.conf import settings
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import Question, Quiz
from .question_generator import QuestionGenerator
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
# Import InferenceApi if used
try:
    from huggingface_hub.inference_api import InferenceApi
except ImportError:
    InferenceApi = None

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
        raise ValueError("GEMINI_API_KEY is not set in settings.py")
    genai.configure(api_key=settings.GEMINI_API_KEY)
    logger.info("Gemini API configured successfully")
except Exception as e:
    logger.error(f"Error configuring Gemini API: {e}")

# Configure Hugging Face API
try:
    huggingface_token = getattr(settings, 'HUGGING_FACE_API_TOKEN', None)
    if not huggingface_token:
        raise ValueError("HUGGING_FACE_API_TOKEN is not set in settings.py")
    if InferenceApi:
        inference = InferenceApi(
            repo_id="mistralai/Mistral-7B-Instruct-v0.2",
            token=huggingface_token
        )
        logger.info("Hugging Face API configured successfully")
except Exception as e:
    logger.error(f"Error configuring Hugging Face API: {e}")

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
        file_name = uploaded_file.name
        fs = FileSystemStorage()
        try:
            filename = fs.save(uploaded_file.name, uploaded_file)
            file_path = fs.path(filename)
            if file_name.lower().endswith('.pptx'):
                try:
                    prs = Presentation(file_path)
                    for slide in prs.slides:
                        for shape in slide.shapes:
                            if hasattr(shape, "text_frame") and shape.text_frame:
                                extracted_text += shape.text_frame.text + "\n"
                except Exception as e:
                    fs.delete(filename)
                    return render(request, 'slides_analyzer/error.html', {'message': f'Error processing PPTX: {e}'})
            elif file_name.lower().endswith('.pdf'):
                try:
                    reader = PdfReader(file_path)
                    for page in reader.pages:
                        page_text = page.extract_text()
                        if page_text:
                            extracted_text += page_text + "\n"
                except Exception as e:
                    fs.delete(filename)
                    return render(request, 'slides_analyzer/error.html', {'message': f'Error processing PDF: {e}'})
            else:
                fs.delete(filename)
                return render(request, 'slides_analyzer/error.html', {'message': "Unsupported file type. Please upload a .pptx or .pdf file."})
            fs.delete(filename)
        except Exception as e:
            return render(request, 'slides_analyzer/error.html', {'message': f'File upload failed: {e}'})
        return render(request, 'slides_analyzer/display_text.html', {'text': extracted_text})
    return render(request, 'slides_analyzer/upload.html')

@csrf_exempt
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
        
        # If no text provided, try to get it from the file
        if not text_content and request.FILES.get('slide_file'):
            uploaded_file = request.FILES['slide_file']
            file_name = uploaded_file.name
            
            # Save the file temporarily to process
            fs = FileSystemStorage()
            filename = fs.save(uploaded_file.name, uploaded_file)
            file_path = fs.path(filename)

            extracted_text = ""
            if file_name.lower().endswith('.pptx'):
                try:
                    prs = Presentation(file_path)
                    for slide in prs.slides:
                        for shape in slide.shapes:
                            if hasattr(shape, "text_frame") and shape.text_frame:
                                extracted_text += shape.text_frame.text + "\n"
                except Exception as e:
                    extracted_text = f"Error processing PPTX: {e}"
                    logger.error(f"Error processing PPTX: {e}")
            elif file_name.lower().endswith('.pdf'):
                try:
                    reader = PdfReader(file_path)
                    for page in reader.pages:
                        page_text = page.extract_text()
                        if page_text:
                            extracted_text += page_text + "\n"
                except Exception as e:
                    extracted_text = f"Error processing PDF: {e}"
                    logger.error(f"Error processing PDF: {e}")
            else:
                 extracted_text = "Unsupported file type. Please upload a .pptx or .pdf file."
                 logger.warning(f"Unsupported file type uploaded: {file_name}")

            # Delete the temporary file
            fs.delete(filename)

            text_content = extracted_text # Set text_content to extracted text
        
        if not text_content:
            return JsonResponse({
                'error': 'No text content provided'
            }, status=400)

        # Get parameters from the request
        num_mcq = int(request.POST.get('num_mcq', 3))
        num_short = int(request.POST.get('num_short', 2))
        
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
    questions = request.session.get('questions', [])
    if not questions:
        return redirect('custom_quiz')
    return render(request, 'slides_analyzer/quiz.html', {'questions': questions, 'user_authenticated': request.user.is_authenticated})

@login_required
def flashcards(request):
    # View for the flashcards page
    return render(request, 'slides_analyzer/flashcards.html', {'user_authenticated': request.user.is_authenticated})

@login_required
def display_questions(request):
    # Example: get questions from session or context
    questions = request.session.get('questions', [])
    return render(request, 'slides_analyzer/display_questions.html', {'questions': questions, 'user_authenticated': request.user.is_authenticated})

@login_required
def display_text(request):
    # Example: get text from session or context
    text = request.session.get('text', '')
    return render(request, 'slides_analyzer/display_text.html', {'text': text, 'user_authenticated': request.user.is_authenticated})

def error(request, message="An error occurred"):
    return render(request, 'slides_analyzer/error.html', {'message': message, 'user_authenticated': request.user.is_authenticated})
