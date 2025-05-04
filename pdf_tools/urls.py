from django.urls import path
from . import views

app_name = 'pdf_tools'  # Define the namespace here

urlpatterns = [
    path('', views.home, name='pdf_tools_home'),  # Home view for PDF tools
    path('merge/', views.merge_pdfs, name='merge'),  # Merge PDFs
    path('split/', views.split_pdf, name='split'),  # Split PDF
    path('compress/', views.compress_pdf, name='compress'),  # Compress PDF
    path('pdf-to-image/', views.pdf_to_image, name='pdf_to_image'),  # Convert PDF to images
    path('image-to-pdf/', views.image_to_pdf, name='image_to_pdf'),  # Convert images to PDF
    path('reorder-pdf/', views.reorder_pdf, name='reorder_pdf'),  # Reorder PDF pages
]
