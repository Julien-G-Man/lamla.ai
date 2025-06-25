#!/usr/bin/env python3
"""
Test script for question generation functionality
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edtech_project.settings')
django.setup()

from slides_analyzer.question_generator import QuestionGenerator

def test_question_generation():
    """Test the question generation with sample text"""
    
    print("🧪 Testing Question Generation")
    print("=" * 40)
    
    # Sample text for testing
    sample_text = """
    Machine learning is a subset of artificial intelligence that focuses on the development of computer programs that can access data and use it to learn for themselves. The process of learning begins with observations or data, such as examples, direct experience, or instruction, in order to look for patterns in data and make better decisions in the future based on the examples that we provide. The primary aim is to allow the computers learn automatically without human intervention or assistance and adjust actions accordingly.
    
    There are three main types of machine learning: supervised learning, unsupervised learning, and reinforcement learning. Supervised learning involves training a model on labeled data, while unsupervised learning finds patterns in unlabeled data. Reinforcement learning uses a system of rewards and penalties to guide the learning process.
    """
    
    print(f"📝 Sample text length: {len(sample_text)} characters")
    
    try:
        # Initialize question generator
        generator = QuestionGenerator()
        print(f"✅ Question Generator initialized")
        print(f"🔑 Primary API: {generator.primary_api}")
        
        # Generate questions
        print("\n🔄 Generating questions...")
        questions = generator.generate_questions(
            text=sample_text,
            num_mcq=3,
            num_short=2
        )
        
        # Display results
        print("\n📊 Results:")
        print(f"MCQ Questions: {len(questions.get('mcq_questions', []))}")
        print(f"Short Questions: {len(questions.get('short_questions', []))}")
        
        if 'error' in questions:
            print(f"❌ Error: {questions['error']}")
        else:
            print("\n📋 MCQ Questions:")
            for i, q in enumerate(questions.get('mcq_questions', []), 1):
                print(f"  {i}. {q.get('question', 'No question')}")
                for j, option in enumerate(q.get('options', [])):
                    print(f"     {chr(65+j)}. {option}")
                print(f"     Correct: {q.get('correct_answer', 'Unknown')}")
                print()
            
            print("📝 Short Answer Questions:")
            for i, q in enumerate(questions.get('short_questions', []), 1):
                print(f"  {i}. {q.get('question', 'No question')}")
                print(f"     Expected: {q.get('expected_answer', 'No answer')}")
                print()
        
        print("✅ Test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_question_generation()
    sys.exit(0 if success else 1) 