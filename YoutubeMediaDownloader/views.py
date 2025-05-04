"""
Views for YouTube Media Downloader Django integration.
"""
import os
import json
import logging
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.http import StreamingHttpResponse
from django.conf import settings
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .yt_downloader import get_available_streams

from .downloader import YouTubeDownloader

# Set up logging
logger = logging.getLogger(__name__)

# Create download directory
DOWNLOAD_DIR = getattr(settings, 'MEDIA_ROOT', os.path.join(settings.BASE_DIR, 'media/youtube_downloads'))
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Initialize YouTube downloader
downloader = YouTubeDownloader(download_dir=DOWNLOAD_DIR)

def youtube_downloader(request):
    """
    Main view for the YouTube downloader page.
    """
    return render(request, 'YoutubeMediaDownloader/index.html')

def video_page(request):
    """
    View for downloading individual YouTube videos.
    """
    if request.method == 'POST':
        video_url = request.POST.get('video_url')
        
        if not video_url:
            messages.error(request, 'Please enter a YouTube video URL')
            return redirect('youtube_media_downloader:video')
            
        try:
            # Get video info
            video_info = downloader.get_video_info(video_url)
            
            # Get available streams
            streams = downloader.get_available_streams(video_url)
            
            # Store in session
            request.session['video_url'] = video_url
            
            return render(request, 'YoutubeMediaDownloader/video.html', {
                'video_info': video_info,
                'streams': streams
            })
        except Exception as e:
            logger.error(f"Error processing video URL: {e}")
            error_msg = str(e)
            
            # Provide more user-friendly error messages
            if "Video unavailable" in error_msg:
                error_msg = "This video is unavailable. It might be private, deleted, or region-restricted."
            elif "Sign in" in error_msg:
                error_msg = "This video requires sign-in to access. It may be age-restricted content."
            
            messages.error(request, f'Error: {error_msg}')
            return redirect('youtube_media_downloader:video')
    
    return render(request, 'YoutubeMediaDownloader/video.html')

def playlist_page(request):
    """
    View for downloading YouTube playlists.
    """
    if request.method == 'POST':
        playlist_url = request.POST.get('playlist_url')
        
        if not playlist_url:
            messages.error(request, 'Please enter a YouTube playlist URL')
            return redirect('youtube_media_downloader:playlist')
            
        try:
            # Get playlist info
            playlist_info = downloader.get_playlist_info(playlist_url)
            
            # Store in session
            request.session['playlist_url'] = playlist_url
            
            return render(request, 'YoutubeMediaDownloader/playlist.html', {
                'playlist_info': playlist_info
            })
        except Exception as e:
            logger.error(f"Error processing playlist URL: {e}")
            error_msg = str(e)
            
            # Provide more user-friendly error messages
            if "Video unavailable" in error_msg:
                error_msg = "This playlist is unavailable. It might be private, deleted, or region-restricted."
            elif "Sign in" in error_msg:
                error_msg = "This playlist requires sign-in to access. It may contain age-restricted content."
            elif "This playlist does not exist" in error_msg:
                error_msg = "The playlist could not be found. Please check the URL and try again."
            
            messages.error(request, f'Error: {error_msg}')
            return redirect('youtube_media_downloader:playlist')
    
    return render(request, 'YoutubeMediaDownloader/playlist.html')

@csrf_exempt
def validate_url(request):
    """
    AJAX endpoint to validate a YouTube URL.
    """
    data = json.loads(request.body)
    url = data.get('url', '')
    is_valid = downloader.validate_youtube_url(url)
    return JsonResponse({'valid': is_valid})

def get_video_info(request):
    """
    Get YouTube video information based on URL.
    """
    video_url = request.GET.get('url')
    if not video_url:
        return JsonResponse({'error': 'Missing video URL'}, status=400)
        
    try:
        video_info = downloader.get_video_info(video_url)
        return JsonResponse(video_info)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@require_POST
