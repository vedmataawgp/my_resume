from django.urls import path
from . import views

app_name = 'resume'  # Define the namespace here

urlpatterns = [
    path('upload/', views.upload_resume, name='upload_resume'),
    path('history/', views.analysis_history, name='analysis_history'),  # Correct name
]
