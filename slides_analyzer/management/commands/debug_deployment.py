from django.core.management.base import BaseCommand
from django.conf import settings
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.test import RequestFactory
from slides_analyzer.models import UserProfile, QuizSession
from slides_analyzer.views import quiz, custom_quiz
import logging
import os
import hashlib

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Debug deployment issues and check system status'

    def add_arguments(self, parser):
        parser.add_argument(
            '--check-api',
            action='store_true',
            help='Check API configurations',
        )
        parser.add_argument(
            '--check-database',
            action='store_true',
            help='Check database connectivity and data',
        )
        parser.add_argument(
            '--check-settings',
            action='store_true',
            help='Check Django settings',
        )
        parser.add_argument(
            '--check-static',
            action='store_true',
            help='Check static files and templates',
        )
        parser.add_argument(
            '--check-ui',
            action='store_true',
            help='Check UI rendering and template differences',
        )

    def handle(self, *args, **options):
        self.stdout.write("🔍 DEPLOYMENT DEBUGGING TOOL")
        self.stdout.write("=" * 50)
        
        # Check settings
        if options['check_settings'] or not any([options['check_api'], options['check_database'], options['check_static'], options['check_ui']]):
            self.check_settings()
        
        # Check API configurations
        if options['check_api']:
            self.check_api_configurations()
        
        # Check database
        if options['check_database']:
            self.check_database()
        
        # Check static files
        if options['check_static']:
            self.check_static_files()
        
        # Check UI rendering
        if options['check_ui']:
            self.check_ui_rendering()

    def check_settings(self):
        self.stdout.write("\n📋 SETTINGS CHECK:")
        
        # Debug mode
        debug_status = "ENABLED" if settings.DEBUG else "DISABLED"
        self.stdout.write(f"   Debug Mode: {debug_status}")
        
        # Database
        db_engine = settings.DATABASES['default']['ENGINE']
        self.stdout.write(f"   Database Engine: {db_engine}")
        
        # Static files
        static_url = getattr(settings, 'STATIC_URL', 'Not set')
        self.stdout.write(f"   Static URL: {static_url}")
        
        # Static root
        static_root = getattr(settings, 'STATIC_ROOT', 'Not set')
        self.stdout.write(f"   Static Root: {static_root}")
        
        # Static files dirs
        static_dirs = getattr(settings, 'STATICFILES_DIRS', [])
        self.stdout.write(f"   Static Dirs: {static_dirs}")
        
        # Allowed hosts
        allowed_hosts = settings.ALLOWED_HOSTS
        self.stdout.write(f"   Allowed Hosts: {allowed_hosts}")
        
        # Secret key
        secret_key = settings.SECRET_KEY
        if secret_key and len(secret_key) > 10:
            self.stdout.write(f"   Secret Key: Set ({len(secret_key)} chars)")
        else:
            self.stdout.write("   Secret Key: Not properly set")
        
        # Environment variables
        self.stdout.write("\n🌍 ENVIRONMENT VARIABLES:")
        env_vars = ['DEBUG', 'DATABASE_URL', 'STATIC_URL', 'CLOUDINARY_URL']
        for var in env_vars:
            value = os.getenv(var)
            if value:
                # Truncate long values for security
                display_value = value[:20] + "..." if len(value) > 20 else value
                self.stdout.write(f"   {var}: {display_value}")
            else:
                self.stdout.write(f"   {var}: Not set")

    def check_api_configurations(self):
        self.stdout.write("\n🔌 API CONFIGURATIONS:")
        
        # Azure OpenAI
        azure_key = getattr(settings, 'AZURE_OPENAI_API_KEY', None)
        azure_endpoint = getattr(settings, 'AZURE_OPENAI_ENDPOINT', None)
        
        if azure_key and azure_endpoint:
            self.stdout.write("   Azure OpenAI: Configured")
            self.stdout.write(f"   Endpoint: {azure_endpoint}")
        else:
            self.stdout.write("   Azure OpenAI: Not configured")
        
        # Gemini
        gemini_key = getattr(settings, 'GEMINI_API_KEY', None)
        if gemini_key:
            self.stdout.write("   Gemini API: Configured")
        else:
            self.stdout.write("   Gemini API: Not configured")
        
        # Hugging Face
        hf_token = getattr(settings, 'HUGGING_FACE_API_TOKEN', None)
        if hf_token:
            self.stdout.write("   Hugging Face: Configured")
        else:
            self.stdout.write("   Hugging Face: Not configured")

    def check_database(self):
        self.stdout.write("\n🗄️ DATABASE CHECK:")
        
        try:
            # Check User model
            user_count = User.objects.count()
            self.stdout.write(f"   Total Users: {user_count}")
            
            # Check UserProfile model
            profile_count = UserProfile.objects.count()
            self.stdout.write(f"   Total Profiles: {profile_count}")
            
            # Check for missing profiles
            users_without_profiles = User.objects.filter(profile__isnull=True).count()
            if users_without_profiles > 0:
                self.stdout.write(f"   Users without profiles: {users_without_profiles} (WARNING)")
            else:
                self.stdout.write("   All users have profiles: OK")
            
            # Check QuizSession
            quiz_count = QuizSession.objects.count()
            self.stdout.write(f"   Total Quiz Sessions: {quiz_count}")
            
            # Check recent activity
            recent_quizzes = QuizSession.objects.order_by('-created_at')[:5]
            if recent_quizzes:
                self.stdout.write("   Recent Quiz Sessions:")
                for quiz in recent_quizzes:
                    self.stdout.write(f"     - {quiz.user.username}: {quiz.subject} ({quiz.created_at})")
            else:
                self.stdout.write("   No recent quiz sessions")
                
        except Exception as e:
            self.stdout.write(f"   Database error: {e}")
            logger.error(f"Database check failed: {e}", exc_info=True)

    def check_static_files(self):
        self.stdout.write("\n📁 STATIC FILES CHECK:")
        
        try:
            # Check main CSS file
            css_path = os.path.join(settings.BASE_DIR, 'static', 'slide_analyzer', 'css', 'main.css')
            if os.path.exists(css_path):
                file_size = os.path.getsize(css_path)
                self.stdout.write(f"   Main CSS: {file_size} bytes")
                
                # Calculate file hash for version tracking
                with open(css_path, 'rb') as f:
                    file_hash = hashlib.md5(f.read()).hexdigest()[:8]
                self.stdout.write(f"   CSS Hash: {file_hash}")
            else:
                self.stdout.write("   Main CSS: Not found")
            
            # Check static files directory structure
            static_dir = os.path.join(settings.BASE_DIR, 'static')
            if os.path.exists(static_dir):
                self.stdout.write(f"   Static directory: {static_dir}")
                for root, dirs, files in os.walk(static_dir):
                    level = root.replace(static_dir, '').count(os.sep)
                    indent = ' ' * 2 * level
                    self.stdout.write(f"{indent}{os.path.basename(root)}/")
                    subindent = ' ' * 2 * (level + 1)
                    for file in files[:5]:  # Limit to first 5 files per directory
                        self.stdout.write(f"{subindent}{file}")
                    if len(files) > 5:
                        self.stdout.write(f"{subindent}... and {len(files) - 5} more files")
            else:
                self.stdout.write("   Static directory: Not found")
                
        except Exception as e:
            self.stdout.write(f"   Static files error: {e}")
            logger.error(f"Static files check failed: {e}", exc_info=True)

    def check_ui_rendering(self):
        self.stdout.write("\n🎨 UI RENDERING CHECK:")
        
        try:
            # Create a test request
            factory = RequestFactory()
            request = factory.get('/')
            
            # Test base template rendering
            try:
                base_content = render_to_string('base.html', {})
                self.stdout.write("   Base template: Renders successfully")
                
                # Check for specific UI elements
                if 'Ask AI Assistant' in base_content:
                    self.stdout.write("   UI Element: 'Ask AI Assistant' found")
                elif 'Ask AI' in base_content:
                    self.stdout.write("   UI Element: 'Ask AI' found")
                else:
                    self.stdout.write("   UI Element: Chatbot toggle text not found")
                
                # Check for CSS classes
                if 'chatbot-container' in base_content:
                    self.stdout.write("   CSS Class: chatbot-container found")
                if 'navbar' in base_content:
                    self.stdout.write("   CSS Class: navbar found")
                if 'sidebar' in base_content:
                    self.stdout.write("   CSS Class: sidebar found")
                    
            except Exception as e:
                self.stdout.write(f"   Base template error: {e}")
            
            # Test quiz template rendering
            try:
                # Create a mock quiz session
                quiz_data = {
                    'mcq_questions': [
                        {
                            'question': 'Test MCQ Question',
                            'options': ['A', 'B', 'C', 'D'],
                            'correct_answer': 'A'
                        }
                    ],
                    'short_questions': [
                        {
                            'question': 'Test Short Question',
                            'answer': 'Test Answer'
                        }
                    ]
                }
                
                quiz_context = {
                    'questions': quiz_data,
                    'quiz_time': 10
                }
                
                quiz_content = render_to_string('slides_analyzer/quiz.html', quiz_context)
                self.stdout.write("   Quiz template: Renders successfully")
                
                # Check for quiz-specific elements
                if 'Test MCQ Question' in quiz_content:
                    self.stdout.write("   Quiz Element: MCQ question found")
                if 'Test Short Question' in quiz_content:
                    self.stdout.write("   Quiz Element: Short question found")
                    
            except Exception as e:
                self.stdout.write(f"   Quiz template error: {e}")
                
        except Exception as e:
            self.stdout.write(f"   UI rendering error: {e}")
            logger.error(f"UI rendering check failed: {e}", exc_info=True) 