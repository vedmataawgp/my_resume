"""
URL patterns for YouTube Media Downloader app.
"""
from django.urls import path
from . import views

app_name = 'youtube_media_downloader'

urlpatterns = [
    # Main pages
    path('', views.youtube_downloader, name='index'),
    path('video/', views.video_page, name='video'),
    path('playlist/', views.playlist_page, name='playlist'),
    
    # API endpoints
    path('api/validate-url/', views.validate_url, name='validate_url'),
    path('api/video/info/', views.get_video_info, name='get_video_info'),
    path('video/download/', views.download_video, name='download_video'),
    path('api/playlist/info/', views.get_playlist_info, name='get_playlist_info'),
    path('playlist/download/', views.download_playlist, name='download_playlist'),
    path('audio/', views.audio_page, name='audio'),
]