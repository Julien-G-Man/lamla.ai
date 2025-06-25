import os
import requests
import json
from typing import Dict, List, Optional
from django.conf import settings
from .models import Question, QuestionCache
import logging

logger = logging.getLogger(__name__)

class QuestionGenerator:
    def __init__(self):
        self.gemini_api_key = getattr(settings, 'GEMINI_API_KEY', None)
        self.gemini_model = getattr(settings, 'GEMINI_MODEL', 'gemini-1.5-pro')
        self.openai_api_key = getattr(settings, 'OPENAI_API_KEY', None)
        self.hf_token = getattr(settings, 'HUGGING_FACE_API_TOKEN', None)
        
        # Prefer Gemini, fallback to OpenAI, then Hugging Face
        if self.gemini_api_key:
            self.primary_api = 'gemini'
        elif self.openai_api_key:
            self.primary_api = 'openai'
        elif self.hf_token:
            self.primary_api = 'huggingface'
        else:
            self.primary_api = None
            logger.warning("No API keys configured for question generation")

    def _create_prompt(self, text: str, num_mcq: int = 3, num_short: int = 2) -> str:
        return f"""Task: Create {num_mcq} multiple-choice questions and {num_short} short-answer questions based on the following text.

Text:
---
{text}
---

Instructions:
1. For multiple-choice questions:
   - Create clear, focused questions
   - Provide 4 options (A, B, C, D)
   - Mark the correct answer
   - Make questions test understanding

2. For short-answer questions:
   - Create questions that need brief but thoughtful answers
   - Include the expected answer

Format your response exactly like this:
MCQ1: [Question]
A) [Option A]
B) [Option B]
C) [Option C]
D) [Option D]
Correct Answer: [Letter]

[Repeat for other MCQs]

Short Answer 1: [Question]
Expected Answer: [Brief answer]

[Repeat for other short answers]"""

    def _call_gemini_api(self, prompt: str) -> str:
        """Call Google Gemini API"""
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.gemini_api_key)
            model = genai.GenerativeModel(self.gemini_model)
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            raise

    def _call_openai_api(self, prompt: str) -> str:
        """Call OpenAI API"""
        try:
            import openai
            client = openai.OpenAI(api_key=self.openai_api_key)
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise

    def _call_huggingface_api(self, prompt: str) -> str:
        """Call Hugging Face API - simplified approach"""
        try:
            # Try a simple text generation model
            API_URL = "https://api-inference.huggingface.co/models/sshleifer/tiny-gpt2"
            headers = {"Authorization": f"Bearer {self.hf_token}"}
            
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": 500,
                    "temperature": 0.7,
                    "return_full_text": False
                }
            }
            
            response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                return result[0].get('generated_text', '')
            elif isinstance(result, dict) and 'generated_text' in result:
                return result['generated_text']
            return str(result)
        except Exception as e:
            logger.error(f"Hugging Face API error: {e}")
            # Don't raise, let it fall through to local fallback
            return ""

    def _call_huggingface_alternative(self, prompt: str) -> str:
        """Try alternative Hugging Face model if primary fails"""
        try:
            # Try another simple model
            API_URL = "https://api-inference.huggingface.co/models/distilgpt2"
            headers = {"Authorization": f"Bearer {self.hf_token}"}
            
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": 500,
                    "temperature": 0.7,
                    "return_full_text": False
                }
            }
            
            response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                return result[0].get('generated_text', '')
            return str(result)
        except Exception as e:
            logger.error(f"Hugging Face alternative API error: {e}")
            return ""

    def _call_local_gpt2(self, prompt: str) -> str:
        """Call local Hugging Face GPT-2 model as a last resort."""
        try:
            from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
            import torch
            
            # Check if CUDA is available, otherwise use CPU
            device = "cuda" if torch.cuda.is_available() else "cpu"
            logger.info(f"Device set to use {device}")
            
            # Load model and tokenizer with proper device handling
            model_name = "gpt2"
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            model = AutoModelForCausalLM.from_pretrained(model_name)
            
            # Move model to device
            model = model.to(device)
            
            # Add padding token if not present
            if tokenizer.pad_token is None:
                tokenizer.pad_token = tokenizer.eos_token
            
            # Create pipeline with proper configuration
            generator = pipeline(
                "text-generation",
                model=model,
                tokenizer=tokenizer,
                device=device,
                torch_dtype=torch.float32 if device == "cpu" else torch.float16
            )
            
            # Generate text with proper parameters
            result = generator(
                prompt, 
                max_length=len(tokenizer.encode(prompt)) + 200,
                num_return_sequences=1,
                temperature=0.7,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id
            )
            
            if result and len(result) > 0:
                return result[0]['generated_text']
            return ""
            
        except Exception as e:
            logger.error(f"Local GPT-2 error: {e}")
            return ""

    def _generate_template_questions(self, text: str, num_mcq: int, num_short: int) -> Dict[str, List[Dict]]:
        """Generate questions using templates when all APIs fail"""
        logger.info("Generating template-based questions")
        
        # Extract sentences and key words from text
        sentences = [s.strip() for s in text.split('.') if len(s.strip()) > 20][:10]
        words = [word.lower() for word in text.split() if len(word) > 4 and word.isalpha()][:20]
        
        mcq_questions = []
        short_questions = []
        
        # Template-based MCQ questions
        mcq_templates = [
            "What is the main topic discussed in the provided text?",
            "Which of the following best describes the key concept mentioned?",
            "What is the primary focus of the material presented?",
            "Which statement accurately reflects the main idea?",
            "What is the central theme of the text?"
        ]
        
        option_templates = [
            ["A concept discussed in the text", "A related topic mentioned", "An important idea presented", "A key point emphasized"],
            ["The main subject matter", "A supporting detail", "An example provided", "A conclusion drawn"],
            ["The primary content", "A secondary point", "A background detail", "A future implication"],
            ["The core message", "A supporting argument", "An illustration", "A summary"],
            ["The fundamental idea", "A supporting concept", "An application", "A limitation"]
        ]
        
        for i in range(min(num_mcq, len(mcq_templates))):
            mcq_questions.append({
                "question": mcq_templates[i],
                "options": option_templates[i],
                "correct_answer": "A"
            })
        
        # Template-based short answer questions
        short_templates = [
            "Summarize the main points from the provided text in 2-3 sentences.",
            "What are the key concepts discussed in the material?",
            "Explain the main ideas presented in the text.",
            "What is the significance of the topics covered?",
            "How do the concepts in the text relate to each other?"
        ]
        
        for i in range(min(num_short, len(short_templates))):
            short_questions.append({
                "question": short_templates[i],
                "expected_answer": "The text discusses various concepts and ideas that should be analyzed based on the content provided."
            })
        
        return {
            "mcq_questions": mcq_questions,
            "short_questions": short_questions
        }

    def generate_questions(self, text: str, num_mcq: int = 3, num_short: int = 2) -> Dict[str, List[Dict]]:
        """
        Generate questions from the provided text, using cache if available.
        """
        # Generate content hash
        content_hash = Question.generate_content_hash(text)
        
        # Check cache first
        try:
            cached = QuestionCache.objects.get(content_hash=content_hash)
            cached.times_used += 1
            cached.save()
            return cached.questions
        except QuestionCache.DoesNotExist:
            pass

        if not self.primary_api:
            logger.warning("No API keys configured for question generation")
            return self._generate_template_questions(text, num_mcq, num_short)

        try:
            prompt = self._create_prompt(text, num_mcq, num_short)
            
            # Try APIs in order of preference with better error handling
            response = None
            last_error = None
            
            # Try Gemini first
            if self.primary_api == 'gemini' and self.gemini_api_key:
                try:
                    response = self._call_gemini_api(prompt)
                    if response:
                        logger.info("Successfully generated questions using Gemini API")
                except Exception as e:
                    last_error = e
                    logger.warning(f"Gemini failed, trying OpenAI: {e}")
                    
            # Try OpenAI if Gemini failed or not available
            if not response and self.openai_api_key:
                try:
                    response = self._call_openai_api(prompt)
                    if response:
                        logger.info("Successfully generated questions using OpenAI API")
                except Exception as e:
                    last_error = e
                    logger.warning(f"OpenAI failed, trying Hugging Face: {e}")
                    
            # Try Hugging Face if OpenAI failed or not available
            if not response and self.hf_token:
                try:
                    response = self._call_huggingface_api(prompt)
                    if response:
                        logger.info("Successfully generated questions using Hugging Face API")
                except Exception as e:
                    last_error = e
                    logger.warning(f"Hugging Face failed, trying local fallback: {e}")
            
            # Local GPT-2 fallback
            if not response:
                try:
                    response = self._call_local_gpt2(prompt)
                    if response:
                        logger.info("Used local GPT-2 fallback for question generation.")
                except Exception as e:
                    last_error = e
                    logger.error(f"Local GPT-2 fallback failed: {e}")
            
            if not response:
                logger.error(f"All question generation methods failed. Last error: {last_error}")
                logger.info("Using template-based question generation as final fallback")
                return self._generate_template_questions(text, num_mcq, num_short)
            
            # Parse the response
            questions = self._parse_response(response)
            
            # Validate that we got some questions
            if not questions.get("mcq_questions") and not questions.get("short_questions"):
                logger.warning("No questions generated from API response, using fallback")
                return self._generate_template_questions(text, num_mcq, num_short)
            
            # Validate question quality - if questions look malformed, use template fallback
            if self._are_questions_malformed(questions):
                logger.warning("Questions appear malformed, using template fallback")
                return self._generate_template_questions(text, num_mcq, num_short)
            
            # Cache the generated questions
            try:
                QuestionCache.objects.create(
                    content_hash=content_hash,
                    questions=questions
                )
            except Exception as e:
                logger.warning(f"Failed to cache questions: {e}")
            
            return questions
            
        except Exception as e:
            logger.error(f"Error generating questions: {e}")
            return self._generate_template_questions(text, num_mcq, num_short)

    def _are_questions_malformed(self, questions: Dict[str, List[Dict]]) -> bool:
        """Check if generated questions appear to be malformed"""
        try:
            # Check MCQ questions
            mcq_questions = questions.get("mcq_questions", [])
            for q in mcq_questions:
                question_text = q.get("question", "")
                options = q.get("options", [])
                
                # Check for placeholder text or malformed questions
                if any(placeholder in question_text.lower() for placeholder in ["[question]", "[option", "placeholder"]):
                    return True
                
                # Check if options are malformed
                if len(options) < 2:
                    return True
                
                for option in options:
                    if any(placeholder in option.lower() for placeholder in ["[option", "placeholder"]):
                        return True
            
            # Check short answer questions
            short_questions = questions.get("short_questions", [])
            for q in short_questions:
                question_text = q.get("question", "")
                if any(placeholder in question_text.lower() for placeholder in ["[question]", "placeholder"]):
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking question quality: {e}")
            return True  # Assume malformed if we can't check

    def _parse_response(self, response: str) -> Dict[str, List[Dict]]:
        """
        Parse the raw response into a structured format.
        """
        questions = {
            "mcq_questions": [],
            "short_questions": []
        }
        
        current_mcq = None
        current_short = None
        
        for line in response.split('\n'):
            line = line.strip()
            if not line:
                continue
                
            if line.startswith('MCQ'):
                if current_mcq:
                    questions["mcq_questions"].append(current_mcq)
                current_mcq = {
                    "question": line.split(':', 1)[1].strip() if ':' in line else line,
                    "options": [],
                    "correct_answer": None
                }
            elif line.startswith(('A)', 'B)', 'C)', 'D)')):
                if current_mcq:
                    current_mcq["options"].append(line[3:].strip())
            elif line.startswith('Correct Answer:'):
                if current_mcq:
                    current_mcq["correct_answer"] = line.split(':', 1)[1].strip()
            elif line.startswith('Short Answer'):
                if current_short:
                    questions["short_questions"].append(current_short)
                current_short = {
                    "question": line.split(':', 1)[1].strip() if ':' in line else line,
                    "expected_answer": None
                }
            elif line.startswith('Expected Answer:'):
                if current_short:
                    current_short["expected_answer"] = line.split(':', 1)[1].strip()
        
        # Add the last questions if they exist
        if current_mcq:
            questions["mcq_questions"].append(current_mcq)
        if current_short:
            questions["short_questions"].append(current_short)
            
        return questions 