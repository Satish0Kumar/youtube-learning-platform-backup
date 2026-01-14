# **📝 README Content for Your Project**

Based on our conversation about your YouTube learning platform project, here's a comprehensive README:

***

```markdown
# 🎓 AI-Powered YouTube Learning Platform

An intelligent web application that extracts transcripts from YouTube videos and provides AI-powered educational features including structured notes and interactive quizzes using Google Gemini models.

## ✨ Features

### 📹 Transcript Extraction
- Extract transcripts from any YouTube video using URL
- Support for both auto-generated and manual captions
- Multiple language support
- Clean, formatted transcript display

### 📝 AI-Powered Notes Generation
- Automatically generate comprehensive study notes from video transcripts
- Structured content with key concepts and explanations
- Download notes as PDF for offline study
- Powered by Google Gemini AI

### 🎯 Interactive Quiz Generation
- AI-generated quizzes based on video content
- Multiple-choice questions with instant feedback
- Adaptive difficulty levels
- Score tracking and performance analysis

### 📄 PDF Export
- Professional PDF generation for notes
- Clean formatting with proper headings
- Easy sharing and offline access

## 🛠️ Tech Stack

- **Frontend:** Streamlit
- **AI/ML:** Google Generative AI (Gemini)
- **APIs:** youtube-transcript-api
- **PDF Generation:** ReportLab
- **Backend:** Python 3.8+
- **Dependencies:** See `requirements.txt`

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- Google Gemini API key ([Get it here](https://makersuite.google.com/app/apikey))

### Setup

1. **Clone the repository**
```bash
git clone https://github.com/Satish0Kumar/youtube-learning-platform-backup.git
cd youtube-learning-platform-backup
```

2. **Create virtual environment**
```bash
python -m venv venv
```

3. **Activate virtual environment**
- Windows:
```bash
.\venv\Scripts\activate
```
- Linux/Mac:
```bash
source venv/bin/activate
```

4. **Install dependencies**
```bash
pip install -r requirements.txt
```

5. **Configure API Keys**

Create a `.streamlit` folder and `secrets.toml` file:
```bash
mkdir .streamlit
```

Add your API key to `.streamlit/secrets.toml`:
```toml
GEMINI_API_KEY = "your-api-key-here"
```

## 🚀 Usage

1. **Start the application**
```bash
streamlit run app.py
```

2. **Access the app**
Open your browser and go to `http://localhost:8501`

3. **Use the platform**
   - Paste a YouTube URL
   - Click "Extract Transcript"
   - Navigate to "Notes" or "Quiz" tabs
   - Generate AI-powered content
   - Download as PDF if needed

## 📁 Project Structure

```
youtube-learning-platform-backup/
├── services/
│   ├── __init__.py
│   ├── notes_generator.py      # AI notes generation logic
│   └── quiz_generator.py       # AI quiz generation logic
├── utils/
│   ├── __init__.py
│   ├── pdf_generator.py        # PDF creation utilities
│   └── transcript_extractor.py # YouTube transcript extraction
├── .streamlit/
│   └── secrets.toml            # API keys (not in repo)
├── app.py                      # Main Streamlit application
├── requirements.txt            # Python dependencies
├── .gitignore                  # Git ignore rules
└── README.md                   # This file
```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file (optional) or use `.streamlit/secrets.toml`:

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

### API Keys

- **Google Gemini API:** Required for AI features
  - Get your key: https://makersuite.google.com/app/apikey
  - Free tier available with generous limits

## 🎯 Features in Detail

### Notes Generation
- Extracts key concepts from video content
- Organizes information hierarchically
- Includes summaries and detailed explanations
- Exportable to PDF format

### Quiz System
- Generates relevant questions from content
- Multiple difficulty levels
- Instant feedback on answers
- Performance tracking

## 🔒 Security

- API keys stored in `.streamlit/secrets.toml` (excluded from Git)
- Environment variables for sensitive data
- No hardcoded credentials in source code

## 🤝 Contributing

This is a final year academic project. Suggestions and improvements are welcome!

## 📄 License

This project is created for educational purposes as part of a final year project.

## 👨‍💻 Author

**Satish Kumar**
- GitHub: [@Satish0Kumar](https://github.com/Satish0Kumar)
- Project: Final Year Computer Science Project

## 🙏 Acknowledgments

- Google Gemini AI for powerful language models
- Streamlit for the amazing web framework
- youtube-transcript-api for transcript extraction
- ReportLab for PDF generation

## 📞 Support

For issues or questions, please open an issue on GitHub.

---

**Note:** This is an educational project developed as part of a final year academic requirement.
```

***

