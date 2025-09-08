import streamlit as st
import whisper
import yt_dlp
import tempfile
import os
import re
from youtube_transcript_api import YouTubeTranscriptApi
from datetime import datetime
from gemini_service import GeminiConceptExplainer

# Configure the Streamlit page
st.set_page_config(
    page_title="YouTube Transcript Generator & AI Analyzer",
    page_icon="📝",
    layout="wide"
)

# Initialize session state
if 'transcript' not in st.session_state:
    st.session_state.transcript = ""
if 'explanation' not in st.session_state:
    st.session_state.explanation = ""
if 'model_used' not in st.session_state:
    st.session_state.model_used = ""
if 'video_title' not in st.session_state:
    st.session_state.video_title = ""

# Title and description
st.title("🎥 YouTube Transcript Generator & AI Analyzer")
st.write("Extract transcripts from YouTube videos and get AI-powered concept explanations!")

def extract_video_id(url):
    """Extract video ID from YouTube URL"""
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

@st.cache_resource
def load_whisper_model(model_size="base"):
    """Load Whisper model (cached for better performance)"""
    return whisper.load_model(model_size)

@st.cache_resource
def init_gemini_service():
    """Initialize Gemini AI service (cached)"""
    try:
        return GeminiConceptExplainer()
    except Exception as e:
        st.error(f"Failed to initialize Gemini AI: {str(e)}")
        return None

def get_video_info(video_url):
    """Get video title and info using yt-dlp"""
    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            return info.get('title', 'Unknown Video'), info.get('duration', 0)
    except Exception:
        return 'Unknown Video', 0

def get_existing_transcript(video_url):
    """Get existing captions using NEW API format"""
    try:
        video_id = extract_video_id(video_url)
        if not video_id:
            return None, "Invalid URL"
        
        # NEW API: Create instance and use fetch()
        ytt_api = YouTubeTranscriptApi()
        fetched_transcript = ytt_api.fetch(video_id)
        
        # Convert to raw data and format
        raw_data = fetched_transcript.to_raw_data()
        formatted_text = '\n'.join([entry['text'] for entry in raw_data])
        return formatted_text, "captions"
        
    except Exception as e:
        return None, f"No captions: {str(e)}"

def download_audio(video_url, output_path):
    """Download audio from YouTube video for Whisper processing"""
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': output_path,
        'extractaudio': True,
        'audioformat': 'wav',
        'quiet': True,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])
        return True
    except Exception as e:
        st.error(f"Audio download failed: {str(e)}")
        return False

def transcribe_with_whisper(audio_path, model_size="base"):
    """Transcribe audio using Whisper"""
    try:
        model = load_whisper_model(model_size)
        result = model.transcribe(audio_path)
        return result["text"], "whisper"
    except Exception as e:
        return None, f"Transcription failed: {str(e)}"

# Sidebar Configuration
st.sidebar.title("⚙️ Settings")

# Whisper model selection
whisper_model = st.sidebar.selectbox(
    "Whisper Model Size",
    ["tiny", "base", "small", "medium"],
    index=1,
    help="Larger models are more accurate but slower"
)

# Add AI model info in sidebar
with st.sidebar.expander("🤖 AI Analysis Info"):
    gemini_service = init_gemini_service()
    if gemini_service:
        st.markdown(gemini_service.get_model_status())
    else:
        st.warning("AI analysis unavailable - check API key configuration")

st.sidebar.markdown("---")
st.sidebar.markdown("**Model Performance:**")
st.sidebar.markdown("- **tiny**: Fastest (~1min per 10min video)")
st.sidebar.markdown("- **base**: Recommended balance")
st.sidebar.markdown("- **small**: Better accuracy")
st.sidebar.markdown("- **medium**: Best accuracy (slower)")

# User input section
video_url = st.text_input(
    "🔗 YouTube Video URL",
    placeholder="https://www.youtube.com/watch?v=... or https://youtu.be/...",
    help="Paste any YouTube video URL here"
)

