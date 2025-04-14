import os
import logging
from flask import Flask, render_template, request, jsonify, flash, redirect, url_for, session
from werkzeug.utils import secure_filename
from werkzeug.middleware.proxy_fix import ProxyFix
import tempfile
import uuid
from datetime import datetime

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)  # needed for url_for to generate with https

# Configure database
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Configure upload folder and allowed extensions
UPLOAD_FOLDER = tempfile.gettempdir()
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Initialize SQLAlchemy
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy(app)

# Define models here to avoid circular imports
from sqlalchemy.dialects.postgresql import JSON

class User(db.Model):
    """User model for future authentication"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    analyses = db.relationship('ResumeAnalysis', backref='user', lazy=True)

class ResumeAnalysis(db.Model):
    """Database model for resume analysis results"""
    id = db.Column(db.Integer, primary_key=True)
    # If user is authenticated, link analysis to them
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    
    # Analysis session UUID (for non-authenticated users)
    session_id = db.Column(db.String(36), nullable=False, index=True)
    
    # File details
    original_filename = db.Column(db.String(255), nullable=True)
    resume_preview = db.Column(db.Text, nullable=True)
    
    # Job description
    job_description = db.Column(db.Text, nullable=False)
    
    # Analysis results
    overall_score = db.Column(db.Integer, nullable=False)
    ats_score = db.Column(db.Integer, nullable=False)
    keyword_match_percentage = db.Column(db.Float, nullable=False)
    structure_score = db.Column(db.Integer, nullable=False)
    semantic_similarity = db.Column(db.Float, nullable=False)
    
    # JSON fields for complex data
    ats_issues = db.Column(JSON, nullable=True)
    matched_keywords = db.Column(JSON, nullable=True)
    missing_keywords = db.Column(JSON, nullable=True)
    structure_issues = db.Column(JSON, nullable=True)
    resume_keywords = db.Column(JSON, nullable=True)
    job_keywords = db.Column(JSON, nullable=True)
    suggestions = db.Column(JSON, nullable=True)
    sections_found = db.Column(JSON, nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, session_id, original_filename, results):
        """Initialize a ResumeAnalysis from results dictionary"""
        self.session_id = session_id
        self.original_filename = original_filename
        
        # Basic fields
        self.job_description = results.get('job_description', '')
        self.resume_preview = results.get('resume_preview', '')
        self.overall_score = results.get('overall_score', 0)
        
        # ATS compatibility
        ats_compat = results.get('ats_compatibility', {})
        self.ats_score = ats_compat.get('score', 0)
        self.ats_issues = ats_compat.get('issues', [])
        
        # Keyword match
        keyword_match = results.get('keyword_match', {})
        self.keyword_match_percentage = keyword_match.get('percentage', 0)
        self.matched_keywords = keyword_match.get('matched_keywords', [])
        self.missing_keywords = keyword_match.get('missing_keywords', [])
        
        # Structure assessment
        structure = results.get('structure_assessment', {})
        self.structure_score = structure.get('score', 0)
        self.structure_issues = structure.get('issues', [])
        
        # Other fields
        self.semantic_similarity = results.get('semantic_similarity', 0)
        self.resume_keywords = results.get('resume_keywords', [])
        self.job_keywords = results.get('job_keywords', [])
        self.suggestions = results.get('suggestions', [])
        self.sections_found = results.get('sections_found', [])
    
    def to_dict(self):
        """Convert model to dictionary for template rendering"""
        return {
            'id': self.id,
            'overall_score': self.overall_score,
            'ats_compatibility': {
                'score': self.ats_score,
                'issues': self.ats_issues
            },
            'keyword_match': {
                'percentage': self.keyword_match_percentage,
                'matched_keywords': self.matched_keywords,
                'missing_keywords': self.missing_keywords
            },
            'structure_assessment': {
                'score': self.structure_score,
                'issues': self.structure_issues
            },
            'semantic_similarity': self.semantic_similarity,
            'resume_keywords': self.resume_keywords,
            'job_keywords': self.job_keywords,
            'suggestions': self.suggestions,
            'sections_found': self.sections_found,
            'resume_preview': self.resume_preview,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M')
        }

# Create tables if they don't exist
with app.app_context():
    db.create_all()

from resume_analyzer import ResumeAnalyzer
from utils import allowed_file

# Initialize Resume Analyzer
resume_analyzer = ResumeAnalyzer()

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
            
            # Add job description to results
            results['job_description'] = job_description
            
            # Ensure all numeric values are Python native types, not NumPy types
            if isinstance(results.get('semantic_similarity'), object) and hasattr(results.get('semantic_similarity'), 'item'):
                results['semantic_similarity'] = float(results['semantic_similarity'])
            
            # Save results to database
            analysis = ResumeAnalysis(
                session_id=analysis_id,
                original_filename=filename,
                results=results
            )
            db.session.add(analysis)
            db.session.commit()
            
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
    
    if not analysis_id:
        flash('No analysis results found. Please upload a resume first.', 'warning')
        return redirect(url_for('index'))
    
    # Get the most recent analysis for this session ID
    analysis = ResumeAnalysis.query.filter_by(session_id=analysis_id).order_by(ResumeAnalysis.created_at.desc()).first()
    
    if not analysis:
        flash('Analysis results not found. Please try again.', 'warning')
        return redirect(url_for('index'))
    
    # Convert DB model to dict for the template
    results = analysis.to_dict()
    return render_template('dashboard.html', results=results)

@app.route('/history')
def history():
    """View history of past analyses"""
    analysis_id = session.get('current_analysis_id')
    
    if not analysis_id:
        flash('No session found. Please upload a resume first.', 'warning')
        return redirect(url_for('index'))
    
    # Get all analyses for this session ID
    analyses = ResumeAnalysis.query.filter_by(session_id=analysis_id).order_by(ResumeAnalysis.created_at.desc()).all()
    
    if not analyses:
        flash('No analysis history found.', 'info')
        return redirect(url_for('index'))
    
    return render_template('history.html', analyses=analyses)

@app.route('/view_analysis/<int:analysis_id>')
def view_analysis(analysis_id):
    """View a specific analysis from history"""
    # Get the specific analysis
    analysis = ResumeAnalysis.query.get_or_404(analysis_id)
    
    # Security check - make sure this analysis belongs to the current session
    current_session_id = session.get('current_analysis_id')
    if not current_session_id or analysis.session_id != current_session_id:
        flash('You do not have permission to view this analysis.', 'danger')
        return redirect(url_for('index'))
    
    # Convert DB model to dict for the template
    results = analysis.to_dict()
    return render_template('dashboard.html', results=results)

@app.route('/api/results/<analysis_id>')
def get_results(analysis_id):
    """API endpoint to get analysis results"""
    # Try to find the analysis in the database
    analysis = ResumeAnalysis.query.filter_by(session_id=analysis_id).first()
    
    if analysis:
        return jsonify(analysis.to_dict())
    else:
        return jsonify({"error": "Analysis not found"}), 404

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    logging.error(f"Server error: {str(e)}")
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
