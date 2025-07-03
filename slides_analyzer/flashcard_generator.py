import google.generativeai as genai
from django.conf import settings
import logging
import re

logger = logging.getLogger(__name__)

class FlashcardGenerator:
    def __init__(self):
        self.model = None
        try:
            if hasattr(settings, 'GEMINI_API_KEY') and settings.GEMINI_API_KEY:
                genai.configure(api_key=settings.GEMINI_API_KEY)
                self.model = genai.GenerativeModel('gemini-pro')
                logger.info("Flashcard Generator initialized successfully")
            else:
                logger.warning("GEMINI_API_KEY not found in settings")
        except Exception as e:
            logger.error(f"Error initializing Flashcard Generator: {e}")

    def generate_flashcards(self, text, num_flashcards=10):
        """
        Generate flashcards from text content.
        Returns a list of flashcards with front (question/concept) and back (answer/explanation).
        """
        if not self.model:
            return {"error": "Flashcard generator not properly initialized"}

        if not text or len(text.strip()) < 50:
            return {"error": "Text content is too short to generate meaningful flashcards"}

        try:
            # Create a comprehensive prompt for flashcard generation
            prompt = f"""
            Create {num_flashcards} educational flashcards from the following text. 
            Each flashcard should have:
            1. Front: A clear question, concept, or term to study
            2. Back: A comprehensive explanation, definition, or answer

            Guidelines:
            - Focus on key concepts, definitions, important facts, and relationships
            - Make questions that test understanding, not just memorization
            - Include a mix of different types: definitions, concepts, processes, comparisons
            - Keep front concise but clear
            - Make back explanations detailed but easy to understand
            - Use examples when helpful
            - Avoid overly complex language

            Text content:
            {text[:4000]}  # Limit text length to avoid token limits

            Format each flashcard as:
            Front: [Question/Concept]
            Back: [Answer/Explanation]

            Generate exactly {num_flashcards} flashcards.
            """

            response = self.model.generate_content(prompt)
            
            if not response.text:
                return {"error": "No response from AI model"}

            # Parse the response to extract flashcards
            flashcards = self._parse_flashcards(response.text, num_flashcards)
            
            if not flashcards:
                return {"error": "Failed to parse flashcards from AI response"}

            return {"flashcards": flashcards}

        except Exception as e:
            logger.error(f"Error generating flashcards: {e}")
            return {"error": f"Failed to generate flashcards: {str(e)}"}

    def _parse_flashcards(self, response_text, expected_count):
        """
        Parse the AI response to extract structured flashcards.
        """
        flashcards = []
        
        # Split by common flashcard patterns
        patterns = [
            r'Front:\s*(.*?)\s*Back:\s*(.*?)(?=Front:|$)',
            r'Q:\s*(.*?)\s*A:\s*(.*?)(?=Q:|$)',
            r'Question:\s*(.*?)\s*Answer:\s*(.*?)(?=Question:|$)',
            r'(\d+\.\s*.*?)\s*-\s*(.*?)(?=\d+\.|$)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, response_text, re.DOTALL | re.IGNORECASE)
            if matches:
                for match in matches:
                    if len(match) == 2:
                        front = match[0].strip()
                        back = match[1].strip()
                        
                        # Clean up the text
                        front = self._clean_text(front)
                        back = self._clean_text(back)
                        
                        if front and back and len(front) > 5 and len(back) > 10:
                            flashcards.append({
                                'front': front,
                                'back': back
                            })
                
                if flashcards:
                    break
        
        # If regex parsing failed, try a simpler approach
        if not flashcards:
            flashcards = self._simple_parse(response_text, expected_count)
        
        return flashcards[:expected_count]

    def _clean_text(self, text):
        """Clean and format text for flashcards."""
        # Remove extra whitespace and newlines
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Remove common prefixes
        text = re.sub(r'^(Front|Back|Q|A|Question|Answer):\s*', '', text, flags=re.IGNORECASE)
        
        # Remove numbering
        text = re.sub(r'^\d+\.\s*', '', text)
        
        return text.strip()

    def _simple_parse(self, response_text, expected_count):
        """
        Simple parsing method as fallback.
        """
        flashcards = []
        
        # Split by lines and look for question-answer pairs
        lines = response_text.split('\n')
        current_front = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Look for question indicators
            if any(indicator in line.lower() for indicator in ['question:', 'q:', 'front:', 'what', 'define', 'explain']):
                if current_front and len(flashcards) < expected_count:
                    # Previous question without answer, create a simple flashcard
                    flashcards.append({
                        'front': current_front,
                        'back': 'Review this concept in your study materials.'
                    })
                current_front = line
            elif current_front and any(indicator in line.lower() for indicator in ['answer:', 'a:', 'back:', 'is:', 'are:', 'the']):
                # This looks like an answer
                flashcards.append({
                    'front': current_front,
                    'back': line
                })
                current_front = None
                
                if len(flashcards) >= expected_count:
                    break
        
        # Handle any remaining question without answer
        if current_front and len(flashcards) < expected_count:
            flashcards.append({
                'front': current_front,
                'back': 'Review this concept in your study materials.'
            })
        
        return flashcards

    def generate_concept_flashcards(self, text, num_flashcards=10):
        """
        Generate concept-based flashcards focusing on key terms and definitions.
        """
        if not self.model:
            return {"error": "Flashcard generator not properly initialized"}

        try:
            prompt = f"""
            Extract {num_flashcards} key concepts, terms, or definitions from the following text.
            Create flashcards that focus on understanding important terminology and concepts.

            For each concept, create:
            Front: The term or concept name
            Back: A clear definition or explanation

            Text content:
            {text[:3000]}

            Format as:
            Front: [Term/Concept]
            Back: [Definition/Explanation]

            Generate exactly {num_flashcards} concept flashcards.
            """

            response = self.model.generate_content(prompt)
            
            if not response.text:
                return {"error": "No response from AI model"}

            flashcards = self._parse_flashcards(response.text, num_flashcards)
            
            return {"flashcards": flashcards}

        except Exception as e:
            logger.error(f"Error generating concept flashcards: {e}")
            return {"error": f"Failed to generate concept flashcards: {str(e)}"}

    def generate_process_flashcards(self, text, num_flashcards=10):
        """
        Generate process-based flashcards focusing on steps, procedures, and sequences.
        """
        if not self.model:
            return {"error": "Flashcard generator not properly initialized"}

        try:
            prompt = f"""
            Extract {num_flashcards} processes, steps, or procedures from the following text.
            Create flashcards that focus on understanding sequences and procedures.

            For each process, create:
            Front: A question about a step or process
            Back: The answer explaining the step or process

            Text content:
            {text[:3000]}

            Format as:
            Front: [Question about process/step]
            Back: [Answer explaining the process/step]

            Generate exactly {num_flashcards} process flashcards.
            """

            response = self.model.generate_content(prompt)
            
            if not response.text:
                return {"error": "No response from AI model"}

            flashcards = self._parse_flashcards(response.text, num_flashcards)
            
            return {"flashcards": flashcards}

        except Exception as e:
            logger.error(f"Error generating process flashcards: {e}")
            return {"error": f"Failed to generate process flashcards: {str(e)}"} 