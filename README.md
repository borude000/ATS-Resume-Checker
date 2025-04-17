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
- 
![Screenshot 2025-04-17 181732](https://github.com/user-attachments/assets/9ea91b01-054e-4e87-83ba-220ea95b9c73)
![Screenshot 2025-04-17 181752](https://github.com/user-attachments/assets/d3af535d-d050-4144-82f5-d26742060d6d)
![Screenshot 2025-04-17 181805](https://github.com/user-attachments/assets/869c1f43-59f5-403a-a9f8-eb99596ec192)
![Screenshot 2025-04-17 181848](https://github.com/user-attachments/assets/d8c0586b-846c-427f-86cd-9bc99bb0946c)
![Screenshot 2025-04-17 181922](https://github.com/user-attachments/assets/3096d7fa-e92a-44c0-90a1-1379d796d47f)
![Screenshot 2025-04-17 181946](https://github.com/user-attachments/assets/ddb0bf83-73d4-4544-825f-623552245ec4)

### Installation & Run

```bash
cd path\to\your\project
python -m venv venv
venv\Scripts\activate
pip install flask flask-sqlalchemy gunicorn psycopg2-binary spacy pymupdf scikit-learn email-validator werkzeug
python -m spacy download en_core_web_sm
flask run
