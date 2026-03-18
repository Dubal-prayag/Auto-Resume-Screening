# AI-Powered Resume Screening System (Pro Edition)

A fully automated, ultra-fast, and highly accurate AI resume screening dashboard built with Streamlit, Python, and Sentence Transformers. This tool allows HR professionals and recruiters to upload a job description alongside dozens of applicant resumes (PDF, DOCX, TXT) to instantly rank top candidates using deep semantic analysis.

## 🚀 Key Features
- **Deep Semantic Matching**: Uses `sentence-transformers` (all-MiniLM-L6-v2) to understand context and meaning, not just exact keyword overlap (i.e., it knows "AWS" = "Amazon Web Services").
- **Pro "SaaS" Minimalist UI**: A hyper-clean, professional interface inspired by enterprise dashboards (Stripe, Tailwind) with intuitive whitespace and high-contrast typography.
- **Explainable AI Reasoning**: Every candidate receives a dynamic, color-coded summary paragraph explaining *why* they got their score based on skill hits and semantic alignment.
- **Advanced Resume Parsing**: Uses `pdfplumber` with spatial layout mapping (`layout=True`) to seamlessly extract data from complex, multi-column resumes.
- **Configurable Skills DB**: Over 200 technical, cyber, and soft skills live in a managed `skills.json` file, allowing easy addition of new keywords without touching Python code.

## ⚙️ How It Works
1. **Upload**: Paste a Job Description and attach candidate resumes.
2. **Analysis**: The engine extracts texts, protects critical technical punctuation (e.g., `C++`, `.NET`), compares semantic embeddings against the JD, and matches 200+ specific skills.
3. **Ranking**: The candidates are scored using a balanced **50% Semantic Match / 50% Exact Skill Match** logic. 
4. **Insights**: Download the results cleanly inside a CSV or view interactive Plotly charts.

## 🛠️ Installation
Ensure you have Python 3.9+ installed.

```bash
# Clone the repository
git clone https://github.com/your-username/resume-screening-system.git
cd resume-screening-system

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows use `venv\\Scripts\\activate`

# Install dependencies
pip install -r requirements.txt
```

## 🖥️ Running Locally
To launch the dashboard, run:
```bash
streamlit run app.py
```
The app will open automatically in your browser at `http://localhost:8501`.
