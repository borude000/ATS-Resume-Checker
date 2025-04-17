# ATS Resume Checker 📝

An AI-powered tool to analyze and improve your resume for Applicant Tracking Systems (ATS). This project helps job seekers optimize their resumes by checking ATS compatibility, analyzing keywords, and offering smart, personalized suggestions.

---

## 🔍 Features

- **ATS Compatibility**
  - Ensure your resume passes through Applicant Tracking Systems with flying colors.

- **Keyword Analysis**
  - Identify important keywords your resume is missing from the job description.

- **Smart Suggestions**
  - Receive tailored recommendations to improve your resume's effectiveness.

---

## 🚀 Getting Started

### Prerequisites
- Python 3.x
- pip (Python package installer)

### Installation & Run

```bash
cd path\to\your\project
python -m venv venv
venv\Scripts\activate

pip install flask flask-sqlalchemy gunicorn psycopg2-binary spacy pymupdf scikit-learn email-validator werkzeug
python -m spacy download en_core_web_sm

flask run
