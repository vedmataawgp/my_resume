# filepath: e:\Divy\Resume\my_resume\my_resume\views.py
from django.shortcuts import render

def home(request):
    return render(request, 'home.html')