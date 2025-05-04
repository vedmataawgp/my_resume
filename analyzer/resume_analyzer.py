
import PyPDF2
from docx import Document
import spacy
import nltk
from nltk.tokenize import word_tokenize
from language_tool_python import LanguageTool


# Download required NLTK data
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')

def extract_text_from_pdf(file_path):
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ''
        for page in reader.pages:
            text += page.extract_text()
    return text

def extract_text_from_docx(file_path):
    doc = Document(file_path)
    return ' '.join([paragraph.text for paragraph in doc.paragraphs])

def analyze_resume(text):
    # Initialize NLP tools
    nlp = spacy.load('en_core_web_sm')
    tool = LanguageTool('en-US')

    # Basic analysis
    doc = nlp(text)
    
    # Extract skills (simplified version)
    skills = [ent.text for ent in doc.ents if ent.label_ in ['ORG', 'PRODUCT']]
    
    # Calculate scores
    grammar_errors = len(tool.check(text))
    grammar_score = max(0, 100 - (grammar_errors * 5))
    
    return {
        'skills': skills,
        'missing_skills': ['Python', 'Django', 'JavaScript'],  # Example missing skills
        'experience': 75.0,  # Example score
        'education_level': 'Bachelor',  # Example
        'grammar_score': grammar_score,
        'keyword_density': 80.0,  # Example score
        'overall_score': 85.0  # Example score
    }
