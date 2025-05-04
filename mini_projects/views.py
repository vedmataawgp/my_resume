from django.shortcuts import render
from django.http import HttpResponse
import pandas as pd
import qrcode
import io

# Excel to VCF
def excel_to_vcf_view(request):
    if request.method == 'POST':
        excel_file = request.FILES.get('excel_file')
        name_column = request.POST.get('name_column')
        phone_column = request.POST.get('phone_column')

        if not excel_file:
            return HttpResponse("No file uploaded.", status=400)

        try:
            # Read the Excel file
            df = pd.read_excel(excel_file)

            # Ensure the selected columns exist
            if name_column not in df.columns or phone_column not in df.columns:
                return HttpResponse("Selected columns do not exist in the uploaded file.", status=400)

            # Generate VCF data
            vcf_data = io.StringIO()
            for _, row in df.iterrows():
                vcf_data.write(f"BEGIN:VCARD\nVERSION:3.0\nFN:{row[name_column]}\nTEL:{row[phone_column]}\nEND:VCARD\n")

            # Return the VCF file as a response
            response = HttpResponse(vcf_data.getvalue(), content_type='text/vcard')
            response['Content-Disposition'] = 'attachment; filename="contacts.vcf"'
            return response
        except Exception as e:
            return HttpResponse(f"Error processing file: {e}", status=500)

    elif request.method == 'GET':
        return render(request, 'mini_projects/excel_to_vcf.html')

    return render(request, 'mini_projects/excel_to_vcf.html')

# Email Validation
def email_validation_view(request):
    if request.method == 'POST':
        excel_file = request.FILES.get('excel_file')
        if not excel_file:
            return HttpResponse("No file uploaded.", status=400)

        try:
            # Read the Excel file
            df = pd.read_excel(excel_file)

            # Ensure the 'Email' column exists
            if 'Email' not in df.columns:
                return HttpResponse("The uploaded file must contain an 'Email' column.", status=400)

            # Handle missing values and validate emails
            df['Email'] = df['Email'].fillna('')  # Replace NaN with empty strings
            valid_emails = df['Email'].str.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', na=False)

            # Filter valid emails
            valid_df = df[valid_emails]

            # Write valid emails to an Excel file
            output = io.BytesIO()
            valid_df.to_excel(output, index=False)
            output.seek(0)

            # Return the file as a response
            response = HttpResponse(output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = 'attachment; filename="validated_emails.xlsx"'
            return response
        except Exception as e:
            return HttpResponse(f"Error processing file: {e}", status=500)

    return render(request, 'mini_projects/email_validation.html')

# QR Code Generator
def qr_code_generator_view(request):
    if request.method == 'POST':
        data = request.POST.get('data')
        if not data:
            return HttpResponse("No data provided.", status=400)

        try:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(data)
            qr.make(fit=True)

            img = qr.make_image(fill_color="black", back_color="white")
            buffer = io.BytesIO()
            img.save(buffer, format="PNG")
            buffer.seek(0)

            response = HttpResponse(buffer, content_type="image/png")
            response['Content-Disposition'] = 'attachment; filename="qr_code.png"'
            return response
        except Exception as e:
            return HttpResponse(f"Error generating QR code: {e}", status=500)

    return render(request, 'mini_projects/qr_code_generator.html')
