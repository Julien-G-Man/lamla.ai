# LAMLA-AI

**LAMLA-AI** is an AI-powered study assistant for students and educators. Upload your study materials (PDF, PPTX), generate quizzes and flashcards, and practice with AI-generated questions—all in a modern, user-friendly web app.

---

## 🚀 Features
- **User Authentication** (Sign up, Login, Logout)
- **Upload Study Materials** (PDF, PPTX)
- **AI-Powered Quiz & Flashcard Generation**
- **Custom Quiz Creation**
- **Exam Analyzer** (Coming Soon)
- **Responsive, Modern UI**
- **Dark/Light Theme with Yellow/Black/Grey Branding**

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

**Option B: Manual setup**
Create a `.env` file in the project root with your API keys:
```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# API Keys (Get your keys from the links below)
GEMINI_API_KEY=your_gemini_key
OPENAI_API_KEY=your_openai_key
HUGGING_FACE_API_TOKEN=your_huggingface_token

# Optional: Gemini Model
GEMINI_MODEL=models/gemini-1.5-pro-latest
```

**Get your API keys:**
- **Gemini**: https://makersuite.google.com/app/apikey
- **OpenAI**: https://platform.openai.com/api-keys  
- **Hugging Face**: https://huggingface.co/settings/tokens

> **Note**: At least one API key is required for question generation. The app will try APIs in order: Gemini → OpenAI → Hugging Face → Local GPT-2 fallback.

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

---

## 📁 Project Structure
```
LAMLA-AI/
├── edtech_project/         # Django project settings
├── slides_analyzer/        # Main app: views, models, templates, static
├── templates/              # Global templates (auth, base)
├── static/                 # (Optional) Global static files
├── db.sqlite3              # SQLite database (default)
├── requirements.txt        # Python dependencies
├── README.md               # This file
└── ...
```

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