"""
AI Notes Generator Service
EXACT COPY from working reference project
"""

import google.generativeai as genai
import streamlit as st
import time
from typing import Tuple, Optional

class NotesGenerator:
    """Smart Gemini AI service with automatic model fallback"""
    
    def __init__(self):
        """Initialize Gemini AI"""
        # Try to get API key from Streamlit secrets first
        try:
            self.api_key = st.secrets["GEMINI_API_KEY"]
        except:
            import os
            self.api_key = os.getenv("GEMINI_API_KEY")
        
        genai.configure(api_key=self.api_key)
        
        # Model priority list (best to fallback) - EXACT from reference
        self.models = [
            {"name": "gemini-2.5-flash-lite", "limit": "1000/day"},
            {"name": "gemini-2.5-flash", "limit": "250/day"},
            {"name": "gemini-2.0-flash", "limit": "200/day"},
            {"name": "gemini-2.5-pro", "limit": "100/day"}
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
                st.info(f"🤖 Analyzing with {model_info['name']}... ({model_info['limit']})")
                
                # Initialize model
                model = genai.GenerativeModel(model_info['name'])
                
                # Generate notes
                response = model.generate_content(
                    prompt,
                    generation_config={
                        'temperature': 0.7,
                        'top_p': 0.8,
                        'top_k': 40,
                        'max_output_tokens': 1500,
                    }
                )
                
                if response and response.text:
                    return response.text.strip(), None
                    
            except Exception as e:
                error_msg = str(e)
                
                # Handle specific quota errors
                if "quota" in error_msg.lower() or "limit" in error_msg.lower():
                    st.warning(f"⚠️ {model_info['name']} quota exceeded, trying next model...")
                    continue
                elif "api" in error_msg.lower():
                    st.warning(f"⚠️ API error with {model_info['name']}, trying next model...")
                    continue
                else:
                    st.error(f"❌ Error with {model_info['name']}: {error_msg}")
                    continue
                
                # Brief delay between attempts
                time.sleep(1)
        
        return None, "All Gemini models are currently unavailable. Please try again later."
