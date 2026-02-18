"""
API Key Manager - Rotates between multiple API keys on quota exhaustion
"""
import os
from dotenv import load_dotenv
import streamlit as st

load_dotenv()

class APIKeyManager:
    
    def __init__(self):
        self.keys = self._load_keys()
        self.current_index = 0
    
    def _load_keys(self):
        """Load all available API keys"""
        keys = []
        
        # Try loading from Streamlit secrets first
        try:
            i = 1
            while True:
                key = st.secrets.get(f"GEMINI_API_KEY_{i}")
                if key:
                    keys.append(key)
                    i += 1
                else:
                    break
        except:
            pass
        
        # Fallback to .env
        if not keys:
            i = 1
            while True:
                key = os.getenv(f"GEMINI_API_KEY_{i}")
                if key:
                    keys.append(key)
                    i += 1
                else:
                    break
        
        # Final fallback — try old single key format
        if not keys:
            single = os.getenv("GEMINI_API_KEY")
            if single:
                keys.append(single)
        
        return keys
    
    def get_current_key(self):
        """Get current active API key"""
        if not self.keys:
            return None
        return self.keys[self.current_index]
    
    def rotate_key(self):
        """Switch to next available key"""
        if self.current_index < len(self.keys) - 1:
            self.current_index += 1
            return True  # Successfully rotated
        return False  # No more keys available
    
    def reset(self):
        """Reset to first key"""
        self.current_index = 0
    
    def total_keys(self):
        return len(self.keys)
