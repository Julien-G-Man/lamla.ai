from django.urls import path
from .views import FileUploadView, ExtractContentView, AnalyzeContentView, UserHistoryView

patterns = [
    path('upload/', FileUploadView.as_view()),
    path('extract/', ExtractContentView.as_view()),
    path('analyze/', AnalyzeContentView.as_view()),
    path('history/<int:user_id>', UserHistoryView.as_view()),
]