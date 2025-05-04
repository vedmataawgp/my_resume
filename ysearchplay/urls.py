from django.urls import path
from . import views

app_name = 'ysearchplay'

urlpatterns = [
    path('', views.home, name='home'),
    path('search/', views.search, name='search'),
    path('play/<str:video_id>/', views.play, name='play'),
    path('history/', views.history, name='history'),
    path('download/<str:video_id>/', views.download_video, name='download_video'),
]
