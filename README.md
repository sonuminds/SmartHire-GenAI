# 💼 SmartHire GenAI

An AI-powered Resume Screening and Candidate Recommendation System built using **Google Gemini, FAISS, Streamlit, and Python**. SmartHire GenAI analyzes resumes, recommends semantically matching jobs, provides AI-generated resume improvement suggestions, and answers career-related questions through a Retrieval-Augmented Generation (RAG) based career mentor.

---

## 🚀 Features

- 📄 **AI Resume Parsing**
  - Extracts structured information from PDF resumes.
  - Identifies:
    - Name
    - Email
    - Phone
    - Skills
    - Education
    - Experience
    - Projects
    - Certifications
    - Target Role

- 💼 **Semantic Job Recommendation**
  - Uses Google Gemini Embeddings.
  - Performs similarity search with FAISS.
  - Recommends the Top 5 most relevant jobs from the dataset.

- 📝 **AI Resume Improvement Suggestions**
  - Reviews the resume against recommended jobs.
  - Highlights:
    - Resume strengths
    - Missing skills
    - Improvement suggestions
    - Overall resume score

- 🎓 **AI Career Mentor (RAG)**
  - Answers career and resume-related questions.
  - Uses Retrieval-Augmented Generation with career guidance notes.
  - Provides grounded responses based on stored knowledge.

- 🛡️ **Guardrails**
  - Blocks unsafe prompts.
  - Rejects unrelated questions.
  - Restricts mentor responses to career-related topics.

---

# 🛠 Tech Stack

| Category | Technologies |
|-----------|--------------|
| Programming Language | Python |
| Frontend | Streamlit |
| LLM | Google Gemini 3.1 Flash Lite |
| Embeddings | Gemini Embedding-001 |
| Vector Database | FAISS |
| Resume Parsing | Gemini API |
| Data Processing | Pandas, NumPy |
| Environment | python-dotenv |

---

# 📂 Project Structure

```
SmartHire-GenAI/
│
├── app/
│   └── streamlit_app.py
│
├── src/
│   ├── config.py
│   ├── parsing/
│   ├── search/
│   ├── mentor/
│   ├── generate/
│   └── safety/
│
├── data/
│   └── career_notes/
│
├── vectorstore/
│   ├── jobs.index
│   └── jobs_metadata.pkl
│
├── requirements.txt
└── README.md
```

---

# ⚙️ Installation

## 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/SmartHire-GenAI.git
cd SmartHire-GenAI
```

---

## 2. Create Virtual Environment

```bash
python -m venv venv
```

Activate:

### Windows

```bash
venv\Scripts\activate
```

### Linux / Mac

```bash
source venv/bin/activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 4. Configure API Key

Create a `.env` file in the project root.

```env
GOOGLE_API_KEY=YOUR_GEMINI_API_KEY
```

---

## 5. Run the Application

```bash
streamlit run app/streamlit_app.py
```

---

# 🔄 Workflow

```
Resume Upload
       │
       ▼
Resume Text Extraction
       │
       ▼
Gemini Resume Parser
       │
       ▼
Structured Resume Profile
       │
       ▼
Gemini Embeddings
       │
       ▼
FAISS Semantic Search
       │
       ▼
Top Matching Jobs
       │
       ▼
AI Resume Suggestions
       │
       ▼
Career Mentor (RAG)
```

---

# 📸 Application Modules

- Resume Upload
- Resume Parser
- Resume Profile Dashboard
- Semantic Job Matching
- AI Resume Suggestions
- AI Career Mentor
- Safety Guardrails

---

# 🎯 Future Enhancements

- ATS Compatibility Score
- Resume PDF Report Download
- User Authentication
- Job Application Tracking
- Career Roadmap Generation
- Interview Preparation Assistant
- Multi-language Resume Support

---

# 👩‍💻 Author

**Shweta Sudarshan Gaikwad**

B.Tech Computer Science and Engineering  
Indian Institute of Information Technology Pune (IIIT Pune)

---

# 📄 License

This project is developed for educational and academic purposes.
