from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
import re
import os
import uuid
import json

from .models import SearchHistory, VideoHistory, Video
from .utils import search_youtube, get_video_info

def get_or_create_session_id(request):
    """Get the current session ID or create a new one if it doesn't exist"""
    if 'session_id' not in request.session:
        request.session['session_id'] = str(uuid.uuid4())
    return request.session['session_id']

def home(request):
    """Home page for YouTube link input"""
    # Get recent video history instead of searches
    recent_videos = VideoHistory.objects.order_by('-viewed_at')[:5]
    return render(request, 'ysearchplay/yt_home.html', {
        'recent_videos': recent_videos,
    })

@require_http_methods(["GET", "POST"])
def search(request):
    """Process YouTube direct link"""
    session_id = get_or_create_session_id(request)
    
    if request.method == 'POST':
        query = request.POST.get('q', '')
        
        # Save to history
        if query:
            SearchHistory.objects.create(
                session_id=session_id,
                query=query
            )
            
            # Extract YouTube video ID from URL
            video_id_match = re.search(r'(?:youtube\.com\/(?:[^\/]+\/.+\/|(?:v|e(?:mbed)?)\/|.*[?&]v=)|youtu\.be\/)([^"&?\/\s]{11})', query)
            
            if video_id_match:
                video_id = video_id_match.group(1)
                return redirect('ysearchplay:play', video_id=video_id)
            else:
                # Not a valid YouTube URL
                messages.error(request, "Please enter a valid YouTube URL.")
    
    return redirect('ysearchplay:home')

# Search results functionality has been removed

def play(request, video_id):
    """Play a YouTube video with ad simulation"""
    session_id = get_or_create_session_id(request)
    
    # Get video info
    video_info = get_video_info(video_id)
    
    if video_info:
        # Save to watch history
        VideoHistory.objects.create(
            session_id=session_id,
            video_id=video_id,
            video_title=video_info.get('title', 'Unknown Video')
        )
        
        # Save to videos if not exists
        if not Video.objects.filter(youtube_id=video_id).exists():
            Video.objects.create(
                youtube_id=video_id,
                title=video_info.get('title', 'Unknown Video'),
                channel=video_info.get('channel', 'Unknown Channel'),
                thumbnail_url=video_info.get('thumbnail_url', ''),
                duration=video_info.get('duration', ''),
                views=video_info.get('views', '')
            )
    
    return render(request, 'ysearchplay/play.html', {
        'video_id': video_id,
        'video_info': video_info,
    })

def history(request):
    """View search and watch history"""
    session_id = get_or_create_session_id(request)
    search_history = SearchHistory.objects.filter(session_id=session_id).order_by('-timestamp')
    video_history = VideoHistory.objects.filter(session_id=session_id).order_by('-viewed_at')
    
    return render(request, 'ysearchplay/history.html', {
        'search_history': search_history,
        'video_history': video_history,
    })

@staff_member_required
def download_video(request, video_id):
    """Download a YouTube video (admin only)"""
    from pytube import YouTube
    
    try:
        yt = YouTube(f"https://www.youtube.com/watch?v={video_id}")
        stream = yt.streams.get_highest_resolution()
        
        # Ensure media directory exists
        os.makedirs(os.path.join(settings.MEDIA_ROOT, 'downloads'), exist_ok=True)
        
        # Download the video
        file_path = stream.download(output_path=os.path.join(settings.MEDIA_ROOT, 'downloads'))
        
        # Return success message
        messages.success(request, f"Video '{yt.title}' downloaded successfully!")
        return JsonResponse({'status': 'success', 'message': 'Video downloaded successfully'})
    except Exception as e:
        messages.error(request, f"Error downloading video: {str(e)}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