# Show video info if URL is provided
if video_url and extract_video_id(video_url):
    try:
        title, duration = get_video_info(video_url)
        st.info(f"📺 **Video**: {title} ({duration//60}:{duration%60:02d})")
    except:
        pass

# Main processing button
if st.button("🚀 Generate Transcript", type="primary"):
    if video_url:
        # Create progress indicators
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # Get video info
            title, duration = get_video_info(video_url)
            st.session_state.video_title = title
            
            # Step 1: Try existing captions
            status_text.text("🔍 Checking for existing captions...")
            progress_bar.progress(20)
            
            transcript, method = get_existing_transcript(video_url)
            
            if transcript and method == "captions":
                status_text.text("✅ Found existing captions!")
                progress_bar.progress(100)
                
                # Store in session state
                st.session_state.transcript = transcript
                st.session_state.explanation = ""  # Reset explanation
                st.session_state.model_used = ""
                
            else:
                # Step 2: Use Whisper for videos without captions
                status_text.text("🎵 No captions found. Downloading audio...")
                progress_bar.progress(40)
                
                with tempfile.TemporaryDirectory() as temp_dir:
                    audio_path = os.path.join(temp_dir, "audio.%(ext)s")
                    
                    if download_audio(video_url, audio_path):
                        status_text.text("🤖 Transcribing with Whisper AI...")
                        progress_bar.progress(70)
                        
                        # Find the actual downloaded file
                        audio_files = [f for f in os.listdir(temp_dir) if f.startswith("audio")]
                        if audio_files:
                            actual_audio_path = os.path.join(temp_dir, audio_files[0])
                            transcript, method = transcribe_with_whisper(actual_audio_path, whisper_model)
                            
                            if transcript:
                                status_text.text("✅ AI transcription completed!")
                                progress_bar.progress(100)
                                
                                # Store in session state
                                st.session_state.transcript = transcript
                                st.session_state.explanation = ""
                                st.session_state.model_used = ""
                                
                            else:
                                st.error("❌ Failed to transcribe audio")
                                transcript = None
                        else:
                            st.error("❌ Audio file not found after download")
                            transcript = None
                    else:
                        st.error("❌ Failed to download video audio")
                        transcript = None
                
        except Exception as e:
            st.error(f"❌ An error occurred: {str(e)}")
            transcript = None
        finally:
            progress_bar.empty()
            status_text.empty()
            
    else:
        st.error("⚠️ Please enter a YouTube URL")
        transcript = None

