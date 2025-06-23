from django.db import models
import hashlib

# Create your models here.

class Quiz(models.Model):
    title = models.CharField(max_length=255)
    # Add other fields as needed, e.g., description, duration

    def __str__(self):
        return self.title

class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    # A simple way to store options, you might need a separate model for more complex options
    # Example: options = models.JSONField(default=list) # Requires Django 3.1+
    # For simplicity, let's use text fields for options and correct answer
    option_a = models.CharField(max_length=255, blank=True, null=True)
    option_b = models.CharField(max_length=255, blank=True, null=True)
    option_c = models.CharField(max_length=255, blank=True, null=True)
    option_d = models.CharField(max_length=255, blank=True, null=True)
    correct_answer = models.CharField(max_length=255) # Stores the text of the correct option
    question_type = models.CharField(max_length=20, choices=[('MCQ', 'Multiple Choice'), ('SHORT', 'Short Answer')])
    difficulty = models.CharField(max_length=10, choices=[('EASY', 'Easy'), ('MEDIUM', 'Medium'), ('HARD', 'Hard')])
    content_hash = models.CharField(max_length=64, unique=True)  # SHA-256 hash of the content
    created_at = models.DateTimeField(auto_now_add=True)
    times_used = models.IntegerField(default=0)

    # Add other fields as needed, e.g., difficulty, explanation

    def __str__(self):
        return self.text

    @classmethod
    def generate_content_hash(cls, text):
        """Generate a hash of the content for caching"""
        return hashlib.sha256(text.encode()).hexdigest()

class QuestionCache(models.Model):
    """Cache for storing generated questions based on content hash"""
    content_hash = models.CharField(max_length=64, unique=True)
    questions = models.JSONField()  # Store the generated questions
    created_at = models.DateTimeField(auto_now_add=True)
    last_used = models.DateTimeField(auto_now=True)
    times_used = models.IntegerField(default=0)

    def __str__(self):
        return f"Cache for {self.content_hash[:8]}..."
