"""
AI Quiz Generator Service - Final Working Version
Handles Gemini's special response object correctly
"""

import google.generativeai as genai
import streamlit as st
import time
import json
import re
from typing import Optional, Dict

class QuizGenerator:
    """Smart quiz generator with model fallback"""
    
    def __init__(self):
        """Initialize Gemini AI"""
        try:
            self.api_key = st.secrets["GEMINI_API_KEY"]
        except:
            import os
            self.api_key = os.getenv("GEMINI_API_KEY")
        
        genai.configure(api_key=self.api_key)
        
        # EXACT SAME models as notes generator (these are working!)
        self.models = [
            {"name": "gemini-2.5-flash-lite", "limit": "1000/day"},
            {"name": "gemini-2.5-flash", "limit": "250/day"},
            {"name": "gemini-2.0-flash", "limit": "200/day"},
            {"name": "gemini-2.5-pro", "limit": "100/day"}
        ]
    
    def create_quiz_prompt(self, transcript: str, num_questions: int, difficulty: str) -> str:
        """Create quiz prompt - simpler format"""
        return f"""You are a quiz creator. Generate {num_questions} questions from this transcript.

Transcript:
{transcript[:2500]}

Create a JSON array with questions.

Example format:
[
  {{
    "id": 1,
    "type": "mcq",
    "question": "What is the main topic?",
    "options": ["Option 1", "Option 2", "Option 3", "Option 4"],
    "correct_answer": "Option 1",
    "explanation": "Brief explanation"
  }},
  {{
    "id": 2,
    "type": "short_answer",
    "question": "Explain key concept?",
    "correct_answer": "Expected answer",
    "explanation": "Brief explanation"
  }}
]

Generate exactly {num_questions} questions.
Difficulty: {difficulty}
Mix: 60% MCQ, 40% short answer
Return ONLY the JSON array, nothing else.
"""
    
    def generate_quiz(self, transcript: str, num_questions: int = 5, 
                     difficulty: str = "Medium") -> Optional[Dict]:
        """Generate quiz with robust error handling"""
        
        if len(transcript) < 100:
            st.error("❌ Transcript too short (need at least 100 characters)")
            return None
        
        prompt = self.create_quiz_prompt(transcript, num_questions, difficulty)
        
        # Try each model with fallback
        for i, model_info in enumerate(self.models):
            try:
                st.info(f"🤖 Generating quiz with {model_info['name']}... ({model_info['limit']})")
                
                # Initialize model
                model = genai.GenerativeModel(
                    model_info['name'],
                    generation_config={
                        'temperature': 0.7,
                        'top_p': 0.95,
                        'max_output_tokens': 2048,
                    }
                )
                
                # Generate quiz
                response = model.generate_content(prompt)
                
                if response and hasattr(response, 'text'):
                    raw_response = response.text
                    
                    # Check if it's already a list (parsed)
                    if isinstance(raw_response, list):
                        st.info(f"✅ Received pre-parsed list from {model_info['name']}")
                        quiz_array = raw_response
                    else:
                        # It's a string-like object - convert carefully
                        # Use repr() then eval, or use re.sub to extract JSON
                        
                        # Method 1: Try to get the string representation
                        response_text = f"{raw_response}"  # Use f-string formatting instead of str()
                        
                        st.info(f"📝 Response preview: {response_text[:150]}...")
                        
                        # Remove markdown code blocks using regex (safer than .split())
                        # This removes ```json and ``` without calling string methods on the object
                        clean_text = re.sub(r'```json\s*', '', response_text)
                        clean_text = re.sub(r'```\s*$', '', clean_text)
                        clean_text = re.sub(r'^\s*```\s*', '', clean_text)
                        
                        # Remove leading/trailing whitespace
                        clean_text = clean_text.strip()
                        
                        st.info(f"✅ Cleaned response from {model_info['name']}")
                        
                        # Parse JSON
                        try:
                            quiz_array = json.loads(clean_text)
                        except json.JSONDecodeError as e:
                            st.warning(f"⚠️ {model_info['name']} - JSON parse error: {str(e)[:50]}")
                            # Try to extract JSON array using regex
                            match = re.search(r'\[.*\]', clean_text, re.DOTALL)
                            if match:
                                try:
                                    quiz_array = json.loads(match.group(0))
                                except:
                                    continue
                            else:
                                continue
                    
                    # Validate structure
                    if isinstance(quiz_array, list) and len(quiz_array) > 0:
                        # Add IDs if missing
                        for idx, q in enumerate(quiz_array):
                            if isinstance(q, dict):
                                if 'id' not in q:
                                    q['id'] = idx + 1
                        
                        quiz_data = {"questions": quiz_array}
                        st.success(f"✅ Generated {len(quiz_array)} questions successfully!")
                        return quiz_data
                    else:
                        st.warning(f"⚠️ {model_info['name']} returned invalid structure")
                        continue
                else:
                    st.warning(f"⚠️ {model_info['name']} returned empty response")
                    continue
                    
            except Exception as e:
                error_msg = str(e).lower()
                
                if "quota" in error_msg or "resource_exhausted" in error_msg:
                    st.warning(f"⚠️ {model_info['name']} quota exceeded, trying next...")
                else:
                    st.warning(f"⚠️ Error with {model_info['name']}: {str(e)[:100]}")
                continue
                
            time.sleep(0.5)
        
        st.error("❌ All models failed. Try:")
        st.error("• Wait a few minutes (quota reset)")
        st.error("• Use fewer questions (try 3)")  
        st.error("• Check API key validity")
        return None
    
    @staticmethod
    def evaluate_answer(user_answer: str, correct_answer: str, question_type: str) -> bool:
        """Evaluate user's answer"""
        if not user_answer or user_answer.strip() == "":
            return False
        
        if question_type == "mcq":
            return user_answer.strip().lower() == correct_answer.strip().lower()
        else:
            # For short answers - keyword matching
            user_words = set(user_answer.lower().split())
            correct_words = set(correct_answer.lower().split())
            
            # Remove common words
            common_words = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'in', 'on', 'at', 'to', 'for', 'of', 'and', 'or'}
            user_words -= common_words
            correct_words -= common_words
            
            if len(correct_words) == 0:
                return False
            
            # Calculate overlap
            overlap = len(user_words.intersection(correct_words))
            match_ratio = overlap / len(correct_words)
            
            return match_ratio >= 0.5  # 50% keyword match
