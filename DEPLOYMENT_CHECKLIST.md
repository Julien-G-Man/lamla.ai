
# DEPLOYMENT CHECKLIST

## Before Deployment:
1. [x] Run: python manage.py collectstatic --noinput --clear
2. [x] Run: python manage.py migrate
3. [x] Set environment variables:
   - DEBUG=False
   - DATABASE_URL (if using external database)
   - All API keys (Azure OpenAI, Gemini, Hugging Face)

## After Deployment:
1. [x] Clear browser cache
2. [x] Clear CDN cache (if using CDN)
3. [x] Restart the application server
4. [x] Test the quiz functionality
5. [x] Check UI elements match local environment

## Common Issues to Check:
1. Static file caching - Clear browser cache
2. Template differences - Ensure all changes are deployed
3. Database migrations - Run migrations on production
4. Environment variables - Verify all are set correctly

## Files to Monitor:
- templates/base.html (for UI text changes)
- static/slide_analyzer/css/main.css (for styling changes)
- edtech_project/settings.py (for configuration changes)
