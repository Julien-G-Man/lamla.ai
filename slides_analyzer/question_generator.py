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
        self.gemini_model = getattr(settings, 'GEMINI_MODEL', 'models/gemini-1.5-pro')
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
        """Call Hugging Face API"""
        try:
            API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
            headers = {"Authorization": f"Bearer {self.hf_token}"}
            
            payload = {
                "inputs": f"<s>[INST] {prompt} [/INST]",
                "parameters": {
                    "max_new_tokens": 800,
                    "temperature": 0.7,
                    "top_p": 0.95,
                    "do_sample": True
                }
            }
            
            response = requests.post(API_URL, headers=headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                return result[0].get('generated_text', '')
            return str(result)
        except Exception as e:
            logger.error(f"Hugging Face API error: {e}")
            raise

    def _call_local_gpt2(self, prompt: str) -> str:
        """Call local Hugging Face GPT-2 model as a last resort."""
        try:
            from transformers import pipeline
            generator = pipeline("text-generation", model="gpt2")
            result = generator(prompt, max_length=120, num_return_sequences=1)
            return result[0]['generated_text']
        except Exception as e:
            logger.error(f"Local GPT-2 error: {e}")
            return ""

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
            return {
                "error": "No API keys configured for question generation",
                "mcq_questions": [],
                "short_questions": []
            }

        try:
            prompt = self._create_prompt(text, num_mcq, num_short)
            
            # Try APIs in order of preference
            response = None
            last_error = None
            
            if self.primary_api == 'gemini':
                try:
                    response = self._call_gemini_api(prompt)
                except Exception as e:
                    last_error = e
                    logger.warning(f"Gemini failed, trying OpenAI: {e}")
                    
            if not response and self.openai_api_key:
                try:
                    response = self._call_openai_api(prompt)
                except Exception as e:
                    last_error = e
                    logger.warning(f"OpenAI failed, trying Hugging Face: {e}")
                    
            if not response and self.hf_token:
                try:
                    response = self._call_huggingface_api(prompt)
                except Exception as e:
                    last_error = e
                    logger.error(f"All APIs failed: {e}")
            
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
                return {
                    "error": f"Failed to generate questions: {last_error}",
                    "mcq_questions": [],
                    "short_questions": []
                }
            
            # Parse the response
            questions = self._parse_response(response)
            
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
            return {
                "error": str(e),
                "mcq_questions": [],
                "short_questions": []
            }

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