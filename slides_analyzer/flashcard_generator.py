import openai
from django.conf import settings
import logging
import re

logger = logging.getLogger(__name__)

class FlashcardGenerator:
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
                logger.info("Flashcard Generator initialized with Azure OpenAI")
                
            # Fallback to regular OpenAI
            elif hasattr(settings, 'OPENAI_API_KEY') and settings.OPENAI_API_KEY:
                self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
                logger.info("Flashcard Generator initialized with OpenAI")
                
            else:
                logger.warning("No OpenAI API key found in settings")
        except Exception as e:
            logger.error(f"Error initializing Flashcard Generator: {e}")

    def generate_flashcards(self, text, num_flashcards=10):
        """
        Generate flashcards from text content.
        Returns a list of flashcards with front (question/concept) and back (answer/explanation).
        """
        if not self.client:
            return {"error": "Flashcard generator not properly initialized"}

        if not text or len(text.strip()) < 50:
            return {"error": "Text content is too short to generate meaningful flashcards"}

        try:
            # Create a comprehensive prompt for flashcard generation
            prompt = f"""
            You are creating {num_flashcards} flashcards from the provided study material. 
            
            CRITICAL REQUIREMENTS:
            1. Extract ONLY information that is EXPLICITLY stated in the provided text
            2. Do NOT add any external knowledge or general information
            3. Use exact definitions, facts, and explanations from the text
            4. Quote specific terms, concepts, and key points from the material
            5. Include page numbers, section references, or specific examples mentioned in the text
            
            FLASHCARD STRUCTURE:
            - Front: A specific question, term, or concept directly from the text
            - Back: The exact definition, explanation, or answer as stated in the text
            
            CONTENT REQUIREMENTS:
            - Use actual terminology and vocabulary from the text
            - Include specific numbers, dates, names, and facts mentioned
            - Reference specific processes, steps, or procedures described
            - Include key relationships, comparisons, or contrasts mentioned
            - Use exact quotes when appropriate (with quotation marks)
            
            STUDY MATERIAL:
            {text[:4000]}
            
            STRICT OUTPUT FORMAT:
            You MUST output exactly {num_flashcards} flashcards in this EXACT format:
            
            1. Front: [Write the question or concept here]
            1. Back: [Write the answer or explanation here]
            2. Front: [Write the question or concept here]
            2. Back: [Write the answer or explanation here]
            3. Front: [Write the question or concept here]
            3. Back: [Write the answer or explanation here]
            ...
            {num_flashcards}. Front: [Write the question or concept here]
            {num_flashcards}. Back: [Write the answer or explanation here]
            
            IMPORTANT: Each flashcard must have TWO separate lines - one for Front and one for Back, both with the same number.
            Do NOT combine Front and Back on the same line.
            Generate exactly {num_flashcards} flashcards using ONLY information from the provided text.
            """

            response = self.client.chat.completions.create(
                model="gpt-4" if "gpt-4" in str(self.client) else "gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert educational content extractor. Your job is to create flashcards that contain ONLY information explicitly stated in the provided study material. Do not add any external knowledge, general information, or assumptions. Extract and use the exact definitions, facts, examples, and explanations from the text."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2500,
                temperature=0.3
            )
            
            if not response.choices or not response.choices[0].message.content:
                return {"error": "No response from AI model"}

            # Parse the response to extract flashcards
            flashcards = self._parse_flashcards(response.choices[0].message.content, num_flashcards)
            
            if not flashcards:
                return {"error": "Failed to parse flashcards from AI response"}

            # Validate that flashcards contain actual content from the text
            validated_flashcards = self._validate_flashcard_content(flashcards, text)
            
            if not validated_flashcards:
                return {"error": "Generated flashcards do not contain sufficient content from the provided text"}

            return {"flashcards": validated_flashcards}

        except Exception as e:
            logger.error(f"Error generating flashcards: {e}")
            return {"error": f"Failed to generate flashcards: {str(e)}"}

    def _parse_flashcards(self, response_text, expected_count):
        """
        Parse the AI response to extract structured flashcards.
        Expected format: 
        1. Front: [content]
        1. Back: [content]
        2. Front: [content]
        2. Back: [content]
        etc.
        """
        flashcards = []
        
        # First, try to parse the new format where each flashcard has two separate lines
        # Pattern: number. Front: content (until next number or end)
        pattern_front = r'(\d+)\.\s*Front:\s*(.*?)(?=\n\d+\.|$)'
        front_matches = re.findall(pattern_front, response_text, re.DOTALL | re.IGNORECASE)
        
        pattern_back = r'(\d+)\.\s*Back:\s*(.*?)(?=\n\d+\.|$)'
        back_matches = re.findall(pattern_back, response_text, re.DOTALL | re.IGNORECASE)
        
        # Create a dictionary to pair fronts and backs by number
        fronts = {int(num): self._clean_text(content) for num, content in front_matches}
        backs = {int(num): self._clean_text(content) for num, content in back_matches}
        
        # Pair them up
        for num in sorted(fronts.keys()):
            if num in backs and fronts[num] and backs[num]:
                flashcards.append({'front': fronts[num], 'back': backs[num]})
        
        if flashcards:
            return flashcards[:expected_count]
        
        # Fallback: try the old format (Front and Back on same line)
        pattern_old = r'\d+\.\s*Front:\s*(.*?)\s*Back:\s*(.*?)(?=\n\d+\.|$)'
        matches = re.findall(pattern_old, response_text, re.DOTALL | re.IGNORECASE)
        if matches:
            for match in matches:
                if len(match) == 2:
                    front = self._clean_text(match[0])
                    back = self._clean_text(match[1])
                    if front and back:
                        flashcards.append({'front': front, 'back': back})
            if flashcards:
                return flashcards[:expected_count]
        
        # Fallback: try to pair every two lines (question, answer)
        lines = [l.strip() for l in response_text.splitlines() if l.strip()]
        i = 0
        while i < len(lines) - 1:
            if lines[i].lower().startswith('front:') and lines[i+1].lower().startswith('back:'):
                front = self._clean_text(lines[i][6:])
                back = self._clean_text(lines[i+1][5:])
                if front and back:
                    flashcards.append({'front': front, 'back': back})
                i += 2
            else:
                i += 1
        if flashcards:
            return flashcards[:expected_count]
        
        # Final fallback: try to pair lines in order
        pairs = [lines[j:j+2] for j in range(0, len(lines), 2)]
        for pair in pairs:
            if len(pair) == 2:
                flashcards.append({'front': self._clean_text(pair[0]), 'back': self._clean_text(pair[1])})
        
        return flashcards[:expected_count]

    def _clean_text(self, text):
        """Clean and format text for flashcards while preserving important content."""
        if not text:
            return ""
            
        # Remove extra whitespace and newlines but preserve paragraph breaks
        text = re.sub(r'\n\s*\n', '\n\n', text.strip())
        text = re.sub(r'[ \t]+', ' ', text)
        
        # Remove common prefixes but preserve the actual content
        text = re.sub(r'^(Front|Back|Q|A|Question|Answer):\s*', '', text, flags=re.IGNORECASE)
        
        # Remove numbering at the start but preserve numbered lists within content
        text = re.sub(r'^\d+[\.\)]\s*', '', text)
        
        # Remove any remaining leading/trailing whitespace
        text = text.strip()
        
        # Ensure the text is not empty after cleaning
        if not text or text.isspace():
            return ""
            
        return text

    def _validate_flashcard_content(self, flashcards, original_text):
        """
        Validate that flashcards contain actual content from the original text.
        """
        if not flashcards or not original_text:
            return flashcards
            
        validated_flashcards = []
        original_text_lower = original_text.lower()
        
        for flashcard in flashcards:
            front = flashcard.get('front', '').lower()
            back = flashcard.get('back', '').lower()
            
            # Check if front or back contains significant content from original text
            front_score = self._calculate_content_overlap(front, original_text_lower)
            back_score = self._calculate_content_overlap(back, original_text_lower)
            
            # Require at least some content overlap or specific terms
            if front_score > 0.1 or back_score > 0.1 or self._contains_key_terms(front + ' ' + back, original_text_lower):
                validated_flashcards.append(flashcard)
            else:
                logger.warning(f"Flashcard rejected due to insufficient content overlap: {flashcard.get('front', '')[:50]}...")
        
        return validated_flashcards

    def _calculate_content_overlap(self, flashcard_text, original_text):
        """
        Calculate the overlap between flashcard text and original text.
        """
        if not flashcard_text or not original_text:
            return 0
            
        # Split into words and find common terms
        flashcard_words = set(re.findall(r'\b\w+\b', flashcard_text))
        original_words = set(re.findall(r'\b\w+\b', original_text))
        
        if not flashcard_words:
            return 0
            
        common_words = flashcard_words.intersection(original_words)
        return len(common_words) / len(flashcard_words)

    def _contains_key_terms(self, flashcard_text, original_text):
        """
        Check if flashcard contains key terms from the original text.
        """
        # Extract potential key terms (longer words, technical terms)
        key_terms = re.findall(r'\b\w{6,}\b', original_text)
        flashcard_words = set(re.findall(r'\b\w+\b', flashcard_text))
        
        # Check if any key terms appear in the flashcard
        for term in key_terms:
            if term in flashcard_words:
                return True
        return False

    def generate_concept_flashcards(self, text, num_flashcards=10):
        """
        Generate concept-based flashcards focusing on key terms and definitions.
        """
        if not self.client:
            return {"error": "Flashcard generator not properly initialized"}

        try:
            prompt = f"""
            You are creating {num_flashcards} concept flashcards from the provided study material.
            
            CRITICAL REQUIREMENTS:
            1. Extract ONLY terms, concepts, and definitions that are EXPLICITLY defined or explained in the text
            2. Do NOT add any external definitions or general knowledge
            3. Use the exact terminology and definitions as stated in the material
            4. Include specific examples, characteristics, or properties mentioned for each concept
            5. Reference the specific context or section where each concept is discussed
            
            CONCEPT FLASHCARD STRUCTURE:
            - Front: The exact term or concept name as it appears in the text
            - Back: The complete definition, explanation, or description as stated in the text
            
            CONTENT REQUIREMENTS:
            - Use exact vocabulary and terminology from the text
            - Include specific characteristics, properties, or features mentioned
            - Reference any examples, applications, or contexts provided
            - Include any classifications, categories, or types mentioned
            - Use exact quotes when the text provides a formal definition
            
            STUDY MATERIAL:
            {text[:4000]}
            
            STRICT OUTPUT FORMAT:
            You MUST output exactly {num_flashcards} concept flashcards in this EXACT format:
            
            1. Front: [Write the exact term/concept from the text here]
            1. Back: [Write the complete definition/explanation from the text here]
            2. Front: [Write the exact term/concept from the text here]
            2. Back: [Write the complete definition/explanation from the text here]
            3. Front: [Write the exact term/concept from the text here]
            3. Back: [Write the complete definition/explanation from the text here]
            ...
            {num_flashcards}. Front: [Write the exact term/concept from the text here]
            {num_flashcards}. Back: [Write the complete definition/explanation from the text here]
            
            IMPORTANT: Each flashcard must have TWO separate lines - one for Front and one for Back, both with the same number.
            Do NOT combine Front and Back on the same line.
            Generate exactly {num_flashcards} concept flashcards using ONLY information from the provided text.
            """

            response = self.client.chat.completions.create(
                model="gpt-4" if "gpt-4" in str(self.client) else "gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert concept extractor. Your job is to identify and extract ONLY terms, concepts, and definitions that are explicitly stated in the provided study material. Do not add any external definitions or general knowledge. Use the exact terminology and explanations as they appear in the text."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2500,
                temperature=0.3
            )
            
            if not response.choices or not response.choices[0].message.content:
                return {"error": "No response from AI model"}

            flashcards = self._parse_flashcards(response.choices[0].message.content, num_flashcards)
            
            # Validate that flashcards contain actual content from the text
            validated_flashcards = self._validate_flashcard_content(flashcards, text)
            
            if not validated_flashcards:
                return {"error": "Generated concept flashcards do not contain sufficient content from the provided text"}

            return {"flashcards": validated_flashcards}

        except Exception as e:
            logger.error(f"Error generating concept flashcards: {e}")
            return {"error": f"Failed to generate concept flashcards: {str(e)}"}

    def generate_process_flashcards(self, text, num_flashcards=10):
        """
        Generate process-based flashcards focusing on steps, procedures, and sequences.
        """
        if not self.client:
            return {"error": "Flashcard generator not properly initialized"}

        try:
            prompt = f"""
            You are creating {num_flashcards} process flashcards from the provided study material.
            
            CRITICAL REQUIREMENTS:
            1. Extract ONLY processes, steps, procedures, and sequences that are EXPLICITLY described in the text
            2. Do NOT add any external knowledge about processes or procedures
            3. Use the exact steps, order, and details as stated in the material
            4. Include specific conditions, requirements, or prerequisites mentioned
            5. Reference the exact sequence and timing as described in the text
            
            PROCESS FLASHCARD STRUCTURE:
            - Front: A specific question about a step, process, or procedure from the text
            - Back: The exact answer, explanation, or description as stated in the text
            
            CONTENT REQUIREMENTS:
            - Use exact step numbers, order, and sequence from the text
            - Include specific conditions, requirements, or prerequisites mentioned
            - Reference any tools, materials, or resources specified
            - Include timing, duration, or frequency mentioned
            - Use exact terminology and process names from the text
            - Include any warnings, cautions, or important notes mentioned
            
            STUDY MATERIAL:
            {text[:4000]}
            
            STRICT OUTPUT FORMAT:
            You MUST output exactly {num_flashcards} process flashcards in this EXACT format:
            
            1. Front: [Write the specific question about process/step from the text here]
            1. Back: [Write the exact answer/explanation from the text here]
            2. Front: [Write the specific question about process/step from the text here]
            2. Back: [Write the exact answer/explanation from the text here]
            3. Front: [Write the specific question about process/step from the text here]
            3. Back: [Write the exact answer/explanation from the text here]
            ...
            {num_flashcards}. Front: [Write the specific question about process/step from the text here]
            {num_flashcards}. Back: [Write the exact answer/explanation from the text here]
            
            IMPORTANT: Each flashcard must have TWO separate lines - one for Front and one for Back, both with the same number.
            Do NOT combine Front and Back on the same line.
            Generate exactly {num_flashcards} process flashcards using ONLY information from the provided text.
            """

            response = self.client.chat.completions.create(
                model="gpt-4" if "gpt-4" in str(self.client) else "gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert process extractor. Your job is to identify and extract ONLY processes, steps, procedures, and sequences that are explicitly described in the provided study material. Do not add any external knowledge about processes or procedures. Use the exact steps, order, and details as they appear in the text."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2500,
                temperature=0.3
            )
            
            if not response.choices or not response.choices[0].message.content:
                return {"error": "No response from AI model"}

            flashcards = self._parse_flashcards(response.choices[0].message.content, num_flashcards)
            
            # Validate that flashcards contain actual content from the text
            validated_flashcards = self._validate_flashcard_content(flashcards, text)
            
            if not validated_flashcards:
                return {"error": "Generated process flashcards do not contain sufficient content from the provided text"}

            return {"flashcards": validated_flashcards}

        except Exception as e:
            logger.error(f"Error generating process flashcards: {e}")
            return {"error": f"Failed to generate process flashcards: {str(e)}"}

# Create a global instance and function for backward compatibility
flashcard_generator = FlashcardGenerator()

def generate_flashcards_from_text(text: str, num_flashcards: int = 10):
    """
    Generate flashcards from text using the FlashcardGenerator instance.
    This function provides backward compatibility for existing code.
    """
    return flashcard_generator.generate_flashcards(text, num_flashcards) 