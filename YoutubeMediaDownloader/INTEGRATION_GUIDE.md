# YouTube Media Downloader Django Integration Guide

This guide will help you integrate the YouTube Media Downloader app into your existing Django project.

## Step 1: Copy Files

Copy the entire `YoutubeMediaDownloader` directory to your Django project's root directory.

## Step 2: Add App to INSTALLED_APPS

Add the YouTube Media Downloader app to your Django project's `settings.py` file:

```python
INSTALLED_APPS = [
    # ... your existing apps
    'YoutubeMediaDownloader',
]
```

## Step 3: Configure Media Settings

Ensure your Django project has media settings configured in `settings.py`:

```python
# Media files (Downloads, user uploads)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Create media directory if it doesn't exist
import os
os.makedirs(os.path.join(BASE_DIR, 'media/youtube_downloads'), exist_ok=True)
```

## Step 4: Add URL Patterns

Include the YouTube Media Downloader URL patterns in your project's main `urls.py` file:

```python
from django.urls import path, include

urlpatterns = [
    # ... your existing URLs
    path('youtube/', include('YoutubeMediaDownloader.urls')),
]
```

For development, you may also need to add media URL patterns:

```python
from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

## Step 5: Install Dependencies

Make sure the required packages are installed:

```bash
pip install yt-dlp requests tqdm
```

## Step 6: Check Templates

The templates assume you have a base template named `base.html`. If your base template has a different name, adjust the `extends` tags in:

- `YoutubeMediaDownloader/templates/YoutubeMediaDownloader/index.html`
- `YoutubeMediaDownloader/templates/YoutubeMediaDownloader/video.html`
- `YoutubeMediaDownloader/templates/YoutubeMediaDownloader/playlist.html`

## Step 7: Run Migrations

Although this app doesn't require database models, it's good practice to run migrations:

```bash
python manage.py migrate
```

## Step 8: Test the Integration

Start your Django server and navigate to `/youtube/` to test the YouTube Media Downloader.

```bash
python manage.py runserver
```

Visit http://localhost:8000/youtube/ in your browser.

## Additional Configuration

### Custom Download Directory

If you want to change the download directory, you can add this to your `settings.py`:

```python
# YouTube Downloader settings
YOUTUBE_DOWNLOAD_FOLDER = os.path.join(BASE_DIR, 'your_custom_path')
```

### Template Customization

You can override the templates by placing your custom versions in your project's templates directory:

```
your_project/templates/YoutubeMediaDownloader/
```

## Features

### Video Quality Options

The YouTube Media Downloader now offers enhanced quality options including:

- 4K/2160p video quality (when available)
- 2K/1440p video quality (when available) 
- 1080p HD video
- 720p HD video
- 480p and 360p standard definition
- Audio-only downloads with various quality options

The downloader smartly combines separate video and audio streams for the best possible quality when needed, especially for higher resolutions like 4K which are usually not available as combined streams.

### Direct Browser Downloads

Videos and playlists download directly to the user's device through the browser without requiring server-side storage. This eliminates permission issues and storage concerns.

### Proper File Naming

Downloads include relevant information in the filename:
- For videos: `video_title_quality.extension`
- For playlists: `playlist_name_quality_timestamp.zip`

### Error Handling

Comprehensive error messages are provided for common issues:
- Region-restricted videos
- Age-restricted content
- Private or deleted videos
- Permission issues with temporary directories

## Troubleshooting

If you encounter import errors with the main application, ensure the `yt_downloader.py` file from the root directory is present (it provides a compatibility layer for existing imports).

### Common Issues and Solutions

1. **HTTP 400 Errors**: The app uses yt-dlp which is more reliable than pytube for handling YouTube's API changes.

2. **Permission Denied Errors**: The app attempts to create temporary directories with appropriate permissions. If issues persist, check your system's temporary directory permissions.

3. **Missing File Extensions**: The downloader now properly detects file types and ensures correct extensions are applied.

4. **Timeout on Large Playlists**: For very large playlists, consider increasing the server timeout settings or limiting the number of videos to download.

For any issues with downloading videos, check the application logs, as detailed error messages are logged during the download process.