import spacy
import re
import logging
from collections import Counter
import fitz  # PyMuPDF
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class ResumeAnalyzer:
    """Class to analyze resumes against job descriptions"""
    
    def __init__(self):
        """Initialize the ResumeAnalyzer with required NLP models"""
        try:
            # Load SpaCy model for NLP
            self.nlp = spacy.load("en_core_web_sm")
            logging.info("Successfully loaded SpaCy model")
        except OSError:
            # If the model is not downloaded, download it
            logging.warning("SpaCy model not found. Downloading...")
            from spacy.cli import download
            download("en_core_web_sm")
            self.nlp = spacy.load("en_core_web_sm")
            logging.info("Successfully downloaded and loaded SpaCy model")
    
    def extract_text_from_pdf(self, pdf_path):
        """Extract text from a PDF file"""
        text = ""
        try:
            # Open the PDF file
            doc = fitz.open(pdf_path)
            
            # Iterate through pages and extract text
            for page in doc:
                text += page.get_text()
            
            return text
        except Exception as e:
            logging.error(f"Error extracting text from PDF: {str(e)}")
            raise
    
    def preprocess_text(self, text):
        """Clean and preprocess text"""
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters, keeping alphanumeric and spaces
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def extract_keywords(self, text):
        """Extract important keywords from text using SpaCy"""
        # Process the text with SpaCy
        doc = self.nlp(text)
        
        # Extract nouns, verbs, and proper nouns as potential keywords
        keywords = []
        for token in doc:
            if token.pos_ in ['NOUN', 'PROPN', 'VERB'] and not token.is_stop:
                keywords.append(token.lemma_)
        
        # Count keyword frequencies
        keyword_freq = Counter(keywords)
        
        # Return the most common keywords
        return dict(keyword_freq.most_common(30))
    
    def calculate_keyword_match(self, resume_keywords, job_keywords):
        """Calculate keyword match percentage between resume and job description"""
        # Get unique keywords
        resume_kw_set = set(resume_keywords.keys())
        job_kw_set = set(job_keywords.keys())
        
        # Find matches and missing keywords
        matches = resume_kw_set.intersection(job_kw_set)
        missing = job_kw_set - resume_kw_set
        
        # Calculate percentage match
        match_percentage = len(matches) / len(job_kw_set) * 100 if job_kw_set else 0
        
        return {
            'match_percentage': match_percentage,
            'matched_keywords': list(matches),
            'missing_keywords': list(missing)
        }
    
    def check_ats_compatibility(self, text):
        """Check ATS compatibility of the resume"""
        issues = []
        score = 100
        
        # Check for common ATS issues
        
        # 1. Check for tables (simplistic check)
        if '|' in text or '+---+' in text:
            issues.append("Resume might contain tables which can confuse ATS systems.")
            score -= 15
        
        # 2. Check for headers/footers (simplistic check)
        if re.search(r'page \d+ of \d+', text, re.IGNORECASE):
            issues.append("Resume might contain headers/footers which can confuse ATS systems.")
            score -= 10
        
        # 3. Check for uncommon section headings
        common_sections = ['education', 'experience', 'skills', 'summary', 'objective', 'projects', 'certifications']
        found_sections = [section for section in common_sections if re.search(r'\b' + section + r'\b', text, re.IGNORECASE)]
        
        if len(found_sections) < 3:  # If less than 3 common sections found
            issues.append("Resume might be missing standard section headings that ATS systems expect.")
            score -= 15
        
        # 4. Check for email and phone number
        if not re.search(r'[\w\.-]+@[\w\.-]+', text):
            issues.append("No email address found. ATS might not be able to capture your contact information.")
            score -= 10
        
        if not re.search(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', text):
            issues.append("No phone number found. ATS might not be able to capture your contact information.")
            score -= 10
        
        # Cap the score at 0
        score = max(0, score)
        
        return {
            'score': score,
            'issues': issues
        }
    
    def assess_resume_structure(self, text):
        """Assess the structure and formatting of the resume"""
        structure_issues = []
        score = 100
        
        # Check resume length (rough estimate based on character count)
        char_count = len(text)
        if char_count < 2000:
            structure_issues.append("Resume seems too short. Consider adding more details about your experience and skills.")
            score -= 15
        elif char_count > 8000:
            structure_issues.append("Resume seems too long. Consider condensing to focus on the most relevant information.")
            score -= 10
        
        # Check for bullet points
        bullet_count = len(re.findall(r'•|\*|-', text))
        if bullet_count < 5:
            structure_issues.append("Few or no bullet points detected. Using bullet points can make your resume more scannable.")
            score -= 10
        
        # Check for section consistency
        sections = re.findall(r'\n([A-Z][A-Z\s]+)(?:\n|:)', text)
        if len(sections) < 3:
            structure_issues.append("Few distinct sections detected. Organize your resume with clear section headings.")
            score -= 15
        
        # Check for dates in experience section
        date_pattern = r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}\b'
        dates = re.findall(date_pattern, text, re.IGNORECASE)
        if len(dates) < 2:
            structure_issues.append("Few or no dates found. Include clear employment dates for each position.")
            score -= 10
        
        # Cap the score at 0
        score = max(0, score)
        
        return {
            'score': score,
            'issues': structure_issues
        }
    
    def generate_suggestions(self, ats_check, keyword_match, structure_assessment):
        """Generate improvement suggestions based on analysis"""
        suggestions = []
        
        # Add ATS compatibility suggestions
        suggestions.extend(ats_check['issues'])
        
        # Add keyword match suggestions
        if keyword_match['match_percentage'] < 70:
            top_missing = keyword_match['missing_keywords'][:5]  # Get top 5 missing keywords
            if top_missing:
                suggestions.append(f"Consider adding these keywords from the job description: {', '.join(top_missing)}")
        
        # Add structure suggestions
        suggestions.extend(structure_assessment['issues'])
        
        # Add general suggestions if few specific ones were found
        if len(suggestions) < 3:
            suggestions.append("Quantify your achievements with numbers and metrics")
            suggestions.append("Tailor your resume specifically for each job application")
            suggestions.append("Use action verbs at the beginning of bullet points")
        
        return suggestions
    
    def calculate_semantic_similarity(self, resume_text, job_description):
        """Calculate semantic similarity between resume and job description using TF-IDF"""
        try:
            # Create TF-IDF vectorizer
            vectorizer = TfidfVectorizer()
            
            # Transform texts to TF-IDF vectors
            tfidf_matrix = vectorizer.fit_transform([resume_text, job_description])
            
            # Calculate cosine similarity
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            
            # Convert to percentage
            similarity_percentage = similarity * 100
            
            return similarity_percentage
        except Exception as e:
            logging.error(f"Error calculating semantic similarity: {str(e)}")
            return 0
    
    def calculate_overall_score(self, ats_score, keyword_match_percentage, structure_score, semantic_similarity):
        """Calculate overall resume quality score"""
        # Weighted average of different scores
        weights = {
            'ats_score': 0.25,
            'keyword_match': 0.30,
            'structure_score': 0.20,
            'semantic_similarity': 0.25
        }
        
        overall_score = (
            ats_score * weights['ats_score'] +
            keyword_match_percentage * weights['keyword_match'] +
            structure_score * weights['structure_score'] +
            semantic_similarity * weights['semantic_similarity']
        )
        
        # Round to nearest integer
        return round(overall_score)
    
    def analyze_resume(self, pdf_path, job_description):
        """Main method to analyze a resume against a job description"""
        # Extract text from PDF
        resume_text = self.extract_text_from_pdf(pdf_path)
        
        # Preprocess texts
        processed_resume = self.preprocess_text(resume_text)
        processed_job = self.preprocess_text(job_description)
        
        # Extract keywords
        resume_keywords = self.extract_keywords(processed_resume)
        job_keywords = self.extract_keywords(processed_job)
        
        # Calculate keyword match
        keyword_match = self.calculate_keyword_match(resume_keywords, job_keywords)
        
        # Check ATS compatibility
        ats_check = self.check_ats_compatibility(resume_text)
        
        # Assess resume structure
        structure_assessment = self.assess_resume_structure(resume_text)
        
        # Calculate semantic similarity
        semantic_similarity = self.calculate_semantic_similarity(processed_resume, processed_job)
        
        # Generate suggestions
        suggestions = self.generate_suggestions(ats_check, keyword_match, structure_assessment)
        
        # Calculate overall score
        overall_score = self.calculate_overall_score(
            ats_check['score'], 
            keyword_match['match_percentage'], 
            structure_assessment['score'],
            semantic_similarity
        )
        
        # Create summary of sections found in resume
        section_pattern = r'\n([A-Z][A-Z\s]+)(?:\n|:)'
        sections_found = re.findall(section_pattern, resume_text)
        sections_summary = [section.strip() for section in sections_found]
        
        # Prepare the final results
        results = {
            'overall_score': overall_score,
            'ats_compatibility': {
                'score': ats_check['score'],
                'issues': ats_check['issues']
            },
            'keyword_match': {
                'percentage': keyword_match['match_percentage'],
                'matched_keywords': keyword_match['matched_keywords'],
                'missing_keywords': keyword_match['missing_keywords']
            },
            'structure_assessment': {
                'score': structure_assessment['score'],
                'issues': structure_assessment['issues']
            },
            'semantic_similarity': semantic_similarity,
            'resume_keywords': list(resume_keywords.keys()),
            'job_keywords': list(job_keywords.keys()),
            'suggestions': suggestions,
            'sections_found': sections_summary,
            # Include sample of resume text for display (first 500 chars)
            'resume_preview': resume_text[:500] + ('...' if len(resume_text) > 500 else '')
        }
        
        return results
