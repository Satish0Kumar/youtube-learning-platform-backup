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

# Page config
st.set_page_config(
    page_title="AI YouTube Learning Platform",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 3.5em;
        font-weight: bold;
        font-size: 16px;
    }
    .notes-container {
        padding: 2rem;
        border-radius: 10px;
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        line-height: 1.8;
    }
    .quiz-question {
        padding: 1.5rem;
        border-radius: 8px;
        background-color: #fff;
        border: 2px solid #e9ecef;
        margin-bottom: 1.5rem;
    }
    .correct-answer {
        background-color: #d4edda;
        border-color: #28a745;
    }
    .incorrect-answer {
        background-color: #f8d7da;
        border-color: #dc3545;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'page' not in st.session_state:
    st.session_state.page = 'home'
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

# Header
st.title("🎓 AI-Powered YouTube Learning Platform")
st.markdown("### Transform YouTube Videos into Study Material & Quizzes")

# Sidebar Navigation
with st.sidebar:
    st.header("📍 Navigation")
    
    if st.button("🏠 Home", use_container_width=True):
        st.session_state.page = 'home'
        st.rerun()
    
    if st.session_state.transcript:
        if st.button("📝 AI Notes", use_container_width=True):
            st.session_state.page = 'notes'
            st.rerun()
        
        if st.button("🧪 AI Quiz", use_container_width=True):
            st.session_state.page = 'quiz_setup'
            st.rerun()
    
    st.markdown("---")
    st.markdown("**Status:**")
    if st.session_state.transcript:
        st.success("✅ Transcript Loaded")
        st.info(f"📊 {len(st.session_state.transcript.split())} words")
    else:
        st.info("⏳ No transcript yet")

st.markdown("---")

# ==================== HOME PAGE ====================
if st.session_state.page == 'home':
    st.subheader("📹 Enter YouTube Video URL")
    
    youtube_url = st.text_input(
        "Paste YouTube URL here:",
        placeholder="https://www.youtube.com/watch?v=...",
        key="url_input"
    )
    
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
                        
                        st.success("✅ Transcript extracted successfully!")
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Words", len(transcript.split()))
                        with col2:
                            st.metric("Characters", len(transcript))
                        with col3:
                            st.metric("Duration", f"~{len(transcript.split())/150:.0f} min")
                        
                        st.info("👈 **Use sidebar to generate Notes or Quiz!**")
                    else:
                        st.error(f"❌ {error}")
    
    with col2:
        if st.button("🔄 Clear All", use_container_width=True):
            st.session_state.transcript = None
            st.session_state.video_id = None
            st.session_state.notes = None
            st.session_state.quiz_data = None
            st.rerun()
    
    # Display transcript if available
    if st.session_state.transcript:
        st.markdown("---")
        with st.expander("📄 View Transcript", expanded=False):
            st.text_area("", st.session_state.transcript, height=300, disabled=True)

# ==================== NOTES PAGE ====================
elif st.session_state.page == 'notes':
    st.subheader("📝 AI-Generated Notes")
    
    if not st.session_state.transcript:
        st.warning("⚠️ Please extract transcript first!")
        if st.button("← Go to Home"):
            st.session_state.page = 'home'
            st.rerun()
    else:
        if not st.session_state.notes:
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("✨ Generate AI Notes", type="primary", use_container_width=True):
                    with st.spinner("🤖 AI is generating comprehensive notes... This may take 30-60 seconds..."):
                        notes_gen = NotesGenerator()
                        notes, error = notes_gen.generate_notes(st.session_state.transcript)
                    
                    if notes:
                        st.session_state.notes = notes
                        st.rerun()
                    else:
                        st.error(f"❌ {error}")
                        st.info("💡 Try again or check your API key")
        else:
            st.success("✅ Notes generated successfully!")
            
            # Display notes
            st.markdown('<div class="notes-container">', unsafe_allow_html=True)
            st.markdown(st.session_state.notes)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Download options
            st.markdown("---")
            col1, col2, col3 = st.columns([1, 1, 1])
            
            with col1:
                st.download_button(
                    label="📥 Download as TXT",
                    data=st.session_state.notes,
                    file_name=f"notes_{st.session_state.video_id}.txt",
                    mime="text/plain",
                    use_container_width=True
                )
            
            with col2:
                try:
                    pdf_buffer = PDFGenerator.generate_notes_pdf(
                        st.session_state.notes,
                        st.session_state.video_url,
                        st.session_state.video_id
                    )
                    
                    st.download_button(
                        label="📄 Download as PDF",
                        data=pdf_buffer,
                        file_name=f"notes_{st.session_state.video_id}.pdf",
                        mime="application/pdf",
                        type="primary",
                        use_container_width=True
                    )
                except Exception as e:
                    st.error(f"PDF generation error: {str(e)}")
            
            with col3:
                if st.button("🔄 Regenerate Notes", use_container_width=True):
                    st.session_state.notes = None
                    st.rerun()

# ==================== QUIZ SETUP PAGE ====================
elif st.session_state.page == 'quiz_setup':
    st.subheader("🧪 AI Quiz Setup")
    
    if not st.session_state.transcript:
        st.warning("⚠️ Please extract transcript first!")
        if st.button("← Go to Home"):
            st.session_state.page = 'home'
            st.rerun()
    else:
        st.info("⚙️ Configure your quiz settings below:")
        
        col1, col2 = st.columns(2)
        
        with col1:
            num_questions = st.selectbox(
                "📊 Number of Questions",
                [5, 10, 15, 20],
                index=0
            )
        
        with col2:
            difficulty = st.selectbox(
                "⚡ Difficulty Level",
                ["Easy", "Medium", "Hard"],
                index=1
            )
        
        st.markdown("---")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🚀 Generate Quiz", type="primary", use_container_width=True):
                with st.spinner("🤖 AI is creating your quiz... This may take 30-60 seconds..."):
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
                    st.rerun()
                else:
                    st.error("❌ Failed to generate quiz. Please try again.")
                    st.info("💡 Try with fewer questions or check your API key")

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
                st.markdown(f'<div class="quiz-question">', unsafe_allow_html=True)
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
                
                st.markdown('</div>', unsafe_allow_html=True)
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
                css_class = "correct-answer" if is_correct else "incorrect-answer"
                st.markdown(f'<div class="quiz-question {css_class}">', unsafe_allow_html=True)
                
                if is_correct:
                    st.success(f"✅ Question {q['id']}: Correct!")
                else:
                    st.error(f"❌ Question {q['id']}: Incorrect")
                
                st.markdown(f"**{q['question']}**")
                st.info(f"**Your Answer:** {user_ans}")
                st.info(f"**Correct Answer:** {q['correct_answer']}")
                st.markdown(f"**💡 Explanation:** {q['explanation']}")
                st.markdown('</div>', unsafe_allow_html=True)
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
        <p>Powered by Streamlit + Google Gemini AI + YouTube Transcript API</p>
    </div>
""", unsafe_allow_html=True)
