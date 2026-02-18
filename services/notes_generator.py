"""
AI Notes Generator Service
Updated to use google.genai (new SDK)
"""

from google import genai
from google.genai import types
import streamlit as st
import time
from typing import Tuple, Optional


class NotesGenerator:
    """Smart Gemini AI service with automatic model fallback"""
    
    def __init__(self):
        # ✅ Try all possible key names in order
        try:
            self.api_key = st.secrets["GEMINI_API_KEY"]
        except:
            import os
            # Try GEMINI_API_KEY first, then fallback to GOOGLE_API_KEY
            self.api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

        if not self.api_key:
            st.error("❌ No API key found! Please set GEMINI_API_KEY in your .env file.")
            return

        self.client = genai.Client(api_key=self.api_key)

        
        # Model priority list (best to fallback)
        self.models = [
            {"name": "gemini-2.5-flash-lite",  "limit": "1000/day", "max_tokens": 8192},  # ✅ Fastest, highest quota
            {"name": "gemini-2.5-flash",       "limit": "250/day",  "max_tokens": 8192},  # ✅ Best performance
            {"name": "gemini-2.0-flash-lite",  "limit": "1000/day", "max_tokens": 8192},  # ✅ Cost efficient
            {"name": "gemini-2.0-flash",       "limit": "200/day",  "max_tokens": 8192},  # ✅ Fallback
            {"name": "gemini-2.5-pro",         "limit": "100/day",  "max_tokens": 8192},  # ✅ Last resort
        ]


    
    def create_notes_prompt(self, transcript: str) -> str:
        """Create structured prompt for notes generation"""
        return f"""You are an expert educational content creator. Generate comprehensive, well-structured study notes from this video transcript.


**Instructions:**
- DO NOT simply summarize or repeat the transcript
- IDENTIFY and EXPLAIN the main concepts, ideas, and insights
- ORGANIZE your response with clear headings
- MAKE complex ideas accessible and understandable
- FOCUS on the "why" and "how" behind the concepts
- HIGHLIGHT key takeaways and practical implications


**Transcript:**
{transcript[:4000]}


**Please provide your analysis in this structure:**


## 🎯 Core Concept
[Main idea/theme in 1-2 sentences]


## 📚 Key Concepts Explained
[Detailed explanation of main concepts - not summary]


## 🔍 Important Insights
[Key insights and deeper understanding points]


## 💡 Practical Takeaways
[What viewers should remember/apply]


## 🎓 Why This Matters
[Broader significance and relevance]
"""
    
    def generate_notes(self, transcript: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Generate AI notes with automatic model fallback
        Returns: (notes_content, error_message)
        """
        if len(transcript) < 50:
            return None, "Transcript too short for meaningful analysis"
        
        prompt = self.create_notes_prompt(transcript)
        
        # Try each model with fallback
        for i, model_info in enumerate(self.models):
            try:
                st.info(f"🤖 AI Engine processing your content...")
                
                # ✅ NEW: Use client.models.generate_content()
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
                    
            except Exception as e:
                error_msg = str(e)
                
                # Handle specific quota errors
                if "quota" in error_msg.lower() or "limit" in error_msg.lower():
                    st.warning(f"⚠️ {model_info['name']} quota exceeded, trying next model...")
                    time.sleep(1)
                    continue
                elif "api" in error_msg.lower():
                    st.warning(f"⚠️ API error with {model_info['name']}, trying next model...")
                    time.sleep(1)
                    continue
                else:
                    st.error(f"❌ Error with {model_info['name']}: {error_msg}")
                    time.sleep(1)
                    continue
        
        return None, "Daily AI quota exhausted. Please try again tomorrow or reduce content length."
