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
        self.azure_openai_api_key = getattr(settings, 'AZURE_OPENAI_API_KEY', None)
        self.azure_openai_endpoint = getattr(settings, 'AZURE_OPENAI_ENDPOINT', None)
        self.gemini_api_key = getattr(settings, 'GEMINI_API_KEY', None)
        self.gemini_model = getattr(settings, 'GEMINI_MODEL', 'gemini-1.5-pro')
        self.hf_token = getattr(settings, 'HUGGING_FACE_API_TOKEN', None)
        
        # Prefer Azure OpenAI, then Gemini, then Hugging Face
        if self.azure_openai_api_key and self.azure_openai_endpoint:
            self.primary_api = 'azure_openai'
        elif self.gemini_api_key:
            self.primary_api = 'gemini'
        elif self.hf_token:
            self.primary_api = 'huggingface'
        else:
            self.primary_api = None
            logger.warning("No API keys configured for question generation")

    def _create_prompt(self, text: str, num_mcq: int = 3, num_short: int = 2, subject: str = None) -> str:
        subject_line = f"Subject/Topic: {subject}\n" if subject else ""
        return f"""Task: Create {num_mcq} multiple-choice questions and {num_short} short-answer questions based on the following text.\n{subject_line}\nText:\n---\n{text}\n---\n\nInstructions:\nFor both multiple-choice and short-answer questions, split them evenly into two types:\n- The first half should be standard questions (clear, focused, test understanding, recall, or basic comprehension).\n- The second half should be challenging questions (require higher-order thinking: application, analysis, synthesis, or evaluation; more analytical and require reasoning or application of concepts).\nIf the number is odd, make the extra question standard.\n\n1. For multiple-choice questions:\n   - For standard questions:\n     - Create clear, focused questions that test understanding or recall\n     - Provide 4 options (A, B, C, D)\n     - Mark the correct answer\n     - For each question, provide a short explanation (1-2 sentences) of why the correct answer is right.\n   - For challenging questions:\n     - Create analytical questions that require higher-order thinking (application, analysis, synthesis, evaluation)\n     - Make distractors (incorrect options) plausible and non-trivial\n     - Provide 4 options (A, B, C, D)\n     - Mark the correct answer\n     - For each question, provide a short explanation (1-2 sentences) of why the correct answer is right and why the distractors are wrong.\n\n2. For short-answer questions:\n   - For standard questions:\n     - Create questions that need brief but thoughtful answers\n     - Focus on understanding or recall\n     - Include the expected answer\n     - For each question, provide a short explanation (1-2 sentences) of what makes a good answer.\n   - For challenging questions:\n     - Create open-ended questions that require explanation, analysis, or application of concepts\n     - Avoid questions that can be answered with a single word or simple fact\n     - Include the expected answer\n     - For each question, provide a short explanation (1-2 sentences) of what makes a good answer.\n\nFormat your response exactly like this:\nMCQ1: [Question]\nA) [Option A]\nB) [Option B]\nC) [Option C]\nD) [Option D]\nCorrect Answer: [Letter]\nExplanation: [Short explanation]\n\n[Repeat for other MCQs]\n\nShort Answer 1: [Question]\nExpected Answer: [Brief answer]\nExplanation: [Short explanation]\n\n[Repeat for other short answers]"""

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

    def _call_azure_openai_api(self, prompt: str) -> str:
        """Call Azure OpenAI API (chat/completions endpoint)"""
        try:
            headers = {
                'Content-Type': 'application/json',
                'api-key': self.azure_openai_api_key
            }
            payload = {
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 5000,
                "temperature": 0.7
            }
            response = requests.post(self.azure_openai_endpoint, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            result = response.json()
            return result['choices'][0]['message']['content']
        except Exception as e:
            logger.error(f"Azure OpenAI API error: {e}")
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

    def _call_ollama(self, prompt: str, model: str = 'llama3') -> str:
        import requests
        url = 'http://localhost:11434/api/generate'
        data = {
            'model': model,
            'prompt': prompt,
            'stream': False
        }
        response = requests.post(url, json=data, timeout=120)
        response.raise_for_status()
        return response.json()['response']

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
                "answer": "A"
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
                "answer": "The text discusses various concepts and ideas that should be analyzed based on the content provided."
            })
        
        return {
            "mcq_questions": mcq_questions,
            "short_questions": short_questions
        }

    def generate_questions(self, text: str, num_mcq: int = 3, num_short: int = 2) -> Dict[str, List[Dict]]:
        """
        Generate questions from the provided text, with multiple fallback options.
        """
        prompt = self._create_prompt(text, num_mcq, num_short)
        
        # Try different APIs in order of preference
        apis_to_try = []
        
        # Add Ollama if available
        try:
            import requests
            response = requests.get('http://localhost:11434/api/tags', timeout=5)
            if response.status_code == 200:
                apis_to_try.append(('ollama', self._call_ollama))
        except Exception as e:
            pass
        
        # Add other APIs based on available keys
        if self.azure_openai_api_key and self.azure_openai_endpoint:
            apis_to_try.append(('azure_openai', self._call_azure_openai_api))
        if self.gemini_api_key:
            apis_to_try.append(('gemini', self._call_gemini_api))
        if self.hf_token:
            apis_to_try.append(('huggingface', self._call_huggingface_api))
        
        # Try each API
        for api_name, api_func in apis_to_try:
            try:
                logger.info(f"Trying {api_name} API")
                response = api_func(prompt)
                if response and response.strip():
                    questions = self._parse_response(response)
                    # Validate that we got some questions
                    if questions.get("mcq_questions") or questions.get("short_questions"):
                        logger.info(f"Successfully generated questions using {api_name}")
                        return questions
            except Exception as e:
                logger.warning(f"{api_name} API failed: {e}")
                continue
        
        # If all APIs fail, use template questions
        logger.info("All APIs failed, using template questions")
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
        Parse the raw response into a structured format, including explanations if present.
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
                    "answer": None,
                    "explanation": None
                }
            elif line.startswith(('A)', 'B)', 'C)', 'D)', 'E)')):
                if current_mcq:
                    option_text = line[3:].strip()
                    # If this is E) and is 'None of the above', mark it
                    if line[:2] == 'E)' and option_text.lower() == 'none of the above':
                        current_mcq["options"].append('None of the above')
                    else:
                        current_mcq["options"].append(option_text)
            elif line.startswith('Correct Answer:'):
                if current_mcq:
                    current_mcq["answer"] = line.split(':', 1)[1].strip()
            elif line.startswith('Explanation:'):
                if current_mcq:
                    current_mcq["explanation"] = line.split(':', 1)[1].strip()
                elif current_short:
                    current_short["explanation"] = line.split(':', 1)[1].strip()
            elif line.startswith('Short Answer'):
                if current_short:
                    questions["short_questions"].append(current_short)
                current_short = {
                    "question": line.split(':', 1)[1].strip() if ':' in line else line,
                    "answer": None,
                    "explanation": None
                }
            elif line.startswith('Expected Answer:'):
                if current_short:
                    current_short["answer"] = line.split(':', 1)[1].strip()
        # Add the last questions if they exist
        if current_mcq:
            # Only add 'None of the above' as E if:
            # - The correct answer is E and none of the options (A-D) match the answer text (i.e., answer is not present among A-D),
            # - OR if the question or any option text contains 'none of the above' (case-insensitive)
            add_none_of_above = False
            if current_mcq["answer"] and current_mcq["answer"].upper() == 'E':
                # Check if any option contains 'none of the above'
                if any('none of the above' in opt.lower() for opt in current_mcq["options"]):
                    add_none_of_above = True
                # Check if the question text contains 'none of the above'
                elif 'none of the above' in current_mcq["question"].lower():
                    add_none_of_above = True
                # Check if the answer is not present among A-D
                elif len(current_mcq["options"]) == 4:
                    add_none_of_above = True
            if add_none_of_above and len(current_mcq["options"]) == 4:
                current_mcq["options"].append('None of the above')
            questions["mcq_questions"].append(current_mcq)
        if current_short:
            questions["short_questions"].append(current_short)
        return questions 