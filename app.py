"""
AI-Powered YouTube Learning Platform
Final Year Project - Complete Implementation
"""

import streamlit as st
from dotenv import load_dotenv
import os
import sys

# Add paths
sys.path.append(os.path.dirname(__file__))

from utils.transcript_extractor import TranscriptExtractor
from services.notes_generator import NotesGenerator
from services.quiz_generator import QuizGenerator
from utils.pdf_generator import PDFGenerator

# Load environment
load_dotenv()


# ========== SESSION STATE INITIALIZATION ==========
# Initialize current_page for navigation


# Add these to your existing session state init block
if 'youtube_url' not in st.session_state:
    st.session_state.youtube_url = ''
if 'video_metadata' not in st.session_state:
    st.session_state.video_metadata = None
if 'transcript_stats' not in st.session_state:
    st.session_state.transcript_stats = None

if 'current_page' not in st.session_state:
    st.session_state.current_page = "home"

# Initialize page for main content routing
if 'page' not in st.session_state:
    st.session_state.page = "home"
    
# Initialize data storage
if 'transcript' not in st.session_state:
    st.session_state.transcript = None
    
if 'video_id' not in st.session_state:
    st.session_state.video_id = None
    
if 'video_url' not in st.session_state:
    st.session_state.video_url = None
    
if 'notes' not in st.session_state:
    st.session_state.notes = None
    
if 'quiz_data' not in st.session_state:
    st.session_state.quiz_data = None
    
if 'user_answers' not in st.session_state:
    st.session_state.user_answers = {}
    
if 'quiz_submitted' not in st.session_state:
    st.session_state.quiz_submitted = False


