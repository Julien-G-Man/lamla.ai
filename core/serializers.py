from rest_framework import serializers
from .models import UploadedFile, ExtractedContent, AnalysisResult

class UploadedFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadedFile
        fields = '__all__'

class ExtractedContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExtractedContent
        fields = '__all__'

class AnalysisResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnalysisResult
        fields = '__all__'