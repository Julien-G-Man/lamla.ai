from django.db import models
from django.contrib.auth.models import User

class UploadedFile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(upload_to='uploads/')
    file_type = models.CharField(max_length=20)
    file_name = models.CharField(max_length=255)
    upload_date = models.DateTimeField(auto_now_add=True)

class ExtractedContent(models.Model):
    uploaded_file = models.ForeignKey(UploadedFile, on_delete=models.CASCADE)
    text = models.TextField()
    topics = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)

class AnalysisResult(models.Model):
    extracted_content = models.ForeignKey(ExtractedContent, on_delete=models.CASCADE)
    topic_frequency = models.JSONField(default=list)
    likely_topics = models.JSONField(default=list)
    summary = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)