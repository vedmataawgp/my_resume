from django.shortcuts import render
from django.http import JsonResponse
from django.core.files.storage import FileSystemStorage
from .models import ResumeAnalysis
from .resume_analyzer import extract_text_from_pdf, extract_text_from_docx
from textblob import TextBlob
from utils import get_improvement_suggestions
import spacy


def upload_resume(request):
    if request.method == 'POST' and request.FILES.get('resume'):
        resume_file = request.FILES['resume']
        fs = FileSystemStorage()
        filename = fs.save(resume_file.name, resume_file)
        file_path = fs.path(filename)

        # Extract text based on file type
        if filename.endswith('.pdf'):
            resume_text = extract_text_from_pdf(file_path)
        elif filename.endswith('.docx'):
            resume_text = extract_text_from_docx(file_path)
        else:
            return JsonResponse({'error': 'Invalid file format'}, status=400)

        # Analyze resume
        analysis = analyze_resume(resume_text)

        # Add derived values to the analysis
        analysis['experience_score'] = analysis.get('experience', 0) * 10


        # Generate suggestions
        analysis['suggestions'] = get_improvement_suggestions(analysis)

        # Clean up
        fs.delete(filename)

        return render(request, 'analyser/results.html', {'analysis': analysis})

    return render(request, 'analyser/upload.html')

def analysis_history(request):
    email = request.GET.get('email')
    if email:
        analyses = ResumeAnalysis.objects.filter(user_email=email)
        return render(request, 'analyser/history.html', {'analyses': analyses})
    return render(request, 'analyser/history.html', {'analyses': []})

def analyze_resume(text):
    # Initialize NLP tools
    nlp = spacy.load('en_core_web_sm')

    # Basic analysis
    doc = nlp(text)

    # Extract named entities
    entities = [(ent.text, ent.label_) for ent in doc.ents if ent.label_ in ['PERSON', 'ORG', 'GPE', 'DATE', 'LANGUAGE']]

    # Extract skills (filter nouns and proper nouns)
    skills = [token.text for token in doc if token.pos_ in ['NOUN', 'PROPN'] and len(token.text) > 2]

    # Calculate grammar score using TextBlob
    blob = TextBlob(text)
    grammar_errors = len(blob.correct().split()) - len(text.split())  # Approximate grammar error count
    grammar_score = max(0, 100 - (grammar_errors * 5))

    # Calculate keyword density (example logic)
    keywords = ['Python', 'Django', 'JavaScript', 'Teaching', 'Mentor', 'Physics', 'Chemistry']
    keyword_count = sum(text.lower().count(keyword.lower()) for keyword in keywords)
    keyword_density = (keyword_count / len(doc)) * 100 if len(doc) > 0 else 0

    # Example missing skills
    missing_skills = [keyword for keyword in keywords if keyword.lower() not in text.lower()]

    # Example experience and education level
    experience = 3.0  # Example: Extracted from text
    education_level = 'Bachelor'  # Example: Extracted from text

    # Calculate skill score (based on the number of extracted skills)
    skill_score = min(len(skills) * 10, 100)  # Example: Each skill contributes 10 points, capped at 100

    # Overall score (weighted average)
    overall_score = (grammar_score * 0.3) + (keyword_density * 0.4) + (experience * 10)

    # Calculate word count and sentence count
    word_count = len([token for token in doc if not token.is_punct])  # Exclude punctuation
    sentence_count = len(list(doc.sents))  # Count sentences

    return {
        'entities': entities,
        'skills': skills[:10],  # Limit to top 10 skills
        'missing_skills': missing_skills,
        'experience': experience,
        'education_level': education_level,
        'grammar_score': grammar_score,
        'keyword_density': keyword_density,
        'skill_score': skill_score,  # Add skill_score
        'overall_score': overall_score,
        'word_count': word_count,  # Add word count
        'sentence_count': sentence_count  # Add sentence count
    }

def get_improvement_suggestions(analysis):
    suggestions = {}

    # Grammar suggestions
    if analysis['grammar_score'] < 80:
        suggestions['Grammar'] = [
            'Improve grammar to increase your score.',
            'Avoid common grammatical errors.'
        ]

    # Skill suggestions
    if analysis['skill_score'] < 80:
        suggestions['Skills'] = [
            'Add more relevant skills to your resume.',
            f"Consider adding these skills: {', '.join(analysis['missing_skills'])}"
        ]

    # Keyword density suggestions
    if analysis['keyword_density'] < 50:
        suggestions['Keywords'] = [
            'Increase the use of relevant keywords in your resume.',
            'Focus on including industry-specific terms.'
        ]

    # Experience suggestions
    if analysis['experience'] < 5:
        suggestions['Experience'] = [
            'Highlight more of your professional experience.',
            'Include specific achievements and responsibilities.'
        ]

    return suggestions
