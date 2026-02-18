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
    def get_video_metadata_simple(video_id: str) -> tuple:
        """
        Simple metadata using only YouTube thumbnail URL
        This ALWAYS works - no API calls needed
        """
        try:
            # These URLs always work for any valid video
            thumbnail = f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
            
            metadata = {
                'title': f'Video ID: {video_id}',
                'thumbnail': thumbnail,
                'duration': 'Click Extract to get details',
                'channel': 'Loading...',
                'views': '--',
                'upload_date': '--'
            }
            
            return metadata, None
            
        except Exception as e:
            return None, str(e)
    @staticmethod
    def get_video_metadata(video_id):
        """Get video metadata like title, channel, views, etc."""
        try:
            # Method 1: Try YouTube oEmbed API
            url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json"
            
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if title is valid
                title = data.get('title')
                if title and title.strip():
                    metadata = {
                        'title': title,
                        'channel': data.get('author_name', 'Unknown'),
                        'thumbnail': data.get('thumbnail_url', f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"),
                        'duration': 'N/A',
                        'views': 'N/A',
                        'upload_date': 'Unknown'
                    }
                    return metadata, None
            
            # Method 2: Try scraping the page title
            page_url = f"https://www.youtube.com/watch?v={video_id}"
            page_response = requests.get(page_url, timeout=10)
            
            if page_response.status_code == 200:
                # Extract title from page HTML
                import re
                title_match = re.search(r'<title>(.*?)</title>', page_response.text)
                
                if title_match:
                    # YouTube titles are in format: "Video Title - YouTube"
                    full_title = title_match.group(1)
                    # Remove " - YouTube" suffix
                    clean_title = full_title.replace(' - YouTube', '').strip()
                    
                    if clean_title and clean_title != 'YouTube':
                        metadata = {
                            'title': clean_title,
                            'channel': 'Unknown',
                            'thumbnail': f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg",
                            'duration': 'N/A',
                            'views': 'N/A',
                            'upload_date': 'Unknown'
                        }
                        return metadata, None
            
            # Fallback: Return basic metadata
            return {
                'title': f"YouTube Video ({video_id})",
                'channel': 'Unknown',
                'thumbnail': f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg",
                'duration': 'N/A',
                'views': 'N/A',
                'upload_date': 'Unknown'
            }, None
                
        except Exception as e:
            # Return basic fallback
            return {
                'title': f"YouTube Video ({video_id})",
                'channel': 'Unknown',
                'thumbnail': f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg",
                'duration': 'N/A',
                'views': 'N/A',
                'upload_date': 'Unknown'
            }, None



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
