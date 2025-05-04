"""
YouTube downloader using yt-dlp instead of pytube.
This module provides reliable functions to download YouTube videos and playlists.
"""
import os
import re
import logging
from datetime import timedelta

import yt_dlp
from yt_dlp.utils import DownloadError

# Set up logging
logger = logging.getLogger(__name__)

def validate_youtube_url(url):
    """
    Validate if a URL is a valid YouTube URL.
    
    Args:
        url (str): URL to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not url:
        return False
        
    # YouTube video patterns
    video_patterns = [
        r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/watch\?v=([a-zA-Z0-9_-]+)',
        r'(?:https?:\/\/)?(?:www\.)?youtu\.be\/([a-zA-Z0-9_-]+)'
    ]
    
    # YouTube playlist pattern
    playlist_pattern = r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/playlist\?list=([a-zA-Z0-9_-]+)'
    
    # Check if URL matches any pattern
    for pattern in video_patterns:
        if re.match(pattern, url):
            return True
            
    if re.match(playlist_pattern, url):
        return True
        
    return False

def get_video_info(video_url):
    """
    Get information about a YouTube video using yt-dlp.
    
    Args:
        video_url (str): YouTube video URL
        
    Returns:
        dict: Video information including title, author, duration, etc.
    """
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'skip_download': True,
        'format': 'best',
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            
            # Format duration as string
            duration = info.get('duration', 0)
            duration_string = str(timedelta(seconds=duration))
            if duration_string.startswith('0:'):
                duration_string = duration_string[2:]
            
            # Get file size (approximate)
            filesize = info.get('filesize') or info.get('filesize_approx')
            if filesize:
                filesize_mb = filesize / (1024 * 1024)  # Convert to MB
            else:
                filesize_mb = None
                
            return {
                'id': info.get('id'),
                'title': info.get('title'),
                'author': info.get('uploader'),
                'duration': duration,
                'duration_string': duration_string,
                'thumbnail_url': info.get('thumbnail'),
                'description': info.get('description'),
                'view_count': info.get('view_count'),
                'upload_date': info.get('upload_date'),
                'filesize_mb': filesize_mb,
                'is_live': info.get('is_live', False),
                'formats': len(info.get('formats', [])),
            }
    except Exception as e:
        logger.error(f"Error getting video info: {e}")
        raise Exception(f"Could not get video information: {str(e)}")

def get_available_streams(video_url):
    """
    Get available streams for a YouTube video using yt-dlp.
    Return 360p video streams with audio and audio-only streams (excluding mp4 audio).
    
    Args:
        video_url (str): YouTube video URL
        
    Returns:
        list: Available stream information (360p video with audio and audio-only streams with size)
    """
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'skip_download': True,
        'format': 'best',
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            formats = info.get('formats', [])
            
            # Filter for 360p video streams with audio
            video_streams = []
            for f in formats:
                if f.get('height') == 360 and f.get('vcodec') != 'none' and f.get('acodec') != 'none':
                    # Calculate approximate file size if available
                    filesize = f.get('filesize') or f.get('filesize_approx')
                    if filesize:
                        filesize_mb = filesize / (1024 * 1024)  # Convert to MB
                    else:
                        filesize_mb = None
                    
                    # Build stream info
                    stream_info = {
                        'format_id': f.get('format_id'),
                        'format_note': 'Video with Audio (360p)',
                        'ext': f.get('ext'),
                        'resolution': f"{f.get('width', 0)}x{f.get('height', 0)}",
                        'fps': f.get('fps'),
                        'filesize': filesize,
                        'filesize_mb': filesize_mb,
                        'tbr': f.get('tbr'),  # Total bitrate
                        'acodec': f.get('acodec'),
                        'vcodec': f.get('vcodec'),
                        'abr': f.get('abr'),  # Audio bitrate
                        'vbr': f.get('vbr'),  # Video bitrate
                        'quality': "360p",
                        'format': f.get('format'),
                        'video_ext': f.get('video_ext', 'mp4'),
                        'is_video': True
                    }
                    
                    # Add to streams list
                    video_streams.append(stream_info)
            
            # Filter for audio-only streams with size and exclude mp4 audio
            audio_streams = []
            for f in formats:
                if (
                    f.get('vcodec') == 'none' and  # Audio-only
                    f.get('acodec') != 'none' and  # Has audio codec
                    f.get('ext') != 'mp4' and  # Exclude mp4 audio
                    (f.get('filesize') or f.get('filesize_approx'))  # Must have size
                ):
                    # Calculate approximate file size
                    filesize = f.get('filesize') or f.get('filesize_approx')
                    filesize_mb = filesize / (1024 * 1024) if filesize else None
                    
                    # Build stream info
                    stream_info = {
                        'format_id': f.get('format_id'),
                        'format_note': 'Audio only',
                        'ext': f.get('ext'),
                        'resolution': 'Audio only',
                        'fps': None,
                        'filesize': filesize,
                        'filesize_mb': filesize_mb,
                        'tbr': f.get('tbr'),  # Total bitrate
                        'acodec': f.get('acodec'),
                        'vcodec': 'none',
                        'abr': f.get('abr'),  # Audio bitrate
                        'vbr': None,
                        'quality': "Audio",
                        'format': f.get('format'),
                        'video_ext': 'none',
                        'is_audio': True
                    }
                    
                    # Add to streams list
                    audio_streams.append(stream_info)
            
            # Combine video and audio streams
            return video_streams + audio_streams
            
    except Exception as e:
        logger.error(f"Error getting available streams: {e}")
        raise Exception(f"Could not get stream information: {str(e)}")
    
def download_video(video_url, download_folder, filename=None):
    """
    Download a YouTube video in 360p quality using yt-dlp.
    
    Args:
        video_url (str): YouTube video URL
        download_folder (str): Folder to save the download
        filename (str, optional): Custom filename
        
    Returns:
        str: Path to the downloaded file
    """
    os.makedirs(download_folder, exist_ok=True)
    
    # Set output template
    if filename:
        output_template = os.path.join(download_folder, filename)
    else:
        output_template = os.path.join(download_folder, '%(title)s.%(ext)s')
    
    # Configure yt-dlp options to force 360p quality
    ydl_opts = {
        'format': 'bestvideo[height<=360]+bestaudio/best[height<=360]',  # Limit to 360p
        'outtmpl': output_template,
        'progress_hooks': [_progress_hook],
        'quiet': False,
        'no_warnings': True,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            
            # Get the downloaded file path
            if info.get('requested_downloads'):
                file_path = info['requested_downloads'][0].get('filepath')
                return file_path
            else:
                # Fallback to constructing path from info
                title = info.get('title', 'video')
                ext = info.get('ext', 'mp4')
                sanitized_title = re.sub(r'[\\/*?:"<>|]', '_', title)
                return os.path.join(download_folder, f"{sanitized_title}.{ext}")
    except DownloadError as e:
        logger.error(f"Download error: {e}")
        raise Exception(f"Download failed: {str(e)}")
    except Exception as e:
        logger.error(f"Error downloading video: {e}")
        raise Exception(f"Could not download video: {str(e)}")

def _progress_hook(d):
    """
    Progress hook for yt-dlp downloads.
    
    Args:
        d (dict): Progress information from yt-dlp
    """
    if d['status'] == 'downloading':
        try:
            percent = d.get('_percent_str', 'N/A')
            speed = d.get('_speed_str', 'N/A')
            eta = d.get('_eta_str', 'N/A')
            
            # Log the progress info
            logger.info(f"Download progress: {percent} at {speed}, ETA: {eta}")
        except Exception:
            pass
    elif d['status'] == 'finished':
        logger.info("Download complete. Converting...")
    elif d['status'] == 'error':
        logger.error(f"Download error: {d.get('error')}")

def get_playlist_info(playlist_url):
    """
    Get information about a YouTube playlist using yt-dlp.
    
    Args:
        playlist_url (str): YouTube playlist URL
        
    Returns:
        dict: Playlist information
    """
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'skip_download': True,
        'extract_flat': True,  # Don't extract full info for each video
        'playlistreverse': False,  # Keep original playlist order
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(playlist_url, download=False)
            
            # Handle case where URL is a video with a playlist reference
            # Get actual playlist info if necessary
            if info.get('_type') == 'playlist':
                playlist_info = info
            else:
                # For single videos with a playlist
                playlist_info = info.get('playlist', info)
                if not isinstance(playlist_info, dict):
                    raise Exception("Not a valid playlist")
            
            # Extract video information
            videos = []
            for entry in playlist_info.get('entries', []):
                if entry:
                    # Calculate duration string
                    duration = entry.get('duration', 0)
                    if duration:
                        duration_string = str(timedelta(seconds=duration))
                        if duration_string.startswith('0:'):
                            duration_string = duration_string[2:]
                    else:
                        duration_string = "Unknown"
                    
                    videos.append({
                        'id': entry.get('id'),
                        'title': entry.get('title', 'Unknown title'),
                        'url': entry.get('url'),
                        'thumbnail': entry.get('thumbnail', ''),
                        'duration': duration,
                        'duration_string': duration_string,
                    })
            
            return {
                'id': playlist_info.get('id'),
                'title': playlist_info.get('title', 'Playlist'),
                'uploader': playlist_info.get('uploader', 'Unknown'),
                'video_count': len(videos),
                'videos': videos,
            }
    except Exception as e:
        logger.error(f"Error getting playlist info: {e}")
        raise Exception(f"Could not get playlist information: {str(e)}")

def download_playlist(playlist_url, download_folder, quality='highest'):
    """
    Download all videos in a YouTube playlist using yt-dlp.
    
    Args:
        playlist_url (str): YouTube playlist URL
        download_folder (str): Folder to save downloads
        quality (str): Quality preference ('highest', 'lowest', 'audio', or resolution like '720p')
        
    Returns:
        list: Results of each video download
    """
    os.makedirs(download_folder, exist_ok=True)
    
    # Map quality setting to format selection with better options for higher resolutions
    if quality == 'highest':
        format_spec = 'bestvideo+bestaudio/best'
    elif quality == 'lowest':
        format_spec = 'worst'
    elif quality == 'audio':
        format_spec = 'bestaudio/best'
    elif quality == '2160p' or quality == '4K':
        format_spec = 'bestvideo[height<=2160]+bestaudio/best[height<=2160]'
    elif quality == '1440p' or quality == '2K':
        format_spec = 'bestvideo[height<=1440]+bestaudio/best[height<=1440]'
    elif quality == '1080p':
        format_spec = 'bestvideo[height<=1080]+bestaudio/best[height<=1080]'
    elif quality == '720p':
        format_spec = 'bestvideo[height<=720]+bestaudio/best[height<=720]'
    elif quality == '480p':
        format_spec = 'bestvideo[height<=480]+bestaudio/best[height<=480]'
    elif quality == '360p':
        format_spec = 'bestvideo[height<=360]+bestaudio/best[height<=360]'
    else:
        format_spec = 'bestvideo+bestaudio/best'  # Default to best quality
        
    # Log format specification
    logger.info(f"Using format specification for quality '{quality}': {format_spec}")
    
    # Configure yt-dlp options
    ydl_opts = {
        'format': format_spec,
        'outtmpl': os.path.join(download_folder, '%(title)s.%(ext)s'),
        'progress_hooks': [_progress_hook],
        'noplaylist': False,  # Process playlist
        'playlistreverse': False,  # Keep original order
        'quiet': False,
        'no_warnings': True,
        'ignoreerrors': True,  # Skip unavailable videos
    }
    
    # Setup for tracking results
    download_results = []
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # First get playlist info
            playlist_info = get_playlist_info(playlist_url)
            total_videos = playlist_info['video_count']
            
            logger.info(f"Starting download of {total_videos} videos from playlist '{playlist_info['title']}'")
            
            # Download the playlist
            result = ydl.extract_info(playlist_url, download=True)
            
            # Track download results
            if 'entries' in result:
                for i, entry in enumerate(result['entries']):
                    if entry:
                        # Success
                        download_results.append({
                            'id': entry.get('id'),
                            'title': entry.get('title', f'Video {i+1}'),
                            'success': True,
                            'path': os.path.join(download_folder, f"{entry.get('title', f'Video {i+1}')}.{entry.get('ext', 'mp4')}"),
                        })
                    else:
                        # Failed or skipped
                        download_results.append({
                            'id': None,
                            'title': f"Video {i+1}",
                            'success': False,
                            'error': 'Video unavailable or skipped',
                        })
            
            return download_results
    except Exception as e:
        logger.error(f"Error downloading playlist: {e}")
        raise Exception(f"Playlist download failed: {str(e)}")