from django.db import models

class ResumeAnalysis(models.Model):
    filename = models.CharField(max_length=255)
    file_type = models.CharField(max_length=10)
    user_email = models.EmailField(null=True, blank=True)
    entities = models.JSONField()  # because entities is a list of tuples
    skills = models.JSONField()
    missing_skills = models.JSONField(null=True, blank=True, default=list)  # Allow null and set default
    word_count = models.IntegerField()
    sentence_count = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    experience = models.FloatField(null=True, blank=True)
    education_level = models.CharField(max_length=100, null=True, blank=True)
    grammar_score = models.FloatField(null=True, blank=True)
    keyword_density = models.FloatField(null=True, blank=True)
    overall_score = models.FloatField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']