# Page configuration
st.set_page_config(
    page_title="YouTube Learning Platform",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ========== ENHANCED CSS WITH BEAUTIFUL COLORS ==========
st.markdown("""
<style>
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Better spacing */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Feature box styling */
    div[data-testid="column"] {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 2rem 1.5rem;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07);
        transition: all 0.3s ease;
    }
    
    div[data-testid="column"]:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 15px rgba(0, 0, 0, 0.15);
    }
    
    /* Specific feature card colors */
    div[data-testid="column"]:nth-child(1) {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    div[data-testid="column"]:nth-child(2) {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
    }
    
    div[data-testid="column"]:nth-child(3) {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        color: white;
    }
    
    /* Make text white in feature cards */
    div[data-testid="column"] h3,
    div[data-testid="column"] p,
    div[data-testid="column"] div {
        color: white !important;
    }
    
    /* Title styling */
    h1 {
        color: #2d3748;
        font-weight: 800;
    }
    
    h2 {
        color: #4a5568;
        font-weight: 700;
    }
    
    /* Button styling */
    .stButton>button {
        border-radius: 10px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }
    
    /* Make emojis bigger in feature cards */
    div[data-testid="column"] h3::before {
        font-size: 1.5em;
        margin-right: 0.3em;
    }
    
    /* Text shadow for better readability */
    div[data-testid="column"] h3 {
        text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.2);
    }
    
    /* Video preview card styling */
    div[data-testid="stImage"] {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }

    /* Metadata section styling */
    div[data-testid="column"] p {
        line-height: 1.8;
    }

    /* Better spacing for video preview */
    .stMarkdown h4 {
        margin-bottom: 1rem;
        color: #4a5568;
    }
    
    /* Stats section styling in video preview */
    div[data-testid="metric-container"] {
        background: rgba(255, 255, 255, 0.1);
        padding: 0.5rem;
        border-radius: 8px;
    }
    
    /* Enhanced Sidebar Styling */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f5f7fa 0%, #e8ecf1 100%);
    }

    /* Sidebar buttons */
    section[data-testid="stSidebar"] .stButton button {
        background: white;
        border: 2px solid #e0e0e0;
        border-radius: 8px;
        padding: 0.5rem;
        transition: all 0.3s ease;
    }

    section[data-testid="stSidebar"] .stButton button:hover {
        border-color: #667eea;
        transform: translateX(5px);
        box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
    }

    /* Active page indicators */
    section[data-testid="stSidebar"] .element-container:has(.stSuccess) {
        background: rgba(102, 126, 234, 0.1);
        border-left: 4px solid #667eea;
        padding: 0.5rem;
        margin: 0.5rem 0;
        border-radius: 5px;
    }

    /* Progress tracker styling */
    section[data-testid="stSidebar"] .stProgress {
        height: 10px;
    }

    /* Sidebar headings */
    section[data-testid="stSidebar"] h3 {
        color: #4a5568;
        font-size: 1rem;
        font-weight: 700;
        margin-top: 1rem;
    }
    
    /* ========== NOTES PAGE STYLING ========== */
    
    /* Notes container */
    .notes-container {
        background: white;
        border-radius: 15px;
        padding: 2rem;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        margin: 1rem 0;
    }
    
    /* Notes headings */
    .notes-container h1 {
        color: #667eea;
        font-size: 2rem;
        margin-top: 2rem;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 3px solid #667eea;
    }
    
    .notes-container h2 {
        color: #764ba2;
        font-size: 1.5rem;
        margin-top: 1.5rem;
        margin-bottom: 0.8rem;
        padding-left: 1rem;
        border-left: 4px solid #f093fb;
    }
    
    .notes-container h3 {
        color: #4facfe;
        font-size: 1.2rem;
        margin-top: 1rem;
        margin-bottom: 0.6rem;
    }
    
    /* Notes paragraphs */
    .notes-container p {
        line-height: 1.8;
        color: #2d3748;
        margin-bottom: 1rem;
        text-align: justify;
    }
    
    /* Notes lists */
    .notes-container ul, .notes-container ol {
        margin-left: 2rem;
        margin-bottom: 1rem;
        line-height: 1.8;
    }
    
    .notes-container li {
        margin-bottom: 0.5rem;
        color: #4a5568;
    }
    
    /* Code blocks */
    .notes-container code {
        background: #f7fafc;
        padding: 0.2rem 0.5rem;
        border-radius: 4px;
        color: #e53e3e;
        font-family: 'Courier New', monospace;
        font-size: 0.9rem;
    }
    
    .notes-container pre {
        background: #2d3748;
        color: #f7fafc;
        padding: 1rem;
        border-radius: 8px;
        overflow-x: auto;
        margin: 1rem 0;
    }
    
    .notes-container pre code {
        background: transparent;
        color: #f7fafc;
        padding: 0;
    }
    
    /* Blockquotes */
    .notes-container blockquote {
        border-left: 4px solid #4facfe;
        padding-left: 1rem;
        margin: 1rem 0;
        color: #4a5568;
        font-style: italic;
        background: #f0f9ff;
        padding: 1rem;
        border-radius: 0 8px 8px 0;
    }
    
    /* Tables */
    .notes-container table {
        width: 100%;
        border-collapse: collapse;
        margin: 1rem 0;
    }
    
    .notes-container th {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.75rem;
        text-align: left;
        font-weight: 600;
    }
    
    .notes-container td {
        padding: 0.75rem;
        border-bottom: 1px solid #e2e8f0;
    }
    
    .notes-container tr:hover {
        background: #f7fafc;
    }
    
    /* Strong/Bold text */
    .notes-container strong {
        color: #2d3748;
        font-weight: 700;
    }
    
    /* Emphasis/Italic */
    .notes-container em {
        color: #4a5568;
        font-style: italic;
    }
    
    /* Section dividers */
    .notes-container hr {
        border: none;
        border-top: 2px solid #e2e8f0;
        margin: 2rem 0;
    }
    
    /* Notes action buttons container */
    .notes-action-card {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        text-align: center;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)



# ==================== ENHANCED SIDEBAR ====================
with st.sidebar:
    # Sidebar Header
    st.markdown("""
    <div style='text-align: center; padding: 1rem 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                border-radius: 10px; margin-bottom: 1rem;'>
        <h2 style='color: white; margin: 0;'>🎓 Learning Hub</h2>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ========== NAVIGATION SECTION (FIXED VERSION) ==========
    st.markdown("### 📍 Navigation")
    st.markdown("")

    # Custom button styling with BLACK text
    st.markdown("""
    <style>
    div[data-testid="stButton"] button {
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        padding: 0.8rem 1rem !important;
        border-radius: 10px !important;
        color: #000000 !important;  /* Black text */
    }

    /* Override disabled button styling */
    div[data-testid="stButton"] button:disabled {
        opacity: 0.5;
        background-color: #e0e0e0 !important;
        color: #666666 !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # HOME BUTTON - Always visible
    if st.session_state.page == "home":
        st.markdown("""
        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    padding: 1rem; border-radius: 10px; margin-bottom: 0.5rem;
                    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);'>
            <p style='color: #000000; margin: 0; font-size: 1.2rem; font-weight: 700;'>
                🏠 Home <span style='font-size: 0.9rem;'>← You are here</span>
            </p>
        </div>
        """, unsafe_allow_html=True)
    else:
        if st.button("🏠 Home", key="nav_home", use_container_width=True, type="primary"):
            st.session_state.page = "home"
            st.rerun()

    # NOTES BUTTON - Enable when transcript exists
    if st.session_state.transcript:
        # Show as gradient box if on notes page
        if st.session_state.page == "notes":
            notes_status = "✅" if st.session_state.notes else ""
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                        padding: 1rem; border-radius: 10px; margin-bottom: 0.5rem;
                        box-shadow: 0 4px 12px rgba(240, 147, 251, 0.4);'>
                <p style='color: #000000; margin: 0; font-size: 1.2rem; font-weight: 700;'>
                    📝 Notes {notes_status} <span style='font-size: 0.9rem;'>← You are here</span>
                </p>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Show as clickable button
            notes_status = "✅" if st.session_state.notes else ""
            if st.button(f"📝 Notes {notes_status}", key="nav_notes", use_container_width=True, type="primary"):
                st.session_state.page = "notes"
                st.rerun()
    else:
        # Show disabled state
        st.button("📝 Notes (Transcript needed)", key="nav_notes_disabled", 
                use_container_width=True, disabled=True)

    # QUIZ BUTTON - Enable when transcript exists
    if st.session_state.transcript:
        # Show as gradient box if on quiz pages
        if st.session_state.page in ["quiz_setup", "quiz"]:
            quiz_status = "✅" if st.session_state.quiz_data else ""
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
                        padding: 1rem; border-radius: 10px; margin-bottom: 0.5rem;
                        box-shadow: 0 4px 12px rgba(79, 172, 254, 0.4);'>
                <p style='color: #000000; margin: 0; font-size: 1.2rem; font-weight: 700;'>
                    📊 Quiz Setup {quiz_status} <span style='font-size: 0.9rem;'>← You are here</span>
                </p>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Show as clickable button
            quiz_status = "✅" if st.session_state.quiz_data else ""
            if st.button(f"📊 Quiz Setup {quiz_status}", key="nav_quiz", use_container_width=True, type="primary"):
                st.session_state.page = "quiz_setup"
                st.rerun()
    else:
        # Show disabled state
        st.button("📊 Quiz Setup (Transcript needed)", key="nav_quiz_disabled",
                use_container_width=True, disabled=True)

    st.markdown("---")



    
    # ========== PROGRESS TRACKER ==========
    st.markdown("### 📈 Progress Tracker")
    
    # Calculate completion percentage
    progress_items = [
        ("Transcript", st.session_state.transcript is not None),
        ("Notes", st.session_state.notes is not None),
        ("Quiz", st.session_state.quiz_data is not None)
    ]
    
    completed = sum(1 for _, status in progress_items if status)
    total = len(progress_items)
    progress_percent = (completed / total) * 100
    
    # Progress bar
    st.progress(progress_percent / 100)
    st.markdown(f"**{completed}/{total} Complete** ({progress_percent:.0f}%)")
    
    # Individual progress items
    for item_name, is_complete in progress_items:
        icon = "✅" if is_complete else "⏳"
        status_text = "Done" if is_complete else "Pending"
        st.markdown(f"{icon} **{item_name}:** {status_text}")
    
    st.markdown("---")
    
    # ========== QUICK ACTIONS ==========
    st.markdown("### ⚡ Quick Actions")
    
    # Generate Notes button
    if st.session_state.transcript and not st.session_state.notes:
        if st.button("✨ Generate Notes", type="primary", use_container_width=True):
            st.session_state.page = 'notes'
            st.rerun()
    elif st.session_state.notes:
        st.info("✅ Notes already generated")
    else:
        st.warning("⚠️ Extract transcript first")
    
    # Generate Quiz button
    if st.session_state.transcript and not st.session_state.quiz_data:
        if st.button("🎯 Generate Quiz", type="primary", use_container_width=True):
            st.session_state.page = 'quiz_setup'
            st.rerun()
    elif st.session_state.quiz_data:
        st.info("✅ Quiz already generated")
    else:
        st.warning("⚠️ Extract transcript first")
    
    st.markdown("---")
    
    # ========== VIDEO INFO (if available) ==========
    if st.session_state.video_id:
        st.markdown("### 📺 Current Video")
        st.markdown(f"**ID:** `{st.session_state.video_id}`")
        
        if st.session_state.transcript:
            word_count = len(st.session_state.transcript.split())
            st.markdown(f"**Words:** {word_count:,}")
        
        # Clear all button
        if st.button("🗑️ Clear All Data", use_container_width=True):
            st.session_state.transcript = None
            st.session_state.video_id = None
            st.session_state.video_url = None
            st.session_state.notes = None
            st.session_state.quiz_data = None
            st.session_state.user_answers = {}
            st.session_state.quiz_submitted = False
            st.session_state.page = 'home'
            st.rerun()
    
    st.markdown("---")
    
    # ========== FOOTER ==========
    st.markdown("""
    <div style='text-align: center; color: #666; font-size: 0.8rem; padding: 1rem 0;'>
        <p>💡 <b>Tip:</b> Use sidebar to navigate</p>
        <p>🎓 Final Year Project 2025-26</p>
    </div>
    """, unsafe_allow_html=True)

# ==================== HOME PAGE ====================
if st.session_state.page == 'home':

    # ========== HERO SECTION ==========
    st.markdown("# 🎓 YouTube Learning Platform")
    st.markdown("### Transform Any YouTube Video Into Learning Material")
    st.markdown("---")
    st.markdown("")

    # ========== FEATURE SHOWCASE ==========
    st.markdown("## ✨ Key Features")
    st.markdown("")
    col1, col2, col3 = st.columns(3, gap="medium")
    with col1:
        st.markdown("### 📝 Smart Transcription")
        st.markdown("Get instant captions or transcription using **YouTube Transcript API** for YouTube video")
    with col2:
        st.markdown("### 🧠 AI Concept Analysis")
        st.markdown("Deep concept explanations powered by **AI** with intelligent fallback system")
    with col3:
        st.markdown("### ✅ AI Quiz Generation")
        st.markdown("AI-generated quizzes with **multiple choice** questions to test understanding")

    st.markdown("")
    st.markdown("---")
    # Big highlighted URL input section
    st.markdown("""
    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 2rem; border-radius: 16px;
                box-shadow: 0 6px 20px rgba(102,126,234,0.4);
                margin: 1rem 0 1.5rem 0;'>
        <h2 style='color: white; margin: 0 0 0.5rem 0; font-size: 1.6rem;'>
            🎬 Enter YouTube Video URL
        </h2>
        <p style='color: rgba(255,255,255,0.85); margin: 0; font-size: 1rem;'>
            Paste any YouTube link below to extract transcript, generate notes and quiz
        </p>
    </div>
    """, unsafe_allow_html=True)

    youtube_url = st.text_input(
        "Paste YouTube URL here:",
        value=st.session_state.youtube_url,
        placeholder="https://www.youtube.com/watch?v=...",
        key="url_input",
        label_visibility="collapsed"
    )

    # Save URL to session state whenever it changes
    if youtube_url != st.session_state.youtube_url:
        st.session_state.youtube_url = youtube_url

    # ========== VIDEO PREVIEW SECTION ==========
    if youtube_url:
        is_valid, message = TranscriptExtractor.validate_url(youtube_url)
        if is_valid:
            video_id = TranscriptExtractor.extract_video_id(youtube_url)
            with st.spinner("🔍 Loading video preview..."):
                metadata, error = TranscriptExtractor.get_video_metadata(video_id)
            if metadata and not error:
                st.session_state.video_metadata = metadata
                st.markdown("#### 🎬 Video Preview")
                # ✅ Full-width thumbnail, no metadata section
                st.image(metadata['thumbnail'], use_column_width=True)
                st.markdown("---")
            else:
                st.warning("⚠️ Could not load video preview, but you can still extract the transcript.")
        else:
            st.error(f"❌ {message}")

    st.markdown("")

    # ========== EXTRACT BUTTON SECTION ==========
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔍 Extract Transcript", type="primary", use_container_width=True):
            if not youtube_url:
                st.error("⚠️ Please enter a YouTube URL")
            else:
                is_valid, message = TranscriptExtractor.validate_url(youtube_url)
                if not is_valid:
                    st.error(f"❌ {message}")
                else:
                    video_id = TranscriptExtractor.extract_video_id(youtube_url)
                    st.info(f"🎬 Video ID: `{video_id}`")
                    with st.spinner("🔄 Extracting transcript..."):
                        transcript, error = TranscriptExtractor.get_transcript(video_id)
                    if transcript:
                        st.session_state.transcript = transcript
                        st.session_state.video_id = video_id
                        st.session_state.video_url = youtube_url
                        # ✅ Save stats to session state
                        st.session_state.transcript_stats = {
                            'words': len(transcript.split()),
                            'chars': len(transcript),
                            'duration': f"~{len(transcript.split())//150} min"
                        }
                        st.success("✅ Transcript extracted successfully!")
                        st.rerun()
                    else:
                        st.error(f"❌ {error}")

    with col2:
        if st.button("🔄 Clear All", type="primary",use_container_width=True):
            st.session_state.transcript = None
            st.session_state.video_id = None
            st.session_state.notes = None
            st.session_state.quiz_data = None
            st.session_state.youtube_url = ''      # ✅ Also clear saved URL
            st.session_state.transcript_stats = None
            st.rerun()

    # ✅ Show transcript stats persistently from session_state
    if st.session_state.transcript:
        stats = st.session_state.transcript_stats
        if stats:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Words", stats['words'])
            with col2:
                st.metric("Characters", stats['chars'])
            with col3:
                st.metric("Duration", stats['duration'])
        st.success("✅ Transcript extracted! Use sidebar to navigate.")
        st.info("👈 **Use sidebar to generate Notes or Quiz!**")
        st.markdown("---")
        with st.expander("📄 View Transcript", expanded=False):
            st.text_area("Transcript Content", st.session_state.transcript, height=300, disabled=True, label_visibility="collapsed")



# ==================== NOTES PAGE ====================
elif st.session_state.page == 'notes':
    st.markdown("# 📝 AI-Generated Notes")
    st.markdown("### Comprehensive study material generated from your video")
    st.markdown("---")
    
    if not st.session_state.transcript:
        st.warning("⚠️ Please extract transcript first!")
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("🏠 Go to Home", use_container_width=True, type="primary"):
                st.session_state.page = 'home'
                st.rerun()
    else:
        if not st.session_state.notes:
            # Generate Notes Section
            st.info("💡 Click the button below to generate comprehensive AI-powered notes from your transcript")
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("✨ Generate AI Notes", type="primary", use_container_width=True, key="gen_notes_btn"):
                    with st.spinner("🤖 AI is analyzing the content and generating comprehensive notes..."):
                        with st.status("Processing...", expanded=True) as status:
                            st.write("📊 Analyzing transcript structure...")
                            st.write("🧠 Extracting key concepts...")
                            st.write("📝 Formatting notes...")
                            
                            notes_gen = NotesGenerator()
                            notes, error = notes_gen.generate_notes(st.session_state.transcript)
                            
                            if notes:
                                st.session_state.notes = notes
                                status.update(label="✅ Notes generated successfully!", state="complete")
                                st.rerun()
                            else:
                                status.update(label="❌ Generation failed", state="error")
                                st.error(f"Error: {error}")
                                st.info("💡 Try again or check your API key configuration")
        else:
            # Display Generated Notes
            st.success("✅ Notes generated successfully! Review and download below.")
            st.markdown("---")
            
            # ========== ONLY 3 ACTION BUTTONS - CLEAN VERSION ==========
            st.markdown("## 📥 Download Options")
            st.markdown("")

            col1, col2, col3 = st.columns(3, gap="large")

            with col1:
                # ✅ CHANGED: Copy button replaced with Regenerate button
                if st.button("🔄 Regenerate Notes", use_container_width=True, type="primary", key="regen_btn"):
                    st.session_state.notes = None
                    st.rerun()

            with col2:
                st.download_button(
                    label="📥 Download TXT",
                    data=st.session_state.notes,
                    file_name=f"notes_{st.session_state.video_id}.txt",
                    mime="text/plain",
                    type="primary",
                    use_container_width=True,
                    key="download_txt_btn"
                )

            with col3:
                try:
                    pdf_buffer = PDFGenerator.generate_notes_pdf(
                        st.session_state.notes,
                        st.session_state.video_url,
                        st.session_state.video_id
                    )
                    
                    st.download_button(
                        label="📄 Download PDF",
                        data=pdf_buffer,
                        file_name=f"notes_{st.session_state.video_id}.pdf",
                        mime="application/pdf",
                        type="primary",
                        use_container_width=True,
                        key="download_pdf_btn"
                    )
                except Exception as e:
                    st.error(f"PDF error: {str(e)}")

            st.markdown("---")
            
            # Display notes with enhanced formatting
            st.markdown("## 📖 Your Study Notes")
            
            # Create tabs for different views
            tab1, tab2 = st.tabs(["📝 Formatted View", "📄 Raw Markdown"])
            
            with tab1:
                # Enhanced formatted view
                st.markdown('<div class="notes-container">', unsafe_allow_html=True)
                st.markdown(st.session_state.notes, unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            
            with tab2:
                # Raw markdown view
                st.code(st.session_state.notes, language="markdown")
            
            # Back to home button at bottom
            st.markdown("---")
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                if st.button("🏠 Back to Home",type="primary", use_container_width=True):
                    st.session_state.page = 'home'
                    st.rerun()

# ==================== QUIZ SETUP PAGE (FIXED BLACK TEXT) ====================
elif st.session_state.page == 'quiz_setup':
    st.markdown("# 🧪 AI Quiz Setup")
    st.markdown("### ⚙️ Configure your quiz settings below:")
    st.markdown("---")

    if not st.session_state.transcript:
        st.warning("⚠️ Please extract transcript first!")
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("🏠 Go to Home", use_container_width=True, type="primary"):
                st.session_state.page = 'home'
                st.rerun()
    else:
        if st.session_state.quiz_data:
            st.success("✅ Quiz already generated! What would you like to do?")
            st.markdown("")

            # Fix: Force black text on buttons
            st.markdown("""
            <style>
            div[data-testid="stButton"] button {
                color: #000000 !important;
                font-weight: 600 !important;
            }
            </style>
            """, unsafe_allow_html=True)

            col1, col2, col3 = st.columns([1, 1, 1])
            with col1:
                if st.button("▶️ Resume Existing Quiz", type="primary", use_container_width=True, key="take_existing_btn"):
                    st.session_state.page = 'quiz'
                    st.rerun()
            with col2:
                if st.button("🔁 Generate New Quiz", type="primary", use_container_width=True, key="gen_new_btn"):
                    st.session_state.quiz_data = None
                    st.session_state.quiz_submitted = False
                    st.session_state.user_answers = {}
                    st.rerun()
            with col3:
                if st.button("🏠 Go to Home", type="primary", use_container_width=True, key="home_from_quiz_btn"):
                    st.session_state.page = 'home'
                    st.rerun()

            # Fix: Correctly count questions
            st.markdown("---")
            st.markdown("### 📋 Current Quiz Info")

            quiz_data = st.session_state.quiz_data
            if isinstance(quiz_data, list):
                question_count = len(quiz_data)
            elif isinstance(quiz_data, dict) and "questions" in quiz_data:
                question_count = len(quiz_data["questions"])
            else:
                question_count = len(quiz_data)

            quiz_info_col1, quiz_info_col2 = st.columns(2)
            with quiz_info_col1:
                st.info(f"📊 **Questions:** {question_count}")
            with quiz_info_col2:
                status_text = "✅ Submitted" if st.session_state.quiz_submitted else "⏳ Not attempted yet"
                st.info(f"📝 **Status:** {status_text}")

        else:
            # ✅ Quiz not yet generated — show setup form (your existing code unchanged below)

            # SUPER STRONG CSS TO FORCE BLACK TEXT
            st.markdown("""
            <style>
            /* Force selectbox text to be BLACK with maximum specificity */
            div[data-baseweb="select"] * {
                color: #000000 !important;
            }

            div[data-baseweb="select"] div {
                color: #000000 !important;
                background-color: #ffffff !important;
                font-weight: 700 !important;
                font-size: 1.2rem !important;
            }

            /* Selected value styling */
            div[data-baseweb="select"] > div:first-child {
                color: #000000 !important;
                background-color: #ffffff !important;
            }

            /* Dropdown arrow */
            div[data-baseweb="select"] svg {
                color: #000000 !important;
            }

            /* Dropdown menu items */
            div[role="listbox"] {
                background-color: #ffffff !important;
            }

            div[role="option"] {
                color: #000000 !important;
                font-weight: 600 !important;
                background-color: #ffffff !important;
            }

            div[role="option"]:hover {
                background-color: #f0f0f0 !important;
                color: #000000 !important;
            }

            /* Override any inherited white color from feature cards */
            section[data-testid="stVerticalBlock"] div[data-baseweb="select"] * {
                color: #000000 !important;
            }

            /* Label text should remain white on gradient */
            .stSelectbox label {
                color: #ffffff !important;
            }
            </style>
            """, unsafe_allow_html=True)

            st.markdown("")

            # Two columns for settings
            col1, col2 = st.columns(2, gap="large")

            with col1:
                # Purple gradient box
                st.markdown("""
                <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                            padding: 1.5rem; border-radius: 12px;
                            box-shadow: 0 4px 12px rgba(0,0,0,0.15);'>
                    <p style='color: white; margin: 0 0 0.8rem 0; font-size: 1.1rem; font-weight: 700;'>
                        📊 Number of Questions
                    </p>
                </div>
                """, unsafe_allow_html=True)

                st.markdown("")  # Small gap

                num_questions = st.selectbox(
                    "Select number of questions",
                    options=[5, 10, 15, 20],
                    index=0,
                    key="num_questions_select",
                    label_visibility="collapsed"
                )

            with col2:
                # Pink gradient box
                st.markdown("""
                <div style='background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                            padding: 1.5rem; border-radius: 12px;
                            box-shadow: 0 4px 12px rgba(0,0,0,0.15);'>
                    <p style='color: white; margin: 0 0 0.8rem 0; font-size: 1.1rem; font-weight: 700;'>
                        ⚡ Difficulty Level
                    </p>
                </div>
                """, unsafe_allow_html=True)

                st.markdown("")  # Small gap

                difficulty = st.selectbox(
                    "Select difficulty level",
                    options=["Easy", "Medium", "Hard"],
                    index=1,
                    key="difficulty_select",
                    label_visibility="collapsed"
                )

            st.markdown("---")
            st.markdown("")

            # Generate Quiz Button
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("🚀 Generate Quiz", type="primary", use_container_width=True, key="generate_quiz_btn"):
                    with st.spinner("🤖 AI is creating your quiz... This may take 30-60 seconds..."):
                        with st.status("Processing...", expanded=True) as status:
                            st.write("📊 Analyzing content...")
                            st.write("❓ Generating questions...")
                            st.write("✅ Creating answers...")

                            quiz_gen = QuizGenerator()
                            quiz_data = quiz_gen.generate_quiz(
                                st.session_state.transcript,
                                num_questions,
                                difficulty
                            )

                        if quiz_data:
                            st.session_state.quiz_data = quiz_data
                            st.session_state.quiz_submitted = False
                            st.session_state.user_answers = {}
                            st.session_state.page = 'quiz'
                            status.update(label="✅ Quiz ready!", state="complete")
                            st.rerun()
                        else:
                            status.update(label="❌ Generation failed", state="error")
                            st.error("Failed to generate quiz. Please try again.")
                            st.info("💡 Try with fewer questions or check API key")

# ==================== QUIZ PAGE ====================
elif st.session_state.page == 'quiz':
    st.subheader("🧪 Take Your Quiz")
    
    if not st.session_state.quiz_data:
        st.warning("⚠️ No quiz data found!")
        if st.button("← Back to Setup"):
            st.session_state.page = 'quiz_setup'
            st.rerun()
    else:
        quiz = st.session_state.quiz_data
        questions = quiz.get('questions', [])
        
        if not st.session_state.quiz_submitted:
            # Display questions
            st.info(f"📝 Answer all {len(questions)} questions and submit when ready!")
            st.markdown("---")
            
            for i, q in enumerate(questions):
                st.markdown(f"### Question {q['id']}")
                st.markdown(f"**{q['question']}**")
                
                if q['type'] == 'mcq':
                    answer = st.radio(
                        "Select your answer:",
                        q['options'],
                        key=f"q_{q['id']}",
                        index=None
                    )
                    if answer:
                        st.session_state.user_answers[q['id']] = answer
                else:
                    answer = st.text_area(
                        "Your answer:",
                        key=f"q_{q['id']}",
                        height=100,
                        placeholder="Type your answer here..."
                    )
                    if answer:
                        st.session_state.user_answers[q['id']] = answer
                
                st.markdown("")
            
            st.markdown("---")
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("✅ Submit Quiz", type="primary", use_container_width=True):
                    if len(st.session_state.user_answers) < len(questions):
                        st.warning(f"⚠️ Please answer all questions! ({len(st.session_state.user_answers)}/{len(questions)} answered)")
                    else:
                        st.session_state.quiz_submitted = True
                        st.rerun()
        
        else:
            # Show results
            st.success("🎉 Quiz Submitted! Here are your results:")
            st.markdown("---")
            
            correct_count = 0
            total_questions = len(questions)
            
            for q in questions:
                user_ans = st.session_state.user_answers.get(q['id'], '')
                is_correct = QuizGenerator.evaluate_answer(
                    user_ans,
                    q['correct_answer'],
                    q['type']
                )
                
                if is_correct:
                    correct_count += 1
                
                # Display question with result
                if is_correct:
                    st.success(f"✅ Question {q['id']}: Correct!")
                else:
                    st.error(f"❌ Question {q['id']}: Incorrect")
                
                st.markdown(f"**{q['question']}**")
                st.info(f"**Your Answer:** {user_ans}")
                st.info(f"**Correct Answer:** {q['correct_answer']}")
                st.markdown(f"**💡 Explanation:** {q['explanation']}")
                st.markdown("")
            
            # Final score
            st.markdown("---")
            score_percent = (correct_count / total_questions) * 100
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.markdown(f"## 🏆 Final Score: {correct_count}/{total_questions}")
                st.progress(score_percent / 100)
                st.markdown(f"### {score_percent:.1f}%")
            
            if score_percent >= 80:
                st.balloons()
                st.success("🌟 Excellent work! You have mastered this topic!")
            elif score_percent >= 60:
                st.info("👍 Good job! Review the explanations to improve further!")
            else:
                st.warning("📚 Keep studying! Review the notes and try again!")
            
            st.markdown("---")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔄 Take Another Quiz", use_container_width=True):
                    st.session_state.page = 'quiz_setup'
                    st.session_state.quiz_data = None
                    st.session_state.user_answers = {}
                    st.session_state.quiz_submitted = False
                    st.rerun()
            with col2:
                if st.button("🏠 Back to Home", use_container_width=True):
                    st.session_state.page = 'home'
                    st.rerun()

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #666; padding: 20px;'>
        <p><strong>🎓 AI-Powered YouTube Learning Platform</strong></p>
        <p>Final Year Project 2025-26</p>
        <p>Powered by Streamlit + AI + YouTube Transcript API</p>
    </div>
""", unsafe_allow_html=True)
