from django.db import models
from django.utils import timezone
import uuid

class SearchHistory(models.Model):
    session_id = models.CharField(max_length=100, blank=True)
    query = models.CharField(max_length=255)
    timestamp = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"{self.query} ({self.timestamp})"
    
    class Meta:
        verbose_name_plural = "Search Histories"
        ordering = ['-timestamp']

class VideoHistory(models.Model):
    session_id = models.CharField(max_length=100, blank=True)
    video_id = models.CharField(max_length=20)
    video_title = models.CharField(max_length=255)
    viewed_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"{self.video_title} ({self.viewed_at})"
    
    class Meta:
        verbose_name_plural = "Video Histories"
        ordering = ['-viewed_at']

class Video(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    youtube_id = models.CharField(max_length=20)
    title = models.CharField(max_length=255)
    channel = models.CharField(max_length=255)
    thumbnail_url = models.URLField()
    duration = models.CharField(max_length=20, blank=True)
    views = models.CharField(max_length=20, blank=True)
    added_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-added_at']
