# 📄 AI Resume Analyzer

An AI-powered resume analyzer that scores a resume's ATS (Applicant Tracking
System) compatibility, extracts skills, matches against target job roles,
finds missing keywords, and generates AI-written improvement suggestions —
all through a simple Streamlit UI.

## ✨ Features

- **PDF Upload & Parsing** — extracts text from resume PDFs (`pdfplumber` + `PyPDF2` fallback)
- **Skill Extraction** — keyword/NLP-based detection across 100+ technical & soft skills
- **ATS Score** — heuristic score (0–100) based on contact info, sections, length, and action-verb usage
- **Job-Role Matching** — TF-IDF cosine similarity + required/preferred skill overlap against 8 predefined roles
- **Missing Keyword Detection** — required vs. preferred skills gap analysis
- **AI Improvement Suggestions** — OpenAI or Gemini generated summary, strengths, weaknesses, rewrites
- **Downloadable PDF Report** — polished report you can save or share
- **Analysis History** — stored locally in SQLite, viewable in the sidebar

## 🧰 Tech Stack

| Layer          | Tech                                   |
|----------------|-----------------------------------------|
| UI             | Streamlit, Plotly                       |
| PDF Parsing    | pdfplumber, PyPDF2                      |
| NLP / Matching | scikit-learn (TF-IDF), keyword matching |
| AI Feedback    | OpenAI API / Gemini API                 |
| Storage        | SQLite                                  |
| Reports        | ReportLab (PDF generation)              |

## 📂 Project Structure

```
ai-resume-analyzer/
├── app.py                  # Streamlit entry point
├── config.py                # Env-based configuration
├── requirements.txt
├── .env.example
├── data/
│   ├── job_roles.json        # Required/preferred skills per role
│   └── skills_db.json        # Master skills keyword database
├── src/
│   ├── pdf_parser.py          # PDF text extraction
│   ├── skill_extractor.py     # Skill/contact/section extraction
│   ├── ats_scorer.py          # ATS scoring heuristics
│   ├── job_matcher.py         # TF-IDF + skill overlap matching
│   ├── llm_analyzer.py        # OpenAI/Gemini feedback generation
│   ├── database.py            # SQLite history persistence
│   └── report_generator.py    # PDF report generation
└── tests/
    └── test_basic.py
```

## 🚀 Getting Started

### 1. Clone & install dependencies

```bash
git clone https://github.com/<your-username>/ai-resume-analyzer.git
cd ai-resume-analyzer
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` and add your API key for **either** OpenAI or Gemini:

```
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...
```

> The app still works without an API key — it falls back to rule-based
> feedback so the core ATS scoring and skill matching always function.

### 3. Run the app

```bash
streamlit run app.py
```

Open the URL Streamlit prints (usually `http://localhost:8501`).

### 4. Run tests

```bash
pytest tests/
```

## 🗺️ How It Works

1. **Upload** a PDF resume — text is extracted via `pdfplumber`.
2. **Skill extraction** scans the text against a curated skills database (languages, frameworks, ML/data tools, cloud/DevOps, soft skills).
3. **ATS scoring** checks contact info, section headers, resume length, and action-verb density.
4. **Job matching** compares your skills to a selected role's required/preferred list, plus a TF-IDF cosine-similarity check between your resume and the role's skill profile.
5. **AI feedback** sends your resume + gap analysis to OpenAI or Gemini for a written summary, strengths/weaknesses, and rewrite suggestions.
6. **Report** — everything is compiled into a downloadable PDF.

## 🔮 Roadmap Ideas

- Support `.docx` resumes
- Add more job roles / let users define custom role profiles
- Multi-resume comparison mode
- Export analysis history as CSV

## 📄 License

MIT — see [LICENSE](LICENSE).
