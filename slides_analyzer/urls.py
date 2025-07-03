from django.urls import path, include
from . import views
import requests

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.user_profile, name='user_profile'),
    path('upload/', views.upload_slides, name='upload_slides'),
    path('generate/', views.generate_questions, name='generate_questions'),
    path('custom-quiz/', views.custom_quiz, name='custom_quiz'),
    path('exam-analyzer/', views.exam_analyzer, name='exam_analyzer'),
    path('quiz/', views.quiz, name='quiz'),
    path('quiz-results/', views.quiz_results, name='quiz_results'),
    path('flashcards/', views.flashcards, name='flashcards'),
    path('test-token/', views.test_token, name='test_token'),
    path('about/', views.about, name='about'),
    path('ajax/extract-text/', views.ajax_extract_text, name='ajax_extract_text'),
    path('ajax/submit-feedback/', views.submit_feedback, name='submit_feedback'),
    path('ajax/subscribe-newsletter/', views.subscribe_newsletter, name='subscribe_newsletter'),
    path('accounts/login/', views.CustomLoginView.as_view(), name='account_login'),
    path('custom-logout/', views.custom_logout, name='custom_logout'),
    # Legal pages
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('terms-of-service/', views.terms_of_service, name='terms_of_service'),
    path('cookie-policy/', views.cookie_policy, name='cookie_policy'),
    path('user-profile/', views.user_profile, name='user_profile'),
    path('feedback-analytics/', views.feedback_analytics, name='feedback_analytics'),
] 

def call_ollama(prompt, model='llama3'):
    url = 'http://localhost:11434/api/generate'
    data = {
        'model': model,
        'prompt': prompt,
        'stream': False
    }
    response = requests.post(url, json=data, timeout=120)
    response.raise_for_status()
    return response.json()['response'] 