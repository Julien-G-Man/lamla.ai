import openai
from django.conf import settings
import logging
import re
from .models import ChatbotKnowledge

logger = logging.getLogger(__name__)

class ChatbotService:
    def __init__(self):
        self.client = None
        try:
            # Try Azure OpenAI first
            if (hasattr(settings, 'AZURE_OPENAI_API_KEY') and settings.AZURE_OPENAI_API_KEY and 
                hasattr(settings, 'AZURE_OPENAI_ENDPOINT') and settings.AZURE_OPENAI_ENDPOINT):
                
                self.client = openai.AzureOpenAI(
                    api_key=settings.AZURE_OPENAI_API_KEY,
                    api_version="2024-02-15-preview",
                    azure_endpoint=settings.AZURE_OPENAI_ENDPOINT
                )
                logger.info("Chatbot Service initialized with Azure OpenAI")
                
            # Fallback to regular OpenAI
            elif hasattr(settings, 'OPENAI_API_KEY') and settings.OPENAI_API_KEY:
                self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
                logger.info("Chatbot Service initialized with OpenAI")
                
            else:
                logger.warning("No OpenAI API key found in settings")
        except Exception as e:
            logger.error(f"Error initializing Chatbot Service: {e}")

    def get_lamla_knowledge_base(self):
        """Get all active knowledge base entries about Lamla AI"""
        knowledge_entries = ChatbotKnowledge.objects.filter(is_active=True)
        knowledge_text = ""
        
        for entry in knowledge_entries:
            knowledge_text += f"Category: {entry.category}\n"
            knowledge_text += f"Question: {entry.question}\n"
            knowledge_text += f"Answer: {entry.answer}\n"
            knowledge_text += f"Keywords: {entry.keywords}\n\n"
        
        return knowledge_text

    def get_edtech_best_practices(self):
        """Return best practices in educational technology for context"""
        return """
Best Practices in Educational Technology:
1. Student-Centered Learning
    • Adapt to different learning styles (visual, auditory, kinesthetic).
    • Encourage self-paced and personalized learning.
    • Use AI to provide adaptive learning paths.

2. Active Engagement
    • Incorporate interactive elements like quizzes, flashcards, and polls.
    • Use gamification (badges, leaderboards, rewards) to motivate learners.
    • Encourage participation and critical thinking.

3. Feedback and Assessment
    • Provide timely, specific, and actionable feedback.
    • Mix formative (ongoing) and summative (final) assessments.
    • Use AI to generate personalized feedback.

4. Accessibility and Inclusivity
    • Support multiple languages and accessibility features (text-to-speech, captions).
    • Ensure mobile-first and low-bandwidth support.
    • Provide offline or downloadable resources when possible.

5. Data-Driven Insights
    • Track learner progress with dashboards and analytics.
    • Use predictive analytics to identify at-risk learners.
    • Share clear progress reports with learners and educators.

6. Collaboration and Community
    • Enable discussion forums, study groups, or peer-to-peer support.
    • Encourage mentorship and teamwork.
    • Use AI chatbots to answer FAQs and provide 24/7 assistance.

7. Privacy and Ethics
    • Ensure student data is protected and used responsibly.
    • Be transparent about AI limitations and capabilities.
    • Avoid bias and ensure fairness in AI-driven tools.

8. Continuous Improvement
    • Gather user feedback regularly.
    • Iterate features based on student and teacher needs.
    • Stay updated with new EdTech trends.
"""

    def clean_markdown(self, text):
        """Remove markdown symbols and fix indentation for lists."""
        import re
        # Remove bold, italics, headings
        text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
        text = re.sub(r'__(.*?)__', r'\1', text)
        text = re.sub(r'^#+\s*', '', text, flags=re.MULTILINE)
        text = re.sub(r'`([^`]*)`', r'\1', text)
        # Remove extra asterisks and underscores
        text = text.replace('*', '').replace('_', '')
        # Fix numbered list indentation (4 spaces)
        text = re.sub(r'^(\d+)\.\s*', r'    \1. ', text, flags=re.MULTILINE)
        # Fix bullet list indentation (4 spaces)
        text = re.sub(r'^[-•]\s*', '    • ', text, flags=re.MULTILINE)
        # Indent sub-lists (detect lines that start with whitespace and a bullet/number)
        text = re.sub(r'^(\s+)(\d+\.\s+)', lambda m: '    ' * (len(m.group(1)) // 4 + 1) + m.group(2), text, flags=re.MULTILINE)
        text = re.sub(r'^(\s+)[•-]\s+', lambda m: '    ' * (len(m.group(1)) // 4 + 1) + '• ', text, flags=re.MULTILINE)
        # Remove extra spaces at line start
        text = re.sub(r'^\s+', '', text, flags=re.MULTILINE)
        # Remove multiple blank lines
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text.strip()

    def generate_response(self, user_message, conversation_history=None):
        """Generate a response to user message using Azure ChatGPT"""
        try:
            if not self.client:
                return self.clean_markdown(self._get_fallback_response(user_message))

            # Get Lamla AI knowledge base for context
            lamla_knowledge = self.get_lamla_knowledge_base()
            edtech_best_practices = self.get_edtech_best_practices()

            # Create system prompt
            system_prompt = f"""You are Lamla AI Copilot, a friendly and helpful AI assistant for an educational platform. Your name is Lamla AI Copilot and you can answer questions about the platform and general topics.

Context about Lamla AI:
{lamla_knowledge}

Educational Technology Best Practices:
{edtech_best_practices}

Key Information about Lamla AI:
- Lamla AI stands for "Learn And Master Like an Ace"
- It's an AI-powered learning platform for students
- Helps students upload study materials and generate quizzes/flashcards and gives them feedback on their performance
- Designed for high school and university students
- Motto: "Study Smarter. Perform Better."
- Contact: lamlaaiteam@gmail.com
- WhatsApp contact: +233509341251
- The current url address is lamla-ai.onrender.com
- Lamla AI can support multiple languages
- The founder is a computer science student at Kwame Nkrumah University of Scince and Technlogy (KNUST), Ghana
- You were developed in June 2025 in a dorm room
- Your training data and knowledge of the world at large extends till October 2023, but you have all the updated knowledge of Lamla AI platform

IMPORTANT RESPONSE GUIDELINES:
1. Be warm, friendly, and encouraging in your tone
2. Use proper formatting for lists with clear indentation and bullet points
3. Structure your responses with clear sections when appropriate
4. Use emojis sparingly but effectively to make responses more engaging
5. Break down complex information into digestible chunks
6. Always introduce yourself as Lamla AI Copilot when appropriate
7. Be helpful, concise, and well-organized
8. When providing step-by-step instructions, use numbered lists with proper indentation
9. When listing features or options, use bullet points with proper indentation
10. DO NOT use markdown symbols like ** or ## in your responses
11. Use clean, readable formatting without bold or heading symbols
12. Immediately identify the user's language and respond in the same language
13. Follow EdTech Best Practices, but be sincere about your limitations and the features you have

You can also answer general questions and help with various topics. Always maintain a helpful and friendly demeanor."""

            # Prepare conversation history
            messages = [{"role": "system", "content": system_prompt}]
            if conversation_history:
                for msg in conversation_history[-6:]:  # Keep last 6 messages for context
                    role = "user" if msg['message_type'] == 'user' else "assistant"
                    messages.append({"role": role, "content": msg['content']})
            messages.append({"role": "user", "content": user_message})

            # Use the correct Azure deployment name
            model_name = getattr(settings, 'AZURE_OPENAI_DEPLOYMENT_NAME', 'gpt-4o-mini-deployment')
            response = self.client.chat.completions.create(
                model=model_name,
                messages=messages,
                max_tokens=400,
                temperature=0.7
            )
            if not response.choices or not response.choices[0].message.content:
                return self.clean_markdown(self._get_fallback_response(user_message))
            return self.clean_markdown(response.choices[0].message.content.strip())
        except Exception as e:
            logger.error(f"Error generating chatbot response: {e}")
            return self.clean_markdown(self._get_fallback_response(user_message))

    def _get_fallback_response(self, user_message):
        """Provide fallback responses when AI is not available"""
        user_message_lower = user_message.lower()
        
        # Simple keyword-based responses with better formatting
        if any(word in user_message_lower for word in ['hello', 'hi', 'hey']):
            return """Hello there! 👋 I'm Lamla AI Copilot, your friendly AI assistant. 

I'm here to help you with:
• Questions about our learning platform
• General topics and inquiries
• Study tips and guidance
• Technical support

What would you like to know today?"""
        
        elif any(word in user_message_lower for word in ['what', 'how', 'help']):
            return """Hi! I'm Lamla AI Copilot, and I'm here to help! 😊

I can assist you with:
• Platform navigation and features
• Quiz and flashcard creation
• Study material uploads
• General questions and topics
• Technical support

What would you like to learn about?"""
        
        elif any(word in user_message_lower for word in ['feature', 'quiz', 'flashcard']):
            return """Great question! Lamla AI offers several amazing features to help you study smarter:

📚 Core Features:
    • AI-powered quiz generation from your study materials
    • Interactive flashcard creation
    • Performance tracking and analytics
    • Personalized study insights
    • Multiple file format support (PDF, PPTX, DOCX)
    • Multilingual support

🎯 Study Tools:
    • Custom Quiz creator
    • Exam Analyzer
    • Progress dashboard
    • Feedback system

Would you like me to explain any specific feature in detail?"""
        
        elif any(word in user_message_lower for word in ['contact', 'support', 'email']):
            return """Need help? I'm here for you! 💪

Contact Information:
    • Email: lamlaaiteam@gmail.com 
    • WhatsApp: +233509341251
    • Our support team is always happy to help
    • Response time: Usually within 24 hours

What we can help with:
    • Technical issues
    • Account questions
    • Feature explanations
    • General inquiries

Feel free to reach out anytime!"""
        
        elif any(word in user_message_lower for word in ['thank', 'thanks']):
            return """You're very welcome! 😊 I'm so glad I could help you today.

If you have any more questions about:
• Our platform features
• Study tips
• Technical support
• Or anything else

Just ask - I'm here to help!"""
        
        else:
            return """Thanks for your message! 👋 I'm Lamla AI Copilot, your friendly AI assistant.

I'm here to help with:
• Platform navigation and features
• Study tools and resources
• General questions and topics
• Technical support

What would you like to know about today?"""

    def get_suggested_questions(self):
        """Get suggested questions for users to ask"""
        return [
            "How do I navigate the platform?",
            "How do I use Custom Quiz?",
            "How do I create flashcards?",
            "What is the Exam Analyzer?",
            "How do I upload study materials?",
            "How do I take quizzes and see results?",
            "What can I see on my Dashboard?",
            "How do I manage my profile?",
            "How does the feedback system work?",
            "How can I get help and support?"
        ]

# Create a global instance of the chatbot service
chatbot_service = ChatbotService() 