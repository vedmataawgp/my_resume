"""
Django integration for YouTube downloader functionality.
"""
import os
import logging
from datetime import timedelta

# Import functions from yt_downloader module
from .yt_downloader import (
    validate_youtube_url,
    get_video_info as yt_get_video_info,
    get_available_streams as yt_get_streams,
    download_video as yt_download_video,
    get_playlist_info as yt_get_playlist_info,
    download_playlist as yt_download_playlist
)

# Set up logging
logger = logging.getLogger(__name__)

class YouTubeDownloader:
    """
    Django integration for YouTube downloader functionality.
    This class provides methods to download YouTube videos and extract video information
    for use in Django applications.
    """
    
    def __init__(self, download_dir=None):
        """
        Initialize the YouTube downloader.
        
        Args:
            download_dir (str, optional): Directory to save downloaded videos.
                                         If None, uses a temporary directory.
        """
        # If download_dir is not specified, use a default directory
        if download_dir is None:
            import tempfile
            download_dir = os.path.join(tempfile.gettempdir(), 'youtube_downloads')
            
        # Ensure the directory exists
        os.makedirs(download_dir, exist_ok=True)
        self.download_dir = download_dir
        logger.info(f"YouTube downloader initialized with download directory: {download_dir}")
    
    def validate_youtube_url(self, url):
        """
        Validate if a URL is a valid YouTube URL.
        
        Args:
            url (str): URL to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        return validate_youtube_url(url)
    
    def get_video_info(self, video_url):
        """
        Get information about a YouTube video.
        
        Args:
            video_url (str): YouTube video URL
            
        Returns:
            dict: Video information including title, author, length, etc.
            
        Raises:
            Exception: If video information cannot be retrieved
        """
        try:
            logger.info(f"Getting video info for URL: {video_url}")
            video_info = yt_get_video_info(video_url)
            logger.info(f"Successfully retrieved video info: {video_info.get('title')}")
            return video_info
        except Exception as e:
            logger.error(f"Error getting video info: {e}")
            raise
    
    def get_available_streams(self, video_url):
        """
        Get available streams for a YouTube video.
        
        Args:
            video_url (str): YouTube video URL
            
        Returns:
            list: Available streams with format and quality information
            
        Raises:
            Exception: If stream information cannot be retrieved
        """
        try:
            logger.info(f"Getting available streams for URL: {video_url}")
            streams = yt_get_streams(video_url)
            logger.info(f"Successfully retrieved {len(streams)} streams")
            return streams
        except Exception as e:
            logger.error(f"Error getting streams: {e}")
            raise
    
    def download_video(self, video_url, format_id, filename=None, progress_callback=None):
        """
        Download a YouTube video.
        
        Args:
            video_url (str): YouTube video URL
            format_id (str): Format ID to download
            filename (str, optional): Custom filename for the downloaded file
            progress_callback (function, optional): Callback function to track progress
            
        Returns:
            str: Path to the downloaded file
            
        Raises:
            Exception: If download fails
        """
        try:
            logger.info(f"Downloading video {video_url} with format {format_id}")
            file_path = yt_download_video(
                video_url, 
                format_id, 
                self.download_dir, 
                filename
            )
            logger.info(f"Video download complete: {file_path}")
            return file_path
        except Exception as e:
            logger.error(f"Error downloading video: {e}")
            raise
    
    def get_playlist_info(self, playlist_url, limit=None):
        """
        Get information about a YouTube playlist.
        
        Args:
            playlist_url (str): YouTube playlist URL
            limit (int, optional): Max number of videos to get info for
            
        Returns:
            dict: Playlist information including title, video count, etc.
            
        Raises:
            Exception: If playlist information cannot be retrieved
        """
        try:
            logger.info(f"Getting playlist info for URL: {playlist_url}")
            playlist_info = yt_get_playlist_info(playlist_url)
            
            # Apply limit if specified
            if limit is not None and isinstance(limit, int) and limit > 0:
                playlist_info['videos'] = playlist_info['videos'][:limit]
                playlist_info['video_count'] = len(playlist_info['videos'])
                
            logger.info(f"Successfully retrieved playlist info: {playlist_info.get('title')} ({playlist_info.get('video_count')} videos)")
            return playlist_info
        except Exception as e:
            logger.error(f"Error getting playlist info: {e}")
            raise
    
    def download_playlist(self, playlist_url, quality='highest', progress_callback=None):
        """
        Download all videos in a YouTube playlist.
        
        Args:
            playlist_url (str): YouTube playlist URL
            quality (str, optional): Quality to download ('highest', '720p', etc.)
            progress_callback (function, optional): Callback function for progress
            
        Returns:
            list: Results of each video download
            
        Raises:
            Exception: If playlist download fails
        """
        try:
            logger.info(f"Downloading playlist {playlist_url} with quality {quality}")
            results = yt_download_playlist(
                playlist_url, 
                self.download_dir, 
                quality
            )
            
            # Count successes and failures
            success_count = sum(1 for result in results if result.get('success', False))
            failed_count = len(results) - success_count
            
            logger.info(f"Playlist download complete: {success_count} successes, {failed_count} failures")
            return results
        except Exception as e:
            logger.error(f"Error downloading playlist: {e}")
            raise