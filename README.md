To Run The Project:
cd path\to\your\project
python -m venv venv
venv\Scripts\activate
pip install flask flask-sqlalchemy gunicorn psycopg2-binary spacy pymupdf scikit-learn email-validator werkzeug
python -m spacy download en_core_web_sm
flask run

