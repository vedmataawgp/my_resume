def get_color_based_on_score(score):
    """
    Return a color based on the score value
    """
    if score < 60:
        return "#FF6B6B"  # Red
    elif score < 80:
        return "#FFD166"  # Yellow
    else:
        return "#06D6A0"  # Green

def get_improvement_suggestions(analysis):
    """
    Generate improvement suggestions based on analysis results
    """
    suggestions = {
        "Skills": [],
        "Experience": [],
        "Education": [],
        "Formatting": [],
        "Keywords": []
    }
    
    # Skills suggestions
    if analysis["skill_score"] < 70:
        suggestions["Skills"].append("Add more relevant technical skills to your resume")
    if analysis["missing_skills"]:
        suggestions["Skills"].append(f"Consider adding these skills if you have them: {', '.join(analysis['missing_skills'])}")
    
    # Experience suggestions
    if analysis["experience_score"] < 60:
        suggestions["Experience"].append("Quantify your achievements with numbers and metrics")
        suggestions["Experience"].append("Use action verbs to describe your responsibilities")
    
    # Education suggestions
    if analysis["education_score"] < 70:
        suggestions["Education"].append("List relevant courses, projects, or academic achievements")
        suggestions["Education"].append("Include GPA if it's above 3.5")
    
    # Formatting suggestions
    if analysis["formatting_score"] < 70:
        suggestions["Formatting"].append("Check for grammar and spelling errors")
        suggestions["Formatting"].append("Use consistent formatting for dates, headings, and bullet points")
        suggestions["Formatting"].append("Ensure appropriate spacing and margins throughout the document")
    
    # Keywords suggestions
    if analysis["keyword_score"] < 70:
        suggestions["Keywords"].append("Include more industry-specific keywords")
        suggestions["Keywords"].append("Match keywords from job descriptions you're applying to")
        suggestions["Keywords"].append("Use action verbs like 'achieved', 'implemented', 'developed'")
    
    # Add default suggestions if any category is empty
    for category, category_suggestions in suggestions.items():
        if not category_suggestions:
            if category == "Skills":
                suggestions[category].append("Organize skills by categories (technical, soft, domain)")
            elif category == "Experience":
                suggestions[category].append("Focus on achievements rather than responsibilities")
            elif category == "Education":
                suggestions[category].append("List education in reverse chronological order")
            elif category == "Formatting":
                suggestions[category].append("Use a clean, professional template")
            elif category == "Keywords":
                suggestions[category].append("Tailor keywords to the specific job description")
    
    return suggestions
