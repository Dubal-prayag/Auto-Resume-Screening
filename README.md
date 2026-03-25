# 🎯 RecruitAI — Enterprise Resume Screening System

<div align="center">

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.x-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Sentence Transformers](https://img.shields.io/badge/Sentence--Transformers-AI-green?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Active-brightgreen?style=for-the-badge)

**A fully automated, AI-powered resume screening dashboard — built for HR professionals and recruiters who need fast, accurate, and explainable candidate ranking at scale.**

[🚀 Quick Start](#️-installation) · [📸 Features](#-key-features) · [🧠 How It Works](#️-how-it-works) · [🛠 Tech Stack](#-tech-stack) · [🤝 Contributing](#-contributing)

</div>

---

## 📌 What Is This?

**RecruitAI** is an open-source, AI-powered resume screening tool built with **Streamlit**, **Python**, and **Sentence Transformers**. It allows HR teams to paste a Job Description and upload dozens of candidate resumes (PDF, DOCX, TXT) — and instantly receive a ranked shortlist with AI-generated reasoning for every score.

No more reading hundreds of CVs manually. No more missing qualified candidates due to keyword mismatches. RecruitAI understands **meaning**, not just exact words.

> ✅ Perfect for: Startups, HR Departments, Recruitment Agencies, Talent Teams, and CS/AI students learning applied NLP.

---

## 🚀 Key Features

| Feature | Description |
|---|---|
| 🧠 **Deep Semantic Matching** | Uses `sentence-transformers` (all-MiniLM-L6-v2) to understand context — knows that "AWS" = "Amazon Web Services" |
| 💡 **Explainable AI Reasoning** | Every candidate gets a color-coded paragraph explaining *why* they scored high or low |
| 📄 **Advanced Resume Parsing** | Uses `pdfplumber` with spatial layout mapping to extract text from complex, multi-column PDFs |
| 🎯 **200+ Skill Database** | Technical, cybersecurity, and soft skills tracked in a manageable `skills.json` — no code changes needed to add new skills |
| 📊 **Interactive Plotly Charts** | Visual comparison of candidates side-by-side with bar charts and score breakdowns |
| 📥 **CSV Export** | One-click download of all results in a clean, shareable spreadsheet |
| 🖥️ **Pro SaaS-Inspired UI** | Minimalist, enterprise-grade interface inspired by Stripe and Tailwind — clean whitespace, high-contrast typography |
| ⚡ **Fast & Local** | Runs entirely on your machine — no data leaves your system, no API costs |

---

## 🧠 How It Works

The system follows a 4-step pipeline:

```
📁 Upload JD + Resumes
        ↓
🔍 Text Extraction (pdfplumber / python-docx)
        ↓
🤖 AI Scoring Engine
   ├── 50% Semantic Similarity  (Sentence Transformers embeddings vs JD)
   └── 50% Skill Match Score    (200+ skills from skills.json)
        ↓
📊 Ranked Results + Explainable AI Summary
```

### Step-by-Step Breakdown

1. **Upload** — Paste your Job Description and attach candidate resumes (PDF, DOCX, or TXT)
2. **Extraction** — The engine extracts clean text while preserving critical technical punctuation (e.g., `C++`, `.NET`, `Node.js`)
3. **Scoring** — Two parallel scoring engines run simultaneously:
   - **Semantic Engine**: Converts both the JD and resume into vector embeddings using `all-MiniLM-L6-v2` and measures cosine similarity
   - **Skill Engine**: Scans resumes against 200+ curated skills in `skills.json` for exact and fuzzy matches
4. **Ranking** — Final score = `(Semantic Score × 0.5) + (Skill Match Score × 0.5)`
5. **Insights** — Candidates are ranked, visualized, and accompanied by a plain-English AI explanation

---

## 🛠 Tech Stack

| Category | Technology |
|---|---|
| **Frontend / UI** | Streamlit |
| **AI / NLP** | Sentence Transformers (`all-MiniLM-L6-v2`), scikit-learn |
| **PDF Parsing** | pdfplumber, python-docx |
| **Data Processing** | Pandas, NumPy |
| **Visualization** | Plotly Express, Plotly Graph Objects |
| **Skills Database** | Custom `skills.json` (200+ entries) |
| **Language** | Python 3.9+ |

---

## 📂 Project Structure

```
resume-screening-system/
│
├── app.py                   # Main Streamlit application (UI + orchestration)
│
├── utils/
│   ├── pdf_parser.py        # Resume text extraction (PDF, DOCX, TXT)
│   ├── preprocessor.py      # Text cleaning & normalization
│   ├── scorer.py            # Core AI ranking logic
│   └── skill_extractor.py   # Skill detection & matching engine
│
├── data/
│   ├── skills.json          # 200+ skills database (editable, no coding needed)
│   └── sample_resumes/      # Example resumes for testing
│
├── output/                  # Auto-generated results & exports
├── requirements.txt         # All Python dependencies
└── README.md
```

---

## ⚙️ Installation

> **Prerequisites:** Python 3.9 or higher must be installed. Check with `python --version`.

### 1. Clone the Repository

```bash
git clone https://github.com/Dubal-prayag/Auto-Resume-Screening.git
cd Auto-Resume-Screening
```

### 2. Create a Virtual Environment

A virtual environment keeps this project's dependencies isolated from your system Python.

```bash
# Create the environment
python -m venv venv

# Activate it:
# On Windows:
venv\Scripts\activate

# On macOS / Linux:
source venv/bin/activate
```

> 💡 You'll know it's active when you see `(venv)` at the start of your terminal line.

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

> ⏳ This may take 2–5 minutes on first run — it downloads the AI model (~90MB).

---

## 🖥️ Running the App

```bash
streamlit run app.py
```

The app will automatically open in your browser at:

```
http://localhost:8501
```

If it doesn't open automatically, copy that URL and paste it into your browser.

---

## 🧪 How to Use (Step-by-Step)

1. **Open the app** at `http://localhost:8501`
2. **Paste your Job Description** into the text area on the left panel
3. **Upload resumes** — drag and drop PDF, DOCX, or TXT files (bulk upload supported)
4. **Click "Screen Resumes"** — the AI processes everything in seconds
5. **View the ranked table** — candidates are sorted from best to worst fit
6. **Read AI explanations** — each candidate has a color-coded reasoning block
7. **Download results** — click "Export CSV" to save the full report

---

## 🔧 Customizing the Skills Database

You can add or remove skills **without touching any Python code**:

1. Open `data/skills.json`
2. Add your skill to the appropriate category:

```json
{
  "technical": ["Python", "Docker", "Kubernetes", "Your New Skill"],
  "soft_skills": ["Communication", "Leadership"],
  "cybersecurity": ["Penetration Testing", "SIEM", "SOC"]
}
```

3. Save the file and re-run the app — changes apply immediately

---

## ❓ Troubleshooting

| Problem | Solution |
|---|---|
| `ModuleNotFoundError` | Make sure your virtual environment is active: `venv\Scripts\activate` |
| App won't open in browser | Manually go to `http://localhost:8501` |
| PDF text not extracting | Ensure the PDF is not scanned/image-only. Use a text-based PDF |
| Slow first run | Normal — the AI model (~90MB) downloads once and caches locally |
| `pip install` fails | Try: `pip install --upgrade pip` then reinstall |

---

## 🤝 Contributing

Contributions are welcome! Here's how to get started:

```bash
# 1. Fork the repo on GitHub
# 2. Clone your fork
git clone https://github.com/YOUR-USERNAME/Auto-Resume-Screening.git

# 3. Create a feature branch
git checkout -b feature/your-feature-name

# 4. Make your changes and commit
git add .
git commit -m "feat: describe your change"

# 5. Push and open a Pull Request
git push origin feature/your-feature-name
```

---

## 📄 License

This project is licensed under the **MIT License** — you are free to use, modify, and distribute it with attribution.

---

## 👨‍💻 Author

**Dubal Prayag**
- GitHub: [@Dubal-prayag](https://github.com/Dubal-prayag)

---

<div align="center">

⭐ **If this project helped you, please give it a star on GitHub!** ⭐

*Built with ❤️ using Python, Streamlit, and open-source AI*

</div>
