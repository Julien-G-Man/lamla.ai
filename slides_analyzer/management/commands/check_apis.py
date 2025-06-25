from django.core.management.base import BaseCommand
from django.conf import settings
import requests
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Check if all configured APIs are working properly'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Checking API configurations...'))
        
        # Check Gemini API
        if hasattr(settings, 'GEMINI_API_KEY') and settings.GEMINI_API_KEY:
            self.stdout.write('✓ Gemini API key is configured')
            try:
                import google.generativeai as genai
                genai.configure(api_key=settings.GEMINI_API_KEY)
                model = genai.GenerativeModel('gemini-1.5-pro')
                response = model.generate_content("Hello")
                self.stdout.write(self.style.SUCCESS('✓ Gemini API is working'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'✗ Gemini API error: {e}'))
        else:
            self.stdout.write(self.style.WARNING('⚠ Gemini API key not configured'))
        
        # Check OpenAI API
        if hasattr(settings, 'OPENAI_API_KEY') and settings.OPENAI_API_KEY:
            self.stdout.write('✓ OpenAI API key is configured')
            try:
                import openai
                client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": "Hello"}],
                    max_tokens=10
                )
                self.stdout.write(self.style.SUCCESS('✓ OpenAI API is working'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'✗ OpenAI API error: {e}'))
        else:
            self.stdout.write(self.style.WARNING('⚠ OpenAI API key not configured'))
        
        # Check Hugging Face API
        if hasattr(settings, 'HUGGING_FACE_API_TOKEN') and settings.HUGGING_FACE_API_TOKEN:
            self.stdout.write('✓ Hugging Face API token is configured')
            try:
                # Test with the new model
                API_URL = "https://api-inference.huggingface.co/models/gpt2"
                headers = {"Authorization": f"Bearer {settings.HUGGING_FACE_API_TOKEN}"}
                response = requests.post(
                    API_URL, 
                    headers=headers, 
                    json={"inputs": "Hello"}, 
                    timeout=30
                )
                response.raise_for_status()
                self.stdout.write(self.style.SUCCESS('✓ Hugging Face API is working'))
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 404:
                    self.stdout.write(self.style.WARNING('⚠ Hugging Face model not found, trying alternative'))
                    try:
                        # Try alternative model
                        API_URL = "https://api-inference.huggingface.co/models/distilgpt2"
                        response = requests.post(
                            API_URL, 
                            headers=headers, 
                            json={"inputs": "Hello"}, 
                            timeout=30
                        )
                        response.raise_for_status()
                        self.stdout.write(self.style.SUCCESS('✓ Hugging Face alternative model is working'))
                    except Exception as e2:
                        self.stdout.write(self.style.ERROR(f'✗ Hugging Face alternative model error: {e2}'))
                else:
                    self.stdout.write(self.style.ERROR(f'✗ Hugging Face API error: {e}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'✗ Hugging Face API error: {e}'))
        else:
            self.stdout.write(self.style.WARNING('⚠ Hugging Face API token not configured'))
        
        self.stdout.write(self.style.SUCCESS('API check completed!')) 