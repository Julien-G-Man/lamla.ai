from django.urls import path
from . import views

urlpatterns = [
    path('upload/', views.upload_slides, name='upload_slides'),
    path('generate/', views.generate_questions, name='generate_questions'),
    path('custom-quiz/', views.custom_quiz, name='custom_quiz'),
    path('exam-analyzer/', views.exam_analyzer, name='exam_analyzer'),
    path('quiz/', views.quiz, name='quiz'),
    path('flashcards/', views.flashcards, name='flashcards'),
    path('test-token/', views.test_token, name='test_token'),
] 