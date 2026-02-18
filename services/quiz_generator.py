"""
AI Quiz Generator Service - MCQ Only Version
Production version without debug messages
"""

from google import genai
from google.genai import types
import streamlit as st
import time
import json
import re
from typing import Optional, Dict


class QuizGenerator:
    """Smart quiz generator - MCQ only"""
    
    def __init__(self):
        """Initialize AI client"""
        # ✅ Always define models FIRST — before anything else
        self.models = [
            {"name": "gemini-2.5-flash-lite", "limit": "1000/day", "max_tokens": 8192},
            {"name": "gemini-2.5-flash",      "limit": "250/day",  "max_tokens": 8192},
        ]
        
        # Load API key manager
        try:
            from utils.api_key_manager import APIKeyManager
            self.key_manager = APIKeyManager()
            api_key = self.key_manager.get_current_key()
        except Exception:
            import os
            api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY_1")
            self.key_manager = None

        if not api_key:
            st.error("❌ No API key found! Please set GEMINI_API_KEY in your .env file.")
            self.client = None
            return

        self.client = genai.Client(api_key=api_key)

    def create_quiz_prompt(self, transcript: str, num_questions: int, difficulty: str) -> str:
        """Create MCQ-only quiz prompt"""
        
        difficulty_guide = {
            "Easy": "straightforward questions",
            "Medium": "moderate difficulty",
            "Hard": "challenging questions"
        }
        
        guide = difficulty_guide.get(difficulty, "moderate difficulty")
        transcript_limit = min(4000, len(transcript))
        
        return f"""Create {num_questions} multiple choice questions from this transcript.


Transcript:
{transcript[:transcript_limit]}


Return ONLY a JSON array. Format each question EXACTLY like this:
[
  {{"id": 1, "type": "mcq", "question": "What is discussed?", "options": ["First", "Second", "Third", "Fourth"], "correct_answer": "First", "explanation": "Because..."}},
  {{"id": 2, "type": "mcq", "question": "Another question?", "options": ["A", "B", "C", "D"], "correct_answer": "A", "explanation": "Reason..."}}
]


Requirements:
- {num_questions} questions total
- Each "type" must be "mcq"
- Each "options" must be array of 4 strings
- "correct_answer" must match one option EXACTLY
- Keep {guide}
- Return ONLY the JSON array, no other text
"""
    
    def clean_json_response(self, text: str) -> str:
        """Clean and extract JSON from response"""
        # Remove markdown
        text = re.sub(r'```json\s*', '', text)
        text = re.sub(r'```\s*', '', text)
        text = text.strip()
        
        # Extract array
        match = re.search(r'\[[\s\S]*\]', text, re.DOTALL)
        if match:
            json_text = match.group(0)
        else:
            json_text = text
        
        # Fix common issues
        json_text = re.sub(r',(\s*[\]\}])', r'\1', json_text)
        
        return json_text
    
    def generate_quiz(self, transcript: str, num_questions: int = 5,
                     difficulty: str = "Medium") -> Optional[Dict]:
        """Generate MCQ-only quiz"""
        
        if len(transcript) < 100:
            st.error("❌ Transcript too short")
            return None
            # ✅ ADD THIS
        if self.client is None:
            st.error("❌ No API key found! Please set GEMINI_API_KEY in your .env file.")
            return None


        if num_questions > 20:
            num_questions = 20
        
        prompt = self.create_quiz_prompt(transcript, num_questions, difficulty)
        
        # Try each model
        for model_info in self.models:
            try:
                with st.spinner(f"🤖 Generating {num_questions} questions..."):
                    
                    # ✅ NEW: Use client.models.generate_content()
                    response = self.client.models.generate_content(
                        model=model_info['name'],
                        contents=prompt,
                        config=types.GenerateContentConfig(
                            temperature=0.7,
                            top_p=0.95,
                            max_output_tokens=model_info['max_tokens'],
                        )
                    )
                    
                    if response and hasattr(response, 'text'):
                        response_text = f"{response.text}"
                        clean_text = self.clean_json_response(response_text)
                        
                        # Parse JSON
                        try:
                            quiz_array = json.loads(clean_text)
                        except json.JSONDecodeError:
                            # Try to extract individual questions
                            pattern = r'\{[^{}]*"type"\s*:\s*"mcq"[^{}]*\}'
                            matches = re.findall(pattern, clean_text, re.DOTALL)
                            
                            if matches:
                                quiz_array = []
                                for match in matches:
                                    try:
                                        q = json.loads(match)
                                        quiz_array.append(q)
                                    except:
                                        continue
                                
                                if not quiz_array:
                                    continue
                            else:
                                continue
                        
                        # Validate questions
                        if isinstance(quiz_array, list) and len(quiz_array) > 0:
                            valid_questions = []
                            
                            for q in quiz_array:
                                if isinstance(q, dict):
                                    has_all = all(k in q for k in ['question', 'options', 'correct_answer', 'explanation'])
                                    
                                    if has_all and q.get('type') == 'mcq':
                                        opts = q.get('options', [])
                                        if isinstance(opts, list) and len(opts) == 4:
                                            if q['correct_answer'] in opts:
                                                q['id'] = len(valid_questions) + 1
                                                valid_questions.append(q)
                            
                            if len(valid_questions) > 0:
                                st.success(f"✅ Generated {len(valid_questions)} questions successfully!")
                                return {"questions": valid_questions}
                            else:
                                continue
                        else:
                            continue
                        
            except Exception as e:
                error_msg = str(e)
                
                # Handle quota errors - try rotating API key first
                if "quota" in error_msg.lower() or "429" in error_msg or "resource_exhausted" in error_msg.lower():
                    st.warning(f"⚠️ Quota exceeded, switching API key...")
                    if self.key_manager.rotate_key():
                        # ✅ Switched to next key — rebuild client
                        self.client = genai.Client(api_key=self.key_manager.get_current_key())
                        st.info(f"🔑 Switched to backup API key, retrying...")
                        # Retry same model with new key (don't continue to next model yet)
                        try:
                            response = self.client.models.generate_content(
                                model=model_info['name'],
                                contents=prompt,
                                config=types.GenerateContentConfig(
                                    temperature=0.7,
                                    top_p=0.8,
                                    top_k=40,
                                    max_output_tokens=1500,
                                )
                            )
                            if response and response.text:
                                return response.text.strip(), None
                        except:
                            pass
                    time.sleep(1)
                    continue
                elif "api" in error_msg.lower() or "404" in error_msg:
                    st.warning(f"⚠️ API error with {model_info['name']}, trying next model...")
                    time.sleep(1)
                    continue
                else:
                    st.warning(f"⚠️ Error with {model_info['name']}, trying next model...")
                    time.sleep(1)
                    continue

        
        st.error("❌ Failed to generate quiz. Please try again with fewer questions.")
        return None
    
    @staticmethod
    def evaluate_answer(user_answer: str, correct_answer: str, question_type: str) -> bool:
        """Evaluate MCQ answer"""
        if not user_answer or not correct_answer:
            return False
        return user_answer.strip().lower() == correct_answer.strip().lower()
