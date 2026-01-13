"""
YouTube Transcript Extractor
EXACT COPY from working reference project
"""

from youtube_transcript_api import YouTubeTranscriptApi
import re
from typing import Optional, Tuple

class TranscriptExtractor:
    """Handles YouTube transcript extraction"""
    
    @staticmethod
    def extract_video_id(url: str) -> Optional[str]:
        """Extract video ID from YouTube URL - EXACT from working project"""
        # Remove any extra parameters first
        url = url.split('&')[0].split('?')[0] if '?' in url else url
        
        patterns = [
            r'(?:v=|/)([0-9A-Za-z_-]{11}).*',
            r'youtu\.be/([0-9A-Za-z_-]{11})',
            r'embed/([0-9A-Za-z_-]{11})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                video_id = match.group(1)
                if len(video_id) == 11:
                    return video_id
        return None
    
    @staticmethod
    def validate_url(url: str) -> Tuple[bool, str]:
        """Validate YouTube URL"""
        if not url or url.strip() == "":
            return False, "Please enter a YouTube URL"
        
        if "youtube" not in url.lower() and "youtu.be" not in url:
            return False, "Invalid YouTube URL"
        
        video_id = TranscriptExtractor.extract_video_id(url)
        if not video_id:
            return False, "Could not extract video ID"
        
        return True, "Valid URL"
    
    @staticmethod
    def get_transcript(video_id: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Get transcript - EXACT method from working reference project
        """
        try:
            # EXACT API usage from working project
            ytt_api = YouTubeTranscriptApi()
            fetched_transcript = ytt_api.fetch(video_id)
            
            # Convert to raw data and format
            raw_data = fetched_transcript.to_raw_data()
            formatted_text = '\n'.join([entry['text'] for entry in raw_data])
            
            return formatted_text, None
            
        except Exception as e:
            return None, f"No captions: {str(e)}"
