import re
import requests
from pytube import YouTube, Search
from urllib.parse import urlparse, parse_qs

def search_youtube(query, page=1, limit=12):
    """
    Search YouTube for videos based on a query using pytube
    
    Args:
        query (str): The search query
        page (int): Page number (starting from 1)
        limit (int): Number of results per page
    
    Returns:
        list: List of video results with their metadata
    """
    try:
        # Calculate the offset based on the page number
        offset = (page - 1) * limit
        
        # Create a Search object
        s = Search(query)
        
        # Get more results than needed (for pagination)
        results_needed = offset + limit
        while len(s.results) < results_needed and s.get_next_results():
            pass
            
        # Slice the results based on pagination
        results = s.results[offset:offset+limit] if offset < len(s.results) else []
        
        # Process video information
        formatted_videos = []
        for video in results:
            # Get video ID from the watch URL
            video_id = video.video_id
            
            # Format duration in minutes:seconds
            duration_seconds = video.length
            minutes, seconds = divmod(duration_seconds, 60)
            formatted_duration = f"{minutes}:{seconds:02d}"
            
            formatted_video = {
                'id': video_id,
                'title': video.title,
                'channel': video.author,
                'duration': formatted_duration,
                'views': f"{video.views:,} views" if hasattr(video, 'views') and video.views else 'Unknown views',
                'thumbnail': f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg"
            }
            formatted_videos.append(formatted_video)
                
        return formatted_videos
    except Exception as e:
        print(f"Error searching YouTube: {str(e)}")
        return []

def get_video_info(video_id):
    """
    Get information about a specific YouTube video using pytube
    
    Args:
        video_id (str): YouTube video ID
    
    Returns:
        dict: Video information (title, channel, etc.)
    """
    try:
        # Create a fallback info in case API call fails
        fallback_info = {
            'title': 'Video Information Unavailable',
            'channel': 'Unknown',
            'thumbnail_url': '',
            'duration': '',
            'views': '',
            'description': 'Could not retrieve video information.'
        }
        
        # Skip API call if video_id is invalid
        if not video_id or len(video_id) != 11:
            print(f"Invalid video ID: {video_id}")
            return fallback_info
            
        # Get video info using pytube
        yt = YouTube(f"https://youtube.com/watch?v={video_id}")
        
        # Format duration in minutes:seconds
        duration_seconds = yt.length
        minutes, seconds = divmod(duration_seconds, 60)
        formatted_duration = f"{minutes}:{seconds:02d}"
        
        # If no video info returned, use fallback
        if not yt:
            print("No video information returned from API")
            return fallback_info
            
        # Extract the necessary information
        info = {
            'title': yt.title,
            'channel': yt.author,
            'thumbnail_url': yt.thumbnail_url,
            'duration': formatted_duration,
            'views': f"{yt.views:,} views" if hasattr(yt, 'views') and yt.views else 'Unknown views',
            'description': yt.description
        }
        
        return info
    except Exception as e:
        print(f"Error getting video info: {str(e)}")
        return {
            'title': 'Video Information Unavailable',
            'channel': 'Unknown',
            'thumbnail_url': '',
            'duration': '',
            'views': '',
            'description': f'Could not retrieve video information. Error: {str(e)}'
        }
