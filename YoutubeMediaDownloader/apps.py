"""
Application configuration for YouTube Media Downloader.
"""
from django.apps import AppConfig

class YoutubeMediaDownloaderConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'YoutubeMediaDownloader'
    verbose_name = 'YouTube Media Downloader'