# Display results if transcript exists
if st.session_state.transcript:
    transcript = st.session_state.transcript
    
    st.success("🎉 Transcript generated successfully!")
    
    # Create enhanced tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📄 Transcript", "🧠 AI Analysis", "💾 Download", "🔧 Debug"])
    
    with tab1:
        st.subheader("📄 Video Transcript")
        st.text_area("Transcript Content", transcript, height=400, label_visibility="collapsed")
        
        # Enhanced Concept Explanation Button
        st.markdown("---")
        st.markdown("### 🧠 Want to understand the key concepts?")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🧠 Explain Core Concepts", type="secondary", use_container_width=True):
                gemini_service = init_gemini_service()
                if gemini_service:
                    with st.spinner("🤖 AI is analyzing the video concepts..."):
                        explanation, model_used = gemini_service.explain_concepts(transcript)
                        st.session_state.explanation = explanation
                        st.session_state.model_used = model_used
                        st.rerun()
                else:
                    st.error("AI service unavailable. Please check configuration.")
        
        # Preview of what AI analysis provides
        with st.expander("💡 What you'll get from AI Analysis"):
            st.markdown("""
            **AI-Powered Concept Explanation includes:**
            - 🎯 **Core Concept**: Main theme identification  
            - 📚 **Key Concepts**: Detailed explanations (not just summaries)
            - 🔍 **Important Insights**: Deeper understanding points
            - 💡 **Practical Takeaways**: Actionable insights
            - 🎓 **Why This Matters**: Broader significance and relevance
            """)
    
    with tab2:
        st.subheader("🧠 AI-Powered Concept Analysis")
        
        if st.session_state.explanation:
            # Show which model was used
            if st.session_state.model_used and st.session_state.model_used != "none":
                st.success(f"✨ Analysis completed using **{st.session_state.model_used}**")
            
            # Display explanation in a nice format
            st.markdown(st.session_state.explanation)
            
            # Action buttons
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔄 Regenerate Analysis", type="secondary"):
                    gemini_service = init_gemini_service()
                    if gemini_service:
                        with st.spinner("🤖 Regenerating analysis..."):
                            explanation, model_used = gemini_service.explain_concepts(transcript)
                            st.session_state.explanation = explanation
                            st.session_state.model_used = model_used
                            st.rerun()
                    else:
                        st.error("AI service unavailable")
            
            with col2:
                # Copy explanation to clipboard (informational)
                st.info("💡 Use the Download tab to save the full analysis")
                
        else:
            st.info("👈 Click **'Explain Core Concepts'** in the Transcript tab to get AI analysis")
            
            st.markdown("### 🚀 What makes our AI analysis special:")
            st.markdown("""
            - **🎯 Concept-Focused**: Identifies and explains key ideas, not just summarization
            - **📚 Educational**: Makes complex topics accessible and understandable  
            - **💡 Insightful**: Provides deeper analysis and practical takeaways
            - **🔄 Reliable**: Smart fallback across 4 different Gemini models
            - **⚡ Fast**: Optimized prompts for quick, quality results
            """)
            
            # Model information
            gemini_service = init_gemini_service()
            if gemini_service:
                st.markdown("### 🤖 Available AI Models:")
                st.markdown("""
                1. **Gemini 2.5 Flash-Lite** - 1000 requests/day (Primary)
                2. **Gemini 2.5 Flash** - 250 requests/day (Fallback)  
                3. **Gemini 2.0 Flash** - 200 requests/day (Fallback)
                4. **Gemini 2.5 Pro** - 100 requests/day (Final fallback)
                """)
    
    with tab3:
        st.subheader("💾 Download Options")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📄 Transcript Only")
            video_id = extract_video_id(video_url) if video_url else "transcript"
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            st.download_button(
                "📥 Download Transcript (TXT)",
                transcript,
                file_name=f"transcript_{video_id}_{timestamp}.txt",
                mime="text/plain",
                use_container_width=True
            )
        
        with col2:
            st.markdown("#### 📊 Complete Analysis")
            if st.session_state.explanation and st.session_state.explanation != "":
                # Create combined analysis file
                combined_content = f"""YouTube Video Analysis Report
{'='*50}

VIDEO INFORMATION:
Title: {st.session_state.video_title}
URL: {video_url}
Analysis Date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
AI Model Used: {st.session_state.model_used}

TRANSCRIPT:
{'-'*20}
{transcript}

AI CONCEPT ANALYSIS:
{'-'*20}
{st.session_state.explanation}

{'='*50}
Generated by: YouTube Transcript Generator & AI Analyzer
"""
                
                st.download_button(
                    "📥 Download Full Analysis (TXT)", 
                    combined_content,
                    file_name=f"analysis_{video_id}_{timestamp}.txt",
                    mime="text/plain",
                    use_container_width=True
                )
            else:
                st.info("Generate AI analysis first to download the complete report")
    
    with tab4:
        st.subheader("🔧 Debug Information")
        
        video_id = extract_video_id(video_url) if video_url else None
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Video Information:**")
            st.write(f"**Title:** {st.session_state.video_title}")
            st.write(f"**Video ID:** {video_id}")
            st.write(f"**URL Valid:** {'✅' if video_id else '❌'}")
            
        with col2:
            st.markdown("**Processing Information:**")
            st.write(f"**Transcript Length:** {len(transcript):,} characters")
            st.write(f"**Word Count:** ~{len(transcript.split()):,} words")
            if st.session_state.model_used:
                st.write(f"**AI Model Used:** {st.session_state.model_used}")
            
        if st.session_state.explanation:
            st.markdown("**AI Analysis Stats:**")
            st.write(f"**Analysis Length:** {len(st.session_state.explanation):,} characters")
            st.write(f"**Analysis Available:** ✅")
        
        # Technical details
        with st.expander("🔍 Technical Details"):
            st.json({
                "video_id": video_id,
                "transcript_chars": len(transcript),
                "transcript_words": len(transcript.split()),
                "ai_analysis_available": bool(st.session_state.explanation),
                "ai_model_used": st.session_state.model_used,
                "whisper_model": whisper_model,
                "timestamp": datetime.now().isoformat()
            })

