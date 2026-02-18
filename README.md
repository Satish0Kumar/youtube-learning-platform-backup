# 🎓 AI-Powered YouTube Learning Platform

> Transform any YouTube video into structured study material using AI — instantly generate transcripts, smart notes, and quizzes.

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.40+-red?style=flat&logo=streamlit)
![AI Powered](https://img.shields.io/badge/AI-Powered-purple?style=flat)
![Final Year Project](https://img.shields.io/badge/Project-Final%20Year%202025--26-green?style=flat)

---

## 📌 About the Project

This is a **Final Year B.Tech Project (2025-26)** that converts any YouTube video into a complete learning experience. Users simply paste a YouTube URL and the platform automatically:

- Extracts the full video transcript
- Generates AI-powered structured study notes
- Creates customizable quizzes to test understanding

Built with **Streamlit** for the frontend and **AI language models** for intelligent content generation.

---

## ✨ Features

- 🎬 **YouTube Transcript Extraction** — Instantly fetch transcripts from any YouTube video using the YouTube Transcript API
- 📝 **AI Notes Generation** — Generate well-structured study notes with key concepts, insights, and takeaways
- 🧪 **AI Quiz Generation** — Create multiple-choice quizzes with custom difficulty levels (Easy / Medium / Hard) and question counts (5 / 10 / 15 / 20)
- 📊 **Progress Tracker** — Visual sidebar tracker showing completion status of Transcript → Notes → Quiz
- 🔁 **Content Retention** — All generated content persists across page navigation within the session
- 🖼️ **Video Preview** — Thumbnail preview of the entered YouTube video
- 📱 **Responsive UI** — Clean, modern interface with gradient cards and smooth navigation

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Streamlit |
| Transcript Extraction | YouTube Transcript API |
| AI / LLM | AI Language Model API |
| PDF Generation | ReportLab |
| Database (optional) | MongoDB (PyMongo) |
| Environment Config | Python dotenv |
| Language | Python 3.10+ |

---

## 📁 Project Structure

youtube-learning-platform/
│
├── app.py # Main Streamlit application
├── requirements.txt # Python dependencies
├── .env # API keys (not pushed to GitHub)
├── .gitignore # Git ignore rules
├── README.md # Project documentation
│
├── services/
│ ├── notes_generator.py # AI notes generation logic
│ └── quiz_generator.py # AI quiz generation logic
│
└── utils/
├── transcript_extractor.py # YouTube transcript fetching
└── pdf_generator.py # PDF export functionality

text

---

## ⚙️ Setup & Installation

### Prerequisites
- Python 3.10 or higher
- A valid AI API key
- Git

### Step 1 — Clone the Repository

```bash
git clone https://github.com/your-username/youtube-learning-platform.git
cd youtube-learning-platform
Step 2 — Create Virtual Environment
bash
python -m venv venv
Step 3 — Activate Virtual Environment
bash
# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
Step 4 — Install Dependencies
bash
pip install -r requirements.txt
Step 5 — Configure API Key
Create a .env file in the project root:

text
GEMINI_API_KEY=your_api_key_here
⚠️ Never push your .env file to GitHub. It is already listed in .gitignore.

Step 6 — Run the Application
bash
streamlit run app.py
Open your browser at: http://localhost:8501

🚀 How to Use
Paste a YouTube URL in the input box on the Home page

Click "Extract Transcript" — the transcript is fetched instantly

Navigate to Notes from the sidebar → Click "Generate AI Notes"

Navigate to Quiz Setup → Select number of questions and difficulty → Click "Generate Quiz"

Take the quiz and check your score!

🔒 Environment Variables
Variable	Description
GEMINI_API_KEY	API key for AI language model access
📸 Screenshots
(Add screenshots of Home page, Notes page, and Quiz page here)

🙌 Acknowledgements
Streamlit — for the rapid web app framework

YouTube Transcript API — for transcript extraction

ReportLab — for PDF generation

👨‍💻 Author
Final Year B.Tech — Computer Science
Academic Year: 2025–26

📄 License
This project is developed for academic purposes as part of a Final Year Project submission.