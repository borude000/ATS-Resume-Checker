# This file is for database models if needed in the future.
# For now, we're using in-memory storage as per requirements.

class ResumeAnalysis:
    """Model class for resume analysis results (currently just for reference)"""
    def __init__(self, resume_text, job_description, ats_score, keyword_matches, 
                 missing_keywords, structure_score, suggestions, overall_score):
        self.resume_text = resume_text
        self.job_description = job_description
        self.ats_score = ats_score
        self.keyword_matches = keyword_matches
        self.missing_keywords = missing_keywords
        self.structure_score = structure_score
        self.suggestions = suggestions
        self.overall_score = overall_score