# Enhanced help sections
with st.expander("📖 Complete Usage Guide"):
    st.markdown("""
    ### 🚀 Basic Workflow:
    1. **Paste YouTube URL** → Get transcript (captions or AI-generated)
    2. **Click "Explain Core Concepts"** → Get intelligent AI analysis  
    3. **Download** transcript, analysis, or both
    
    ### 🧠 AI Analysis Features:
    - **🎯 Concept Identification**: Finds main themes and ideas
    - **📚 Detailed Explanations**: Goes beyond summarization
    - **💡 Practical Insights**: Actionable takeaways and applications
    - **🔄 Smart Fallback**: Automatically uses the best available AI model
    - **⚡ Fast Processing**: Optimized for speed and quality
    
    ### 🤖 AI Model System:
    - **Primary**: Gemini 2.5 Flash-Lite (1000/day)
    - **Fallback 1**: Gemini 2.5 Flash (250/day)
    - **Fallback 2**: Gemini 2.0 Flash (200/day)  
    - **Final**: Gemini 2.5 Pro (100/day)
    
    ### 📊 What Makes This Special:
    - Combines **transcript extraction** with **intelligent analysis**
    - Provides **concept explanations**, not just summaries
    - **Reliable processing** with multiple AI model fallbacks
    - **Professional outputs** ready for research or learning
    """)

with st.expander("🔧 Troubleshooting"):
    st.markdown("""
    ### Common Issues & Solutions:
    
    **Transcript Generation:**
    - **Slow processing**: Try smaller Whisper model (tiny/base)
    - **Download fails**: Video may be private/restricted
    - **Memory errors**: Use 'tiny' model for very long videos
    - **No captions found**: App automatically uses AI transcription
    
    **AI Analysis:**
    - **Analysis fails**: App tries multiple models automatically
    - **"Quota exceeded"**: System switches to next available model
    - **Empty analysis**: Check if transcript is long enough (>50 characters)
    
    **General:**
    - **App running slow**: Clear browser cache and refresh
    - **Download issues**: Try right-click → Save As
    - **URL not working**: Ensure it's a valid YouTube URL
    """)

# Footer with enhanced information
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        <p>🔥 <strong>Enhanced YouTube Analysis Platform</strong></p>
        <p>💡 Powered by Streamlit + OpenAI Whisper + Google Gemini AI</p>
        <p>🚀 Transcript Generation + Intelligent Concept Analysis</p>
        <p>🆓 Completely Free • 🔒 No Data Stored • ⚡ Fast Processing</p>
    </div>
    """, 
    unsafe_allow_html=True
)

# Usage statistics (optional - you can remove this if not needed)
if st.session_state.transcript:
    st.markdown(
        f"""
        <div style='text-align: center; color: #888; font-size: 0.8em; margin-top: 20px;'>
            Session Stats: {len(st.session_state.transcript.split())} words transcribed
            {f"• AI analysis completed with {st.session_state.model_used}" if st.session_state.explanation else ""}
        </div>
        """, 
        unsafe_allow_html=True
    )
