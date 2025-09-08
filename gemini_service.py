import google.generativeai as genai
import streamlit as st
import time
from typing import Tuple, Optional

class GeminiConceptExplainer:
    """Smart Gemini AI service with automatic model fallback"""
    
    def __init__(self):
        self.api_key = st.secrets["GEMINI_API_KEY"]
        genai.configure(api_key=self.api_key)
        
        # Model priority list (best to fallback)
        self.models = [
            {"name": "gemini-2.5-flash-lite", "limit": "1000/day"},
            {"name": "gemini-2.5-flash", "limit": "250/day"}, 
            {"name": "gemini-2.0-flash", "limit": "200/day"},
            {"name": "gemini-2.5-pro", "limit": "100/day"}
        ]
        
    def create_concept_prompt(self, transcript: str) -> str:
        """Create structured prompt for concept explanation"""
        return f"""
You are an expert content analyst. Analyze this video transcript and explain the core concepts in a clear, structured way.

**Instructions:**
- DO NOT simply summarize or repeat the transcript
- IDENTIFY and EXPLAIN the main concepts, ideas, and insights
- ORGANIZE your response with clear headings
- MAKE complex ideas accessible and understandable
- FOCUS on the "why" and "how" behind the concepts
- HIGHLIGHT key takeaways and practical implications

**Transcript:**
{transcript[:4000]}  # Limit for API efficiency

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

    def explain_concepts(self, transcript: str) -> Tuple[str, str]:
        """
        Explain video concepts with automatic model fallback
        Returns: (explanation, model_used)
        """
        
        if len(transcript) < 50:
            return "❌ Transcript too short for meaningful analysis.", "none"
        
        prompt = self.create_concept_prompt(transcript)
        
        for i, model_info in enumerate(self.models):
            try:
                st.info(f"🤖 Analyzing with {model_info['name']}... ({model_info['limit']})")
                
                # Initialize model
                model = genai.GenerativeModel(model_info['name'])
                
                # Generate explanation
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
                    return response.text.strip(), model_info['name']
                    
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
        
        return "❌ All Gemini models are currently unavailable. Please try again later.", "none"
    
    def get_model_status(self) -> str:
        """Display current model availability info"""
        return """
        **🤖 AI Model Fallback System:**
        1. **Gemini 2.5 Flash-Lite** (1000 requests/day) - Fastest
        2. **Gemini 2.5 Flash** (250 requests/day) - Multimodal  
        3. **Gemini 2.0 Flash** (200 requests/day) - Advanced
        4. **Gemini 2.5 Pro** (100 requests/day) - Highest Quality
        """
