from django.db import models
import hashlib
from django.contrib.auth.models import User
from django.core.validators import EmailValidator
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.

class UserProfile(models.Model):
    """Extended user profile with additional fields like profile picture"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    profile_picture = models.ImageField(
        upload_to='profile_pictures/',
        null=True,
        blank=True,
        help_text="Upload your profile picture (JPG, PNG, GIF up to 5MB)"
    )
    bio = models.TextField(max_length=500, blank=True, help_text="Tell us about yourself")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False, help_text="Soft-delete flag for user/admin")

    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    @property
    def profile_picture_url(self):
        """Return the profile picture URL or default image"""
        if self.profile_picture:
            return self.profile_picture.url
        return '/static/slide_analyzer/images/profile_default.png'

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create a UserProfile when a User is created"""
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save the UserProfile when a User is saved"""
    if hasattr(instance, 'profile'):
        instance.profile.save()

class QuizSession(models.Model):
    """Model to track quiz sessions and results"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quiz_sessions')
    subject = models.CharField(max_length=100, blank=True, help_text="Subject/topic of the quiz", db_index=True)
    total_questions = models.IntegerField(default=0)
    correct_answers = models.IntegerField(default=0)
    score_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    duration_minutes = models.IntegerField(default=0, help_text="Time taken in minutes")
    questions_data = models.JSONField(default=dict, help_text="Stored quiz questions and answers")
    user_answers = models.JSONField(default=dict, help_text="User's answers")
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Quiz Session"
        verbose_name_plural = "Quiz Sessions"
    
    def __str__(self):
        return f"{self.user.username} - {self.subject} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"
    
    @property
    def score_display(self):
        """Return score as a formatted string"""
        return f"{self.correct_answers}/{self.total_questions} ({self.score_percentage}%)"

class ExamDocument(models.Model):
    """Model to store uploaded exam documents for analysis"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='exam_documents')
    title = models.CharField(max_length=255, help_text="Document title/name")
    subject = models.CharField(max_length=100, help_text="Subject of the exam")
    year = models.IntegerField(help_text="Year of the exam", null=True, blank=True)
    document_file = models.FileField(
        upload_to='exam_documents/',
        help_text="Upload exam document (PDF, DOCX, TXT)"
    )
    extracted_text = models.TextField(blank=True, help_text="Extracted text from document")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-uploaded_at']
        verbose_name = "Exam Document"
        verbose_name_plural = "Exam Documents"
    
    def __str__(self):
        return f"{self.title} - {self.subject} ({self.uploaded_at.strftime('%Y-%m-%d')})"

class ExamAnalysis(models.Model):
    """Model to store exam analysis results"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='exam_analyses')
    subject = models.CharField(max_length=100, help_text="Subject being analyzed", db_index=True)
    documents_analyzed = models.ManyToManyField(ExamDocument, related_name='analyses')
    analysis_data = models.JSONField(default=dict, help_text="Analysis results including trends and predictions")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Exam Analysis"
        verbose_name_plural = "Exam Analyses"
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['subject', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.subject} Analysis ({self.created_at.strftime('%Y-%m-%d')})"

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
    question_content_hash = models.CharField(max_length=64, unique=True, db_index=True)
    question_text = models.TextField(null=True, blank=True)
    answer = models.TextField(null=True, blank=True)
    question_type = models.CharField(max_length=20, null=True, blank=True)
    options = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_used = models.DateTimeField(auto_now=True, db_index=True)
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


class ChatMessage(models.Model):
    """Model to store chatbot conversation messages"""
    MESSAGE_TYPES = [
        ('user', 'User Message'),
        ('bot', 'Bot Response'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session_id = models.CharField(max_length=100, help_text="Session identifier for anonymous users")
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPES)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
        verbose_name = "Chat Message"
        verbose_name_plural = "Chat Messages"
    
    def __str__(self):
        return f"{self.message_type} - {self.content[:50]}..."


class ChatbotKnowledge(models.Model):
    """Model to store knowledge base for the chatbot about Lamla AI"""
    category = models.CharField(max_length=50, help_text="Category of information (e.g., 'features', 'pricing', 'how_to')")
    question = models.CharField(max_length=200, help_text="Common question or topic")
    answer = models.TextField(help_text="Detailed answer about Lamla AI")
    keywords = models.TextField(blank=True, help_text="Comma-separated keywords for matching")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['category', 'question']
        verbose_name = "Chatbot Knowledge"
        verbose_name_plural = "Chatbot Knowledge"
    
    def __str__(self):
        return f"{self.category}: {self.question}"
