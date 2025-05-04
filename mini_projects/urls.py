from django.urls import path
from . import views

app_name = 'mini_projects'


urlpatterns = [
    path('excel-to-vcf/', views.excel_to_vcf_view, name='excel_to_vcf'),
    path('email-validation/', views.email_validation_view, name='email_validation'),
    path('qr-code-generator/', views.qr_code_generator_view, name='qr_code_generator'),
]