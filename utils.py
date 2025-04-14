import os

def allowed_file(filename):
    """Check if the uploaded file is a PDF"""
    ALLOWED_EXTENSIONS = {'pdf'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
