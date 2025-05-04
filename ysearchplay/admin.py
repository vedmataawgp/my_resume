from django.contrib import admin
from .models import SearchHistory, VideoHistory, Video

@admin.register(SearchHistory)
class SearchHistoryAdmin(admin.ModelAdmin):
    list_display = ('query', 'session_id', 'timestamp')
    list_filter = ('timestamp',)
    search_fields = ('query', 'session_id')

@admin.register(VideoHistory)
class VideoHistoryAdmin(admin.ModelAdmin):
    list_display = ('video_title', 'video_id', 'session_id', 'viewed_at')
    list_filter = ('viewed_at',)
    search_fields = ('video_title', 'video_id', 'session_id')

@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ('title', 'channel', 'youtube_id', 'added_at')
    list_filter = ('added_at',)
    search_fields = ('title', 'channel', 'youtube_id')
