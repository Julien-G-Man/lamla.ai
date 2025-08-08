from django.core.management.base import BaseCommand
from django.conf import settings
from django.contrib.auth.models import User
from slides_analyzer.models import UserProfile, QuizSession
import logging

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

    def handle(self, *args, **options):
        self.stdout.write("🔍 DEPLOYMENT DEBUGGING TOOL")
        self.stdout.write("=" * 50)
        
        # Check settings
        if options['check_settings'] or not any([options['check_api'], options['check_database']]):
            self.check_settings()
        
        # Check API configurations
        if options['check_api']:
            self.check_api_configurations()
        
        # Check database
        if options['check_database']:
            self.check_database()

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
        
        # Allowed hosts
        allowed_hosts = settings.ALLOWED_HOSTS
        self.stdout.write(f"   Allowed Hosts: {allowed_hosts}")
        
        # Secret key
        secret_key = settings.SECRET_KEY
        if secret_key and len(secret_key) > 10:
            self.stdout.write(f"   Secret Key: Set ({len(secret_key)} chars)")
        else:
            self.stdout.write("   Secret Key: Not properly set")

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