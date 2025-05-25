from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
from .models import UploadedFile, ExtractedContent, AnalysisResult
from .serializers import UploadedFileSerializer, ExtractedContentSerializer, AnalysisResultSerializer
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
import textract  # pip install textract

class FileUploadView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    
    def post(self, request, format=None):
        file_obj = request.FILES.get('file')
        if not file_obj:
            return Response({'error': 'No file provided.'}, status=status.HTTP_400_BAD_REQUEST)
        user = request.user if request.user.is_authenticated else User.objects.first()  # For demo
        uploaded_file = UploadedFile.objects.create(
            user=user,
            file=file_obj,
            file_type=file_obj.content_type,
            file_name=file_obj.name
        )
        serializer = UploadedFileSerializer(uploaded_file)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class ExtractContentView(APIView):
    def post(self, request, format=None):
        file_id = request.data.get('file_id')
        if not file_id:
            return Response({'error': 'file_id is required.'}, status=400)
        try:
            uploaded_file = UploadedFile.objects.get(id=file_id)
        except UploadedFile.DoesNotExist:
            return Response({'error': 'UploadedFile not found.'}, status=404)
        file_path = uploaded_file.file.path
        try:
            text = textract.process(file_path).decode('utf-8')
        except Exception as e:
            return Response({'error': str(e)}, status=400)
        extracted = ExtractedContent.objects.create(
            uploaded_file=uploaded_file,
            text=text,
            topics=[]
        )
        serializer = ExtractedContentSerializer(extracted)
        return Response(serializer.data)

class AnalyzeContentView(APIView):
    def post(self, request, format=None):
        content_id = request.data.get('content_id')
        if not content_id:
            return Response({'error': 'content_id is required.'}, status=400)
        try:
            content = ExtractedContent.objects.get(id=content_id)
        except ExtractedContent.DoesNotExist:
            return Response({'error': 'ExtractedContent not found.'}, status=404)
        text = content.text
        # Simple topic extraction: most common words
        words = [w for w in text.split() if len(w) > 4]
        freq = {}
        for w in words:
            freq[w] = freq.get(w, 0) + 1
        topic_frequency = sorted(freq.items(), key=lambda x: x[1], reverse=True)[:5]
        likely_topics = [t[0] for t in topic_frequency]
        summary = " ".join(words[:50]) + "..."
        analysis = AnalysisResult.objects.create(
            extracted_content=content,
            topic_frequency=topic_frequency,
            likely_topics=likely_topics,
            summary=summary
        )
        serializer = AnalysisResultSerializer(analysis)
        return Response(serializer.data)

class UserHistoryView(APIView):
    def get(self, request, user_id):
        files = UploadedFile.objects.filter(user_id=user_id)
        serializer = UploadedFileSerializer(files, many=True)
        return Response(serializer.data)

class GenerateQuizView(APIView):
    def post(self, request):
        summary = request.data.get('summary')
        topics = request.data.get('topics', [])
        questions = []
        for topic in topics:
            questions.append(f'What is the significance of "{topic}" in your study material?')
        if summary:
            questions.append(f'Summarize the following in your own words: "{summary[:100]}..."')
        return Response({'questions': questions})