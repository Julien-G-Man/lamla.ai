from django.db import models
import hashlib
from django.contrib.auth.models import User
from django.core.validators import EmailValidator
from django.utils import timezone

# Create your models here.

class Quiz(models.Model):
    title = models.CharField(max_length=255)
    # Add other fields as needed, e.g., description, duration
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Question(models.Model):
    question_text = models.TextField()
    answer = models.TextField(default='N/A')
    question_type = models.CharField(max_length=20, choices=[
        ('mcq', 'Multiple Choice'),
        ('short', 'Short Answer'),
    ], default='mcq')
    options = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.question_text
    
    @staticmethod
    def generate_content_hash(text: str) -> str:
        """Generate a hash for the content to use for caching"""
        return hashlib.sha256(text.encode('utf-8')).hexdigest()

class QuestionCache(models.Model):
    """Cache for storing generated questions based on content hash"""
    question_content_hash = models.CharField(max_length=64, unique=True)
    question_text = models.TextField(null=True, blank=True)
    answer = models.TextField(null=True, blank=True)
    question_type = models.CharField(max_length=20, null=True, blank=True)
    options = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_used = models.DateTimeField(auto_now=True)
    times_used = models.IntegerField(default=0)

    def __str__(self):
        return f"Cache for {self.question_content_hash[:8]}..."

class Feedback(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    rating = models.IntegerField(choices=[
        (1, '1 Star'),
        (2, '2 Stars'),
        (3, '3 Stars'),
        (4, '4 Stars'),
        (5, '5 Stars'),
    ], null=True, blank=True)
    feedback_text = models.TextField(blank=True)
    feedback_type = models.CharField(max_length=20, choices=[
        ('general', 'General Feedback'),
        ('quiz', 'Quiz Feedback'),
        ('bug', 'Bug Report'),
        ('feature', 'Feature Request'),
    ], default='general')
    page_url = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Feedback from {self.user.username if self.user else 'Anonymous'} - {self.created_at.strftime('%Y-%m-%d')}"

class Subscription(models.Model):
    """Newsletter subscription from students"""
    email = models.EmailField(
        unique=True,
        validators=[EmailValidator()],
        help_text="Student's email address"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True, help_text="Whether subscription is active")
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Newsletter Subscription"
        verbose_name_plural = "Newsletter Subscriptions"
    
    def __str__(self):
        return f"{self.email} ({self.created_at.strftime('%Y-%m-%d')})"

class Contact(models.Model):
    """Contact form submissions from students"""
    SUBJECT_CHOICES = [
        ('general', 'General Inquiry'),
        ('technical', 'Technical Support'),
        ('feature', 'Feature Request'),
        ('bug', 'Bug Report'),
        ('feedback', 'Feedback'),
        ('other', 'Other'),
    ]
    
    name = models.CharField(max_length=100, help_text="Student's full name")
    email = models.EmailField(validators=[EmailValidator()], help_text="Student's email address")
    subject = models.CharField(max_length=200, help_text="Subject of the message")
    message = models.TextField(help_text="Student's message")
    created_at = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False, help_text="Whether the issue has been resolved")
    response_sent = models.BooleanField(default=False, help_text="Whether a response has been sent")
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Contact Form Submission"
        verbose_name_plural = "Contact Form Submissions"
    
    def __str__(self):
        return f"{self.name} - {self.subject} ({self.created_at.strftime('%Y-%m-%d')})"
    
    @property
    def short_message(self):
        """Return first 100 characters of message for admin display"""
        return self.message[:100] + "..." if len(self.message) > 100 else self.message
