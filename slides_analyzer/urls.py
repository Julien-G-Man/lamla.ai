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
    path('test-flashcard/', views.test_flashcard_generator, name='test_flashcard_generator'),
    path('test-chatbot/', views.test_chatbot, name='test_chatbot'),
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
    path('contact/', views.contact, name='contact'),
    path('user-profile/', views.user_profile, name='user_profile'),
    path('feedback-analytics/', views.feedback_analytics, name='feedback_analytics'),
    
    # Subscriber Dashboard (Admin only)
    path('subscribers/', views.view_subscribers, name='view_subscribers'),
    path('users/', views.view_users, name='view_users'),
    path('subscribers/download/', views.download_subscribers_csv, name='download_subscribers_csv'),
    path('subscribers/data/', views.get_subscribers_data, name='get_subscribers_data'),
    path('subscribers/toggle-status/', views.toggle_subscription_status, name='toggle_subscription_status'),
    path('users/download/', views.download_users_csv, name='download_users_csv'),
    path('users/data/', views.get_users_data, name='get_users_data'),
    path('users/delete/', views.delete_user, name='delete_user'),
    path('users/restore/', views.restore_user, name='restore_user'),
    path('users/toggle-status/', views.toggle_user_status, name='toggle_user_status'),
    path('users/deleted/', views.view_deleted_users, name='view_deleted_users'),
    path('users/deleted/data/', views.get_deleted_users_data, name='get_deleted_users_data'),
    
    # Chatbot URLs
    path('api/chatbot/support-request/', views.chatbot_support_request, name='chatbot_support_request'),
    path('api/chatbot/message/', views.chatbot_message, name='chatbot_message'),
    path('api/chatbot/suggestions/', views.chatbot_suggestions, name='chatbot_suggestions'),
    path('api/chatbot/history/', views.chatbot_history, name='chatbot_history'),
    path('faq/', views.faq, name='faq'),
    path('quiz-download/', views.download_quiz_text, name='download_quiz_text'),
    path('exam-analysis-results/', views.exam_analysis_results, name='exam_analysis_results'),
    path('exam-analysis-results/<int:analysis_id>/', views.exam_analysis_results, name='exam_analysis_results'),
    path('history/', views.history, name='history'),
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