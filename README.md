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
Create a `.env` file in the project root with your API keys:
```
GEMINI_API_KEY=your_gemini_key
OPENAI_API_KEY=your_openai_key
HUGGING_FACE_API_TOKEN=your_huggingface_token
```

### 5. Run Migrations
```sh
python manage.py migrate
```

### 6. Create a Superuser (Optional)
```sh
python manage.py createsuperuser
```

### 7. Run the Development Server
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