# Lamla-AI

**Lamla** stands for **Learn And Master Like an Ace** — your smart exam preparation assistant. Lamla helps you study with intention, not panic. It's not a cramming tool or a generic GPT wrapper, but a purpose-built platform to help you **Study Smarter. Perform Better.**

Lamla-AI empowers students to upload their study materials, generate AI-powered quizzes, receive instant feedback, and track their performance with actionable insights. Built for high school and university students (starting in Africa, but for the world), Lamla is your intelligent study companion for mastering any subject.

---

## 🚀 Core Features
- **Upload Study Materials** (PDF, text)
- **AI-Powered Quiz Generation** (personalized, with explanations)
- **Instant Feedback** (actionable, growth-focused)
- **Performance Tracking** (color-coded bar charts, robust analytics)
- **Subject & Topic Selection** (focus your study)
- **User Authentication** (Sign up, Login, Logout)
- **Profile Management**
  - **Edit Name, Email, and Bio**
  - **Profile Picture Upload** (JPG/PNG/GIF, up to 5MB, with instant preview and persistence)
  - **Unified Modern Card UI** (profile and dashboard cards match)
- **Modern, Responsive UI** (mobile-friendly, branded)

> **Lamla-AI is not a shortcut or cheat tool — it's a smart compass for students who want to prepare better, not later.**

---

## 🛠️ Tech Stack
- **Backend:** Django 5, Django REST Framework
- **Frontend:** Django Templates, Custom CSS
- **AI Integration:** Google Gemini, OpenAI, Hugging Face (Mistral)
- **Auth:** Django Allauth
- **Database:** SQLite (default, easy to switch)

---

## ⚡ Quickstart

### 1. Clone the Repo
```sh
git clone https://github.com/your-username/your-repo.git
cd LAMLA-AI
```

### 2. Create & Activate a Virtual Environment
```sh
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
```sh
pip install -r requirements.txt
```

### 4. Set Up Environment Variables
**Option A: Use the setup script (Recommended)**
```sh
python setup_env.py
```
> **Note:** The setup script only creates a template `.env` file. You must manually add your real API keys and secrets after running it.

**Option B: Manual setup**
Create a `.env` file in the project root with your API keys:
```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# API Keys (Get your keys from the links below)
GEMINI_API_KEY=your_gemini_key
AZURE_OPENAI_API_KEY=your_azure_openai_key
AZURE_OPENAI_ENDPOINT=your_azure_openai_endpoint
HUGGING_FACE_API_TOKEN=your_huggingface_token

# Optional: Gemini Model
GEMINI_MODEL=models/gemini-1.5-pro-latest

# Email Configuration for Form Notifications
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@lamla.ai
ADMIN_EMAIL=admin@lamla.ai
```

**Get your API keys:**
- **Gemini**: https://makersuite.google.com/app/apikey
- **Azure OpenAI**: https://portal.azure.com/#view/Microsoft_Azure_ProjectOxford/CognitiveServicesHub/~/OpenAI
- **Hugging Face**: https://huggingface.co/settings/tokens

> **Security Note:**
> - Your `.env` file contains sensitive secrets and **must never be committed to version control**. It is already included in `.gitignore`.
> - For production, set environment variables securely in your deployment environment instead of using a `.env` file.
> - Never log, print, or expose your API keys in code or error messages.

> **Note**: At least one API key is required for question generation. The app will try APIs in order: Azure OpenAI → Gemini → Hugging Face → Local GPT-2 fallback.

### 5. Test API Configuration
```sh
python manage.py check_apis
```

### 6. Run Migrations
```sh
python manage.py migrate
```

### 7. Create a Superuser (Optional)
```sh
python manage.py createsuperuser
```

### 8. Run the Development Server
```sh
python manage.py runserver
```

Visit [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in your browser.

### 9. Serve Media Files in Development
To display uploaded profile pictures and other media, add this to your `edtech_project/urls.py`:
```python
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # ... your other url patterns ...
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

---

## 📁 Project Structure
```
LAMLA-AI/
├── edtech_project/         # Django project settings
├── slides_analyzer/        # Main app: views, models, templates, static
├── templates/              # Global templates (auth, base)
├── static/                 # (Optional) Global static files
├── media/                  # User-uploaded files (profile pictures, etc.)
├── db.sqlite3              # SQLite database (default)
├── requirements.txt        # Python dependencies
├── README.md               # This file
└── ...
```

---

## 👤 Profile Management
- **Edit your name, email, and bio** from the profile page.
- **Upload a profile picture** (JPG, PNG, or GIF, up to 5MB). Click the camera icon on your profile image, select a file, and save changes. The image will instantly preview and persist across sessions.
- **Unified look:** The profile card now matches the dashboard's main card (black background, white text).
- **Bio field:** Share a bit about yourself for a more personalized experience.

---

## 🌍 Who is Lamla-AI for?
- **High school and university students** (especially in Africa, but globally relevant)
- Learners who want to master subjects, not just cram
- Anyone seeking guided, purposeful, and data-driven study

---

## 🤝 Contributing
Pull requests are welcome! For major changes, please open an issue first to discuss what you'd like to change.

---

## 📄 License
[MIT](LICENSE) 

## 🔧 Troubleshooting

### API Issues
If you encounter API errors:

1. **Check your API keys**: Run `python manage.py check_apis`
2. **Verify quotas**: Ensure your API accounts have sufficient credits
3. **Test individual APIs**: Use `python test_hf.py` for Hugging Face testing
4. **Fallback mode**: The app will use local GPT-2 if all APIs fail

### Common Errors
- **"No API keys configured"**: Add at least one API key to your `.env` file
- **"Quota exceeded"**: Check your API account billing/quotas
- **"Model not found"**: The app automatically tries alternative models
- **"Device set to use cpu"**: Normal for systems without GPU

### Performance Tips
- Use Gemini API for best performance (free tier available)
- Local GPT-2 works offline but requires more memory
- Cache questions are stored to reduce API calls 