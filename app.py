import os
import logging
from flask import Flask, render_template, request, jsonify, flash, redirect, url_for, session
from werkzeug.utils import secure_filename
from werkzeug.middleware.proxy_fix import ProxyFix
import tempfile
import uuid

from resume_analyzer import ResumeAnalyzer
from utils import allowed_file

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)  # needed for url_for to generate with https

# Configure upload folder and allowed extensions
UPLOAD_FOLDER = tempfile.gettempdir()
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Initialize Resume Analyzer
resume_analyzer = ResumeAnalyzer()

# In-memory storage for analysis results
analysis_results = {}

@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze_resume():
    """Analyze the uploaded resume and job description"""
    if 'resume' not in request.files:
        flash('No resume file uploaded', 'danger')
        return redirect(request.url)
    
    resume_file = request.files['resume']
    job_description = request.form.get('job_description', '')
    
    if resume_file.filename == '':
        flash('No resume file selected', 'danger')
        return redirect(request.url)
    
    if not job_description:
        flash('Job description is required', 'danger')
        return redirect(request.url)
    
    if resume_file and allowed_file(resume_file.filename):
        # Create a unique ID for this analysis
        analysis_id = str(uuid.uuid4())
        
        # Save the uploaded file temporarily
        filename = secure_filename(resume_file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        resume_file.save(filepath)
        
        try:
            # Analyze the resume
            results = resume_analyzer.analyze_resume(filepath, job_description)
            
            # Store results in memory
            analysis_results[analysis_id] = results
            
            # Store the analysis ID in the session
            session['current_analysis_id'] = analysis_id
            
            # Redirect to dashboard
            return redirect(url_for('dashboard'))
            
        except Exception as e:
            logging.error(f"Error analyzing resume: {str(e)}")
            flash(f'Error analyzing resume: {str(e)}', 'danger')
            return redirect(request.url)
        finally:
            # Clean up the file
            if os.path.exists(filepath):
                os.remove(filepath)
    else:
        flash('Invalid file type. Please upload a PDF file.', 'danger')
        return redirect(request.url)

@app.route('/dashboard')
def dashboard():
    """Render the dashboard with analysis results"""
    analysis_id = session.get('current_analysis_id')
    
    if not analysis_id or analysis_id not in analysis_results:
        flash('No analysis results found. Please upload a resume first.', 'warning')
        return redirect(url_for('index'))
    
    results = analysis_results[analysis_id]
    return render_template('dashboard.html', results=results)

@app.route('/api/results/<analysis_id>')
def get_results(analysis_id):
    """API endpoint to get analysis results"""
    if analysis_id in analysis_results:
        return jsonify(analysis_results[analysis_id])
    else:
        return jsonify({"error": "Analysis not found"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
