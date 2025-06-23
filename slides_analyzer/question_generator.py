import os
from typing import Dict, List, Optional
from django.conf import settings
from transformers import pipeline, AutoModelForCausalLM, AutoTokenizer
import torch
from .models import Question, QuestionCache

class QuestionGenerator:
    def __init__(self):
        # Initialize with a smaller model that can run on CPU
        self.model_name = "distilgpt2"  # Small model that can run on CPU
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForCausalLM.from_pretrained(self.model_name)
        
        # Move model to CPU if CUDA is not available
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model.to(self.device)
        
        # Initialize the text generation pipeline
        self.generator = pipeline(
            "text-generation",
            model=self.model,
            tokenizer=self.tokenizer,
            device=0 if self.device == "cuda" else -1
        )

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

        try:
            prompt = self._create_prompt(text, num_mcq, num_short)
            
            # Generate text using the local model
            response = self.generator(
                prompt,
                max_length=800,
                num_return_sequences=1,
                temperature=0.8,
                top_p=0.95,
                repetition_penalty=1.2,
                do_sample=True
            )[0]['generated_text']
            
            # Parse the response
            questions = self._parse_response(response)
            
            # Cache the generated questions
            QuestionCache.objects.create(
                content_hash=content_hash,
                questions=questions
            )
            
            return questions
            
        except Exception as e:
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
                    "question": line.split(':', 1)[1].strip(),
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
                    "question": line.split(':', 1)[1].strip(),
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