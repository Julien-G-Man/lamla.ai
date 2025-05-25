from django.contrib import admin
from .models import UploadedFile, ExtractedContent, AnalysisResult

admin.site.register(UploadedFile)
admin.site.register(ExtractedContent)
admin.site.register(AnalysisResult)