def download_video(request):
    """
    Download a YouTube video directly to the user's browser using streaming.
    This method avoids using temporary files on disk.
    """
    video_url = request.session.get('video_url')
    format_id = request.POST.get('format_id')
    
    if not video_url or not format_id:
        messages.error(request, 'Missing required parameters for download')
        return redirect('youtube_media_downloader:video')
    
    try:
        # Get video info to prepare filename
        video_info = downloader.get_video_info(video_url)
        title = video_info.get('title', 'video')
        # Sanitize the title for filename
        import re
        title = re.sub(r'[\\/*?:"<>|]', '_', title)
        
        # Get stream info to determine file extension
        streams = downloader.get_available_streams(video_url)
        stream = next((s for s in streams if s.get('format_id') == format_id), None)
        
        if not stream:
            messages.error(request, 'Selected format is not available')
            return redirect('youtube_media_downloader:video')
        
        file_ext = stream.get('ext', 'mp4')
        is_audio = stream.get('is_audio', False)
        
        # Add appropriate extension based on format
        if is_audio:
            content_type = 'audio/mp3' if file_ext == 'mp3' else f'audio/{file_ext}'
        else:
            content_type = 'video/mp4' if file_ext == 'mp4' else f'video/{file_ext}'
        
        # Build a user-friendly filename with quotes for proper HTTP header handling
        filename = f"{title}.{file_ext}"
        
        # Create a streaming response using yt-dlp's direct stream
        import subprocess
        
        # Configure yt-dlp command for streaming
        yt_dlp_command = [
            'yt-dlp', 
            '-f', format_id, 
            '-o', '-',  # Output to stdout
            '--no-part',  # Don't use .part files
            '--no-cache-dir',  # Don't use cache
            video_url
        ]
        
        # Create a StreamingHttpResponse with the yt-dlp command output
        process = subprocess.Popen(
            yt_dlp_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            bufsize=10**8  # Use large buffer
        )
        
        # Function to stream process output
        def stream_response():
            while True:
                chunk = process.stdout.read(8192)
                if not chunk:
                    break
                yield chunk
            
            # Check for errors after streaming is complete
            stderr = process.stderr.read().decode('utf-8', errors='ignore')
            if process.wait() != 0 and stderr:
                logger.error(f"yt-dlp error: {stderr}")
        
        # Create streaming response with appropriate headers
        response = StreamingHttpResponse(
            stream_response(),
            content_type=content_type
        )
        
        # Properly format and escape the filename for Content-Disposition header
        # RFC 6266 compliant filename handling
        import urllib.parse
        ascii_filename = filename.encode('ascii', 'replace').decode()
        quoted_filename = urllib.parse.quote(filename)
        
        response['Content-Disposition'] = f'attachment; filename="{ascii_filename}"; filename*=UTF-8\'\'{quoted_filename}'
        
        return response
        
    except Exception as e:
        logger.error(f"Error downloading video: {e}")
        error_msg = str(e)
        
        # Provide more user-friendly error messages
        if "Permission denied" in error_msg:
            error_msg = "Permission denied. Please run this application with proper permissions."
        elif "Video unavailable" in error_msg:
            error_msg = "This video is unavailable. It might be private, deleted, or region-restricted."
        elif "Sign in" in error_msg:
            error_msg = "This video requires sign-in to access. It may be age-restricted content."
        elif "This video is not available" in error_msg:
            error_msg = "This video is not available for download due to restrictions."
        
        messages.error(request, f'Download failed: {error_msg}')
        return redirect('youtube_media_downloader:video')
    
def get_playlist_info(request):
    """
    Get YouTube playlist information based on URL.
    """
    playlist_url = request.GET.get('url')
    if not playlist_url:
        return JsonResponse({'error': 'Missing playlist URL'}, status=400)
        
    try:
        playlist_info = downloader.get_playlist_info(playlist_url)
        return JsonResponse(playlist_info)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@require_POST
def download_playlist(request):
    """
    Download a YouTube playlist.
    This creates a zip file with all downloaded videos and sends it to the user's browser.
    """
    playlist_url = request.session.get('playlist_url')
    quality = request.POST.get('quality', 'highest')
    
    if not playlist_url:
        messages.error(request, 'Missing playlist URL')
        return redirect('youtube_media_downloader:playlist')
    
    try:
        # Create a temporary directory with a unique name
        import tempfile
        import shutil
        import zipfile
        import uuid
        
        # Use the system's temporary directory with a custom filename
        temp_dir = tempfile.gettempdir()
        unique_dir = os.path.join(temp_dir, f"yt_playlist_{uuid.uuid4().hex}")
        os.makedirs(unique_dir, exist_ok=True)
        
        # Ensure the directory has proper permissions
        try:
            os.chmod(unique_dir, 0o755)  # rwxr-xr-x
        except:
            pass  # Continue if permission change fails
        
        logger.info(f"Created temporary directory for playlist download: {unique_dir}")
        
        # Download the playlist videos to the temporary directory
        results = downloader.download_playlist(playlist_url, unique_dir, quality)
        
        success_count = sum(1 for result in results if result.get('success', False))
        failed_count = len(results) - success_count
        
        if success_count == 0:
            # No videos were downloaded successfully
            shutil.rmtree(unique_dir)
            messages.error(request, 'Playlist download failed: No videos could be downloaded.')
            return redirect('youtube_media_downloader:playlist')
        
        # Get playlist info for the zip filename
        try:
            playlist_info = downloader.get_playlist_info(playlist_url)
            playlist_title = playlist_info.get('title', 'playlist').replace(' ', '_')
            # Sanitize filename
            import re
            playlist_title = re.sub(r'[\\/*?:"<>|]', '_', playlist_title)
        except:
            playlist_title = 'youtube_playlist'
        
        # Create a zip file for the downloaded videos
        zip_path = os.path.join(unique_dir, f"{playlist_title}.zip")
        
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for result in results:
                if result.get('success', False) and result.get('filepath'):
                    # Add file to zip
                    file_path = result.get('filepath')
                    zipf.write(file_path, os.path.basename(file_path))
        
        # Serve the zip file to the user as a direct download
        with open(zip_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/zip')
            response['Content-Disposition'] = f'attachment; filename="{playlist_title}.zip"'
            
            # Schedule cleanup of temporary files after sending
            import threading
            def cleanup():
                import time
                time.sleep(5)  # Wait longer for zip files which might be large
                try:
                    shutil.rmtree(unique_dir)
                    logger.info(f"Cleanup: Removed temporary directory {unique_dir}")
                except Exception as e:
                    logger.error(f"Cleanup: Failed to remove temporary directory {unique_dir}: {e}")
            
            threading.Thread(target=cleanup).start()
            
            return response
        
    except Exception as e:
        logger.error(f"Error downloading playlist: {e}")
        error_msg = str(e)
        
        # Provide more user-friendly error messages
        if "Permission denied" in error_msg:
            error_msg = "Permission denied while creating temporary files. Please check your system's temporary directory permissions."
        elif "Video unavailable" in error_msg:
            error_msg = "One or more videos in the playlist are unavailable."
        elif "Sign in" in error_msg:
            error_msg = "This playlist contains age-restricted videos that require sign-in."
        elif "This video is not available" in error_msg:
            error_msg = "Some videos in this playlist are not available for download."
        
        messages.error(request, f'Playlist download failed: {error_msg}')
        return redirect('youtube_media_downloader:playlist')
    """
    Download a YouTube playlist.
    This creates a zip file with all downloaded videos and sends it to the user's browser.
    """
    playlist_url = request.session.get('playlist_url')
    quality = request.POST.get('quality', 'highest')
    
    if not playlist_url:
        messages.error(request, 'Missing playlist URL')
        return redirect('youtube_media_downloader:playlist')
    
    try:
        # Create a temporary directory with a unique name
        import tempfile
        import shutil
        import zipfile
        import uuid
        
        # Use the system's temporary directory with a custom filename
        temp_dir = tempfile.gettempdir()
        unique_dir = os.path.join(temp_dir, f"yt_playlist_{uuid.uuid4().hex}")
        os.makedirs(unique_dir, exist_ok=True)
        
        # Ensure the directory has proper permissions
        try:
            os.chmod(unique_dir, 0o755)  # rwxr-xr-x
        except:
            pass  # Continue if permission change fails
        
        logger.info(f"Created temporary directory for playlist download: {unique_dir}")
        
        # Download the playlist videos to the temporary directory
        results = downloader.download_playlist(playlist_url, unique_dir, quality)
        
        success_count = sum(1 for result in results if result.get('success', False))
        failed_count = len(results) - success_count
        
        if success_count == 0:
            # No videos were downloaded successfully
            shutil.rmtree(unique_dir)
            messages.error(request, 'Playlist download failed: No videos could be downloaded.')
            return redirect('youtube_media_downloader:playlist')
        
        # Get playlist info for the zip filename
        try:
            playlist_info = downloader.get_playlist_info(playlist_url)
            playlist_title = playlist_info.get('title', 'playlist').replace(' ', '_')
            # Sanitize filename
            import re
            playlist_title = re.sub(r'[\\/*?:"<>|]', '_', playlist_title)
        except:
            playlist_title = 'youtube_playlist'
        
        # Create a zip file for the downloaded videos
        zip_path = os.path.join(unique_dir, f"{playlist_title}.zip")
        
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for result in results:
                if result.get('success', False) and result.get('filepath'):
                    # Add file to zip
                    file_path = result.get('filepath')
                    zipf.write(file_path, os.path.basename(file_path))
        
        # Serve the zip file to the user as a direct download
        with open(zip_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/zip')
            response['Content-Disposition'] = f'attachment; filename="{playlist_title}.zip"'
            
            # Schedule cleanup of temporary files after sending
            import threading
            def cleanup():
                import time
                time.sleep(5)  # Wait longer for zip files which might be large
                try:
                    shutil.rmtree(unique_dir)
                    logger.info(f"Cleanup: Removed temporary directory {unique_dir}")
                except Exception as e:
                    logger.error(f"Cleanup: Failed to remove temporary directory {unique_dir}: {e}")
            
            threading.Thread(target=cleanup).start()
            
            return response
        
    except Exception as e:
        logger.error(f"Error downloading playlist: {e}")
        error_msg = str(e)
        
        # Provide more user-friendly error messages
        if "Permission denied" in error_msg:
            error_msg = "Permission denied while creating temporary files. Please check your system's temporary directory permissions."
        elif "Video unavailable" in error_msg:
            error_msg = "One or more videos in the playlist are unavailable."
        elif "Sign in" in error_msg:
            error_msg = "This playlist contains age-restricted videos that require sign-in."
        elif "This video is not available" in error_msg:
            error_msg = "Some videos in this playlist are not available for download."
        
        messages.error(request, f'Playlist download failed: {error_msg}')
        return redirect('youtube_media_downloader:playlist')
    """
    Download a YouTube playlist.
    This creates a zip file with all downloaded videos and sends it to the user's browser.
    """
    playlist_url = request.session.get('playlist_url')
    quality = request.POST.get('quality', 'highest')
    
    if not playlist_url:
        messages.error(request, 'Missing playlist URL')
        return redirect('youtube_media_downloader:playlist')
    
    try:
        # Create a temporary directory for the downloads
        import tempfile
        import shutil
        import zipfile
        
        temp_dir = tempfile.mkdtemp()
        logger.info(f"Created temporary directory for playlist download: {temp_dir}")
        
        # Download the playlist videos to the temporary directory
        results = downloader.download_playlist(playlist_url, temp_dir, quality)
        
        success_count = sum(1 for result in results if result.get('success', False))
        failed_count = len(results) - success_count
        
        if success_count == 0:
            # No videos were downloaded successfully
            shutil.rmtree(temp_dir)
            messages.error(request, 'Playlist download failed: No videos could be downloaded.')
            return redirect('youtube_media_downloader:playlist')
        
        # Get playlist info for the zip filename
        try:
            playlist_info = downloader.get_playlist_info(playlist_url)
            playlist_title = playlist_info.get('title', 'playlist').replace(' ', '_')
            # Sanitize filename
            import re
            playlist_title = re.sub(r'[\\/*?:"<>|]', '_', playlist_title)
        except:
            playlist_title = 'youtube_playlist'
        
        # Create a zip file for the downloaded videos
        zip_path = os.path.join(temp_dir, f"{playlist_title}.zip")
        
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for result in results:
                if result.get('success', False) and result.get('filepath'):
                    # Add file to zip
                    file_path = result.get('filepath')
                    zipf.write(file_path, os.path.basename(file_path))
        
        # Serve the zip file to the user as a direct download
        with open(zip_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/zip')
            response['Content-Disposition'] = f'attachment; filename="{playlist_title}.zip"'
            
            # Schedule cleanup of temporary files after sending
            import threading
            def cleanup():
                import time
                time.sleep(5)  # Wait longer for zip files which might be large
                try:
                    shutil.rmtree(temp_dir)
                    logger.info(f"Cleanup: Removed temporary directory {temp_dir}")
                except Exception as e:
                    logger.error(f"Cleanup: Failed to remove temporary directory {temp_dir}: {e}")
            
            threading.Thread(target=cleanup).start()
            
            return response
        
    except Exception as e:
        logger.error(f"Error downloading playlist: {e}")
        error_msg = str(e)
        
        # Provide more user-friendly error messages
        if "Video unavailable" in error_msg:
            error_msg = "One or more videos in the playlist are unavailable."
        elif "Sign in" in error_msg:
            error_msg = "This playlist contains age-restricted videos that require sign-in."
        elif "This video is not available" in error_msg:
            error_msg = "Some videos in this playlist are not available for download."
        
        messages.error(request, f'Playlist download failed: {error_msg}')
        return redirect('youtube_media_downloader:playlist')
    
def audio_page(request):
    """
    View for streaming YouTube audio.
    """
    if request.method == 'POST':
        video_url = request.POST.get('video_url')

        if not video_url:
            messages.error(request, 'Please enter a YouTube video URL')
            return redirect('youtube_media_downloader:audio')

        try:
            # Get available streams and find the best audio stream
            streams = get_available_streams(video_url)
            best_audio_stream = next((s for s in streams if s.get('is_audio', False)), None)

            if not best_audio_stream:
                raise Exception("No suitable audio stream found.")

            # Pass the audio URL to the template
            audio_url = best_audio_stream.get('url')
            return render(request, 'YoutubeMediaDownloader/audio.html', {'audio_url': audio_url})

        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
            return redirect('youtube_media_downloader:audio')

    return render(request, 'YoutubeMediaDownloader/audio.html')