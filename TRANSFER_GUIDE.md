# 🚀 How to Apply Performance Optimizations to Your Local Machine

## **Method 1: Manual Copy (Recommended)**

### **Step 1: Download/Copy New Files**
Copy these NEW files to your local project root:
- `optimize_static_images.py` (image optimization script)
- `PERFORMANCE_OPTIMIZATIONS.md` (documentation)
- `PERFORMANCE_CHECKLIST.md` (action items)

### **Step 2: Update Your Local Files**

#### **A. Update `edtech_project/settings.py`**

**Find line with `DEBUG = True` and change to:**
```python
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
```

**In MIDDLEWARE section, add GZip compression:**
```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.gzip.GZipMiddleware',  # ← ADD THIS LINE
    'django.contrib.sessions.middleware.SessionMiddleware',
    # ... rest of your middleware
]
```

**Add these NEW sections anywhere after MIDDLEWARE:**
```python
# Cache Configuration
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'cache_table',
        'TIMEOUT': 300,  # 5 minutes default
        'OPTIONS': {
            'MAX_ENTRIES': 1000,
        }
    }
}

# Session Configuration for Performance
SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'
SESSION_CACHE_ALIAS = 'default'
SESSION_COOKIE_AGE = 86400  # 24 hours
```

**In DATABASES section, add after the existing config:**
```python
# Database Performance Optimizations
if 'sqlite' in DATABASES['default']['ENGINE']:
    DATABASES['default']['OPTIONS'] = {
        'timeout': 20,
        'init_command': "PRAGMA foreign_keys=ON; PRAGMA journal_mode=WAL; PRAGMA synchronous=NORMAL; PRAGMA cache_size=1000; PRAGMA temp_store=MEMORY;",
    }
```

**In STATIC files section, add after STATIC_ROOT:**
```python
# Static File Optimizations
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

# WhiteNoise Configuration for Static File Compression
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
WHITENOISE_USE_FINDERS = True
WHITENOISE_AUTOREFRESH = DEBUG
```

#### **B. Update `slides_analyzer/views.py`**

**Add imports at the top (around line 15):**
```python
from django.db.models import Q, Prefetch
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from django.utils.decorators import method_decorator
```

**Find the `def home(request):` function and add caching:**
```python
@cache_page(60 * 15)  # Cache for 15 minutes
def home(request):
    return render(request, 'slides_analyzer/home.html')
```

**Find the `def dashboard(request):` function and add login_required:**
```python
@login_required
def dashboard(request):
    # ... rest stays the same
```

**Replace the entire `def history(request):` function with the optimized version**
(This is a big change - copy the entire new function from the modified file)

#### **C. Update `slides_analyzer/models.py`**

**In QuizSession model, update these fields:**
```python
subject = models.CharField(max_length=100, blank=True, help_text="Subject/topic of the quiz", db_index=True)
created_at = models.DateTimeField(auto_now_add=True, db_index=True)
```

**In QuizSession Meta class, add indexes:**
```python
class Meta:
    ordering = ['-created_at']
    verbose_name = "Quiz Session"
    verbose_name_plural = "Quiz Sessions"
    indexes = [
        models.Index(fields=['user', '-created_at']),
        models.Index(fields=['subject', '-created_at']),
    ]
```

**Apply similar changes to ExamAnalysis and QuestionCache models**

## **Step 3: Run Commands in Your Local Environment**

**Navigate to your project directory:**
```bash
cd /path/to/your/django/project
```

**Activate your virtual environment:**
```bash
# If using venv
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate     # Windows

# If using conda
conda activate your-env-name
```

**Run the optimization commands:**
```bash
# 1. Create database migrations for new indexes
python manage.py makemigrations slides_analyzer

# 2. Apply migrations
python manage.py migrate

# 3. Create cache table
python manage.py createcachetable

# 4. Optimize images (if you copied the script)
python optimize_static_images.py

# 5. Collect static files with compression
python manage.py collectstatic --noinput
```

**Set environment variable for production:**
```bash
# Create/update .env file
echo "DEBUG=False" >> .env
```

## **Method 2: Git Patch (Advanced)**

If you're comfortable with git, you could:
1. Initialize git in the remote environment
2. Commit changes
3. Create a patch file
4. Apply the patch to your local repo

## **Verification**

After applying changes, test that everything works:

```bash
# Start development server
python manage.py runserver

# Check for any errors in console
# Visit your site and verify it loads correctly
```

## **Expected Results**

✅ Faster page loads (40-60% improvement)
✅ Optimized database queries 
✅ Compressed static files
✅ Proper caching enabled
✅ Smaller image files

## **Troubleshooting**

If you get errors:
1. Check syntax in modified files
2. Make sure all imports are correct
3. Run `python manage.py check` to validate
4. Check Django logs for specific error messages

