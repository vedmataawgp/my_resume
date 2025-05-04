import os
from io import BytesIO
import zipfile
import tempfile
import json
from pathlib import Path
from django.shortcuts import render
from django.http import FileResponse, HttpResponseBadRequest, JsonResponse, HttpResponse
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from .forms import UploadFileForm, SingleFileForm, SplitPdfForm, PdfToImageForm, ImageToPdfForm, ReorderPdfForm
from PyPDF2 import PdfMerger, PdfReader, PdfWriter
from pdf2image import convert_from_bytes
from PIL import Image

def validate_pdf_file(file):
    """Validates if a file is a PDF."""
    if not file.name.lower().endswith('.pdf'):
        return False
    # Additional validation could be added here
    return True

def log_error(message, exception=None):
    """Log error details for debugging."""
    import traceback
    from datetime import datetime
    
    error_details = f"[{datetime.now()}] ERROR: {message}\n"
    if exception:
        error_details += f"Exception: {str(exception)}\n"
        error_details += f"Traceback: {traceback.format_exc()}\n"
    
    print(error_details)
    return error_details

def home(request):
    """Home page view with file upload form."""
    context = {
        'merge_form': UploadFileForm(),
        'split_form': SplitPdfForm(),
        'compress_form': SingleFileForm(),
        'pdf_to_image_form': PdfToImageForm(),
        'image_to_pdf_form': ImageToPdfForm(),
        'reorder_pdf_form': ReorderPdfForm(),
    }
    return render(request, 'pdf_tools/home.html', context)

def merge_pdfs(request):
    """Handle PDF merge operations."""
    if request.method == 'POST':
        files = request.FILES.getlist('files')
        
        # Validate files
        if not files:
            return HttpResponseBadRequest('No files provided.')
        
        for file in files:
            if not validate_pdf_file(file):
                return HttpResponseBadRequest(f'{file.name} is not a valid PDF file.')
        
        # Get page ranges if provided
        page_order = request.POST.get('page_order', '')
        
        merger = PdfMerger()
        
        if page_order:
            # Parse the page order (e.g., "file1.pdf:1-3,file2.pdf:4-5")
            order_parts = page_order.split(',')
            
            for part in order_parts:
                if ':' in part:
                    filename, pages = part.split(':')
                    file = next((f for f in files if f.name == filename), None)
                    
                    if file and pages:
                        reader = PdfReader(file)
                        if '-' in pages:
                            start, end = map(int, pages.split('-'))
                            # Convert to zero-based index
                            merger.append(reader, pages=(start-1, end))
                        else:
                            # Single page case
                            page = int(pages) - 1
                            merger.append(reader, pages=(page, page+1))
                else:
                    # If no page range specified, add the whole file
                    file = next((f for f in files if f.name == part), None)
                    if file:
                        merger.append(file)
        else:
            # If no page order specified, merge all files in the order they were uploaded
            for file in files:
                merger.append(file)
        
        # Create merged PDF in memory
        output = BytesIO()
        merger.write(output)
        merger.close()
        output.seek(0)
        
        # Return the merged PDF file as a download
        return FileResponse(output, as_attachment=True, filename='merged.pdf')
    
    # For GET requests, show the merge form
    return render(request, 'pdf_tools/merge.html', {'form': UploadFileForm()})

def split_pdf(request):
    """Handle PDF split operations."""
    if request.method == 'POST':
        form = SplitPdfForm(request.POST, request.FILES)
        
        if form.is_valid():
            uploaded_file = request.FILES['file']
            split_ranges = form.cleaned_data['split_ranges']
            
            if not validate_pdf_file(uploaded_file):
                return HttpResponseBadRequest('Not a valid PDF file.')
            
            reader = PdfReader(uploaded_file)
            total_pages = len(reader.pages)
            
            # Parse the split ranges
            try:
                ranges = []
                for range_str in split_ranges.split(','):
                    if '-' in range_str:
                        start, end = map(int, range_str.split('-'))
                        if start < 1 or end > total_pages or start > end:
                            return HttpResponseBadRequest(f'Invalid page range: {range_str}. The PDF has {total_pages} pages.')
                        ranges.append((start, end))
                    else:
                        page = int(range_str)
                        if page < 1 or page > total_pages:
                            return HttpResponseBadRequest(f'Invalid page number: {page}. The PDF has {total_pages} pages.')
                        ranges.append((page, page))
            except ValueError:
                return HttpResponseBadRequest('Invalid page range format. Use format like "1-3,4-6".')
            
            # Create a zip file containing all the split parts
            zip_buffer = BytesIO()
            
            with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
                for i, (start, end) in enumerate(ranges):
                    writer = PdfWriter()
                    
                    # Add pages from the range (convert to 0-based index)
                    for page_num in range(start - 1, end):
                        writer.add_page(reader.pages[page_num])
                    
                    # Write to a temporary buffer
                    pdf_buffer = BytesIO()
                    writer.write(pdf_buffer)
                    pdf_buffer.seek(0)
                    
                    # Add to zip file
                    zip_file.writestr(f'split_part_{i+1}.pdf', pdf_buffer.read())
            
            # Prepare the zip file for download
            zip_buffer.seek(0)
            return FileResponse(zip_buffer, as_attachment=True, filename='split_pdfs.zip')
        
        return HttpResponseBadRequest('Invalid form submission.')
    
    # For GET requests, show the split form
    return render(request, 'pdf_tools/split.html', {'form': SplitPdfForm()})

def compress_pdf(request):
    """Handle PDF compression operations."""
    if request.method == 'POST':
        form = SingleFileForm(request.POST, request.FILES)
        
        if form.is_valid():
            uploaded_file = request.FILES['file']
            
            if not validate_pdf_file(uploaded_file):
                return HttpResponseBadRequest('Not a valid PDF file.')
            
            # Simple compression using PyPDF2
            # Note: This doesn't provide significant compression but preserves the structure
            reader = PdfReader(uploaded_file)
            writer = PdfWriter()
            
            # Copy each page (this alone can provide minor compression)
            for page in reader.pages:
                writer.add_page(page)
            
            # Set compression parameters
            # Note: PyPDF2 doesn't have advanced compression options
            
            # Write to a buffer
            output = BytesIO()
            writer.write(output)
            output.seek(0)
            
            # Return the compressed file for download
            return FileResponse(output, as_attachment=True, filename='compressed.pdf')
        
        return HttpResponseBadRequest('Invalid form submission.')
    
    # For GET requests, show the compression form
    return render(request, 'pdf_tools/compress.html', {'form': SingleFileForm()})


def pdf_to_image(request):
    """Convert PDF pages to images."""
    if request.method == 'POST':
        form = PdfToImageForm(request.POST, request.FILES)
        
        if form.is_valid():
            uploaded_file = request.FILES['file']
            image_format = form.cleaned_data['format']
            dpi = form.cleaned_data['dpi']
            
            if not validate_pdf_file(uploaded_file):
                return HttpResponseBadRequest('Not a valid PDF file.')
            
            # Read the uploaded file into memory
            pdf_bytes = uploaded_file.read()
            
            # Convert PDF to images
            try:
                images = convert_from_bytes(pdf_bytes, dpi=dpi)
            except Exception as e:
                return HttpResponseBadRequest(f'Error converting PDF: {str(e)}')
            
            # Create a zip file containing all images
            zip_buffer = BytesIO()
            
            with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
                for i, image in enumerate(images):
                    # Create a buffer for the image
                    img_buffer = BytesIO()
                    # Save the image to the buffer
                    image.save(img_buffer, format=image_format.upper())
                    img_buffer.seek(0)
                    
                    # Add to zip file with appropriate extension (maintain user-friendly extension)
                    extension = 'jpg' if image_format.lower() == 'jpeg' else image_format.lower()
                    zip_file.writestr(f'page_{i+1}.{extension}', img_buffer.read())
            
            # Prepare the zip file for download
            zip_buffer.seek(0)
            return FileResponse(zip_buffer, as_attachment=True, filename=f'pdf_images.zip')
        
        return HttpResponseBadRequest('Invalid form submission.')
    
    # For GET requests, show the form
    return render(request, 'pdf_tools/pdf_to_image.html', {'form': PdfToImageForm()})


def image_to_pdf(request):
    """Convert images to a PDF file."""
    if request.method == 'POST':
        form = ImageToPdfForm(request.POST, request.FILES)
        
        if form.is_valid():
            image_files = request.FILES.getlist('images')
            
            if not image_files:
                return HttpResponseBadRequest('No image files provided.')
            
            # Check if files are valid images
            valid_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.gif']
            for img_file in image_files:
                ext = os.path.splitext(img_file.name.lower())[1]
                if ext not in valid_extensions:
                    return HttpResponseBadRequest(f'{img_file.name} is not a valid image file.')
            
            # Create a new PDF file
            output = BytesIO()
            
            # Create the first image as PDF
            try:
                first_image = Image.open(image_files[0])
                # Convert to RGB mode if necessary (to avoid CMYK or palette issues)
                if first_image.mode != 'RGB':
                    first_image = first_image.convert('RGB')
                
                # Create a list to store all images
                images = []
                images.append(first_image)
                
                # Open remaining images and add to list
                for i in range(1, len(image_files)):
                    img = Image.open(image_files[i])
                    if img.mode != 'RGB':
                        img = img.convert('RGB')
                    images.append(img)
                
                # Save first image to PDF and append the rest
                first_image.save(output, 'PDF', save_all=True, append_images=images[1:])
                output.seek(0)
                
                return FileResponse(output, as_attachment=True, filename='images_to_pdf.pdf')
            except Exception as e:
                return HttpResponseBadRequest(f'Error creating PDF: {str(e)}')
        
        return HttpResponseBadRequest('Invalid form submission.')
    
    # For GET requests, show the form
    return render(request, 'pdf_tools/image_to_pdf.html', {'form': ImageToPdfForm()})


def reorder_pdf(request):
    """Reorder PDF pages using drag and drop."""
    context = {'form': ReorderPdfForm()}
    
    if request.method == 'POST':
        print(f"POST request received for reorder_pdf: {request.POST.keys()}")
        
        if 'file' in request.FILES:
            try:
                # Initial upload of the PDF file
                uploaded_file = request.FILES['file']
                print(f"File uploaded: {uploaded_file.name}, size: {uploaded_file.size} bytes")
                
                if not validate_pdf_file(uploaded_file):
                    context['error'] = 'Not a valid PDF file.'
                    return render(request, 'pdf_tools/reorder_pdf.html', context)
                
                # Ensure temp directory exists
                os.makedirs(os.path.join(settings.MEDIA_ROOT, 'temp'), exist_ok=True)
                
                # Store the file temporarily
                fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'temp'))
                filename = fs.save(uploaded_file.name, uploaded_file)
                file_path = fs.path(filename)
                print(f"File saved to: {file_path}")
                
                # Read the PDF to extract page count and thumbnails
                reader = PdfReader(file_path)
                total_pages = len(reader.pages)
                print(f"PDF has {total_pages} pages")
                
                # Generate thumbnails for each page
                page_images = []
                try:
                    # Read file from disk to avoid file handle issues
                    with open(file_path, 'rb') as pdf_file:
                        pdf_data = pdf_file.read()
                    
                    # Convert PDF pages to images for preview
                    print("Converting PDF pages to images...")
                    images = convert_from_bytes(pdf_data, dpi=72)
                    print(f"Generated {len(images)} image previews")
                    
                    for i, image in enumerate(images):
                        # Save thumbnail to temporary file
                        thumb_path = os.path.join(settings.MEDIA_ROOT, 'temp', f'thumb_{i+1}.jpg')
                        image.thumbnail((200, 200))  # Resize for thumbnail
                        image.save(thumb_path, 'JPEG')
                        
                        # Get the URL for the thumbnail
                        thumb_url = f'{settings.MEDIA_URL}temp/thumb_{i+1}.jpg'
                        page_images.append({
                            'number': i+1,
                            'url': thumb_url
                        })
                        print(f"Saved thumbnail {i+1} to {thumb_path}")
                    
                    # Set up context for the template
                    context.update({
                        'filename': filename,
                        'total_pages': total_pages,
                        'thumbnails': page_images,
                        'show_reorder': True  # Flag to show reordering UI
                    })
                    
                    return render(request, 'pdf_tools/reorder_pdf.html', context)
                    
                except Exception as e:
                    error_msg = log_error("Error creating thumbnails", e)
                    context['error'] = f"Error processing PDF: {str(e)}"
                    return render(request, 'pdf_tools/reorder_pdf.html', context)
            
            except Exception as e:
                error_msg = log_error("Error processing PDF upload", e)
                context['error'] = f"Error uploading PDF: {str(e)}"
                return render(request, 'pdf_tools/reorder_pdf.html', context)
        
        elif 'process' in request.POST:
            # Process the reordering request
            try:
                # Get data from request
                filename = request.POST.get('filename')
                print(f"Processing reorder request for file: {filename}")
                
                page_order_str = request.POST.get('page_order')
                if not page_order_str:
                    context['error'] = 'No page order provided.'
                    return render(request, 'pdf_tools/reorder_pdf.html', context)
                
                new_order = json.loads(page_order_str)
                print(f"New page order: {new_order}")
                
                # Open the stored PDF file
                file_path = os.path.join(settings.MEDIA_ROOT, 'temp', filename)
                if not os.path.exists(file_path):
                    context['error'] = f'PDF file not found: {filename}'
                    return render(request, 'pdf_tools/reorder_pdf.html', context)
                
                reader = PdfReader(file_path)
                writer = PdfWriter()
                
                # Add pages in the new order
                for page_num in new_order:
                    # Convert from 1-based to 0-based index
                    page_idx = int(page_num) - 1
                    if 0 <= page_idx < len(reader.pages):
                        writer.add_page(reader.pages[page_idx])
                    else:
                        context['error'] = f'Invalid page number: {page_num}'
                        return render(request, 'pdf_tools/reorder_pdf.html', context)
                
                # Create output PDF
                output = BytesIO()
                writer.write(output)
                output.seek(0)
                
                # Delete temporary files
                try:
                    os.remove(file_path)
                    for i in range(len(reader.pages)):
                        thumb_path = os.path.join(settings.MEDIA_ROOT, 'temp', f'thumb_{i+1}.jpg')
                        if os.path.exists(thumb_path):
                            os.remove(thumb_path)
                except Exception as e:
                    # Log but don't fail if cleanup fails
                    log_error("Error cleaning up temporary files", e)
                
                # Return the reordered PDF
                return FileResponse(output, as_attachment=True, filename='reordered.pdf')
            
            except json.JSONDecodeError as e:
                error_msg = log_error("Invalid JSON in page_order", e)
                context['error'] = 'Invalid page order format'
                return render(request, 'pdf_tools/reorder_pdf.html', context)
                
            except Exception as e:
                error_msg = log_error("Error processing reorder request", e)
                context['error'] = f'Error during reordering: {str(e)}'
                return render(request, 'pdf_tools/reorder_pdf.html', context)
        
        # Handle unexpected POST
        context['error'] = 'Invalid form submission'
        return render(request, 'pdf_tools/reorder_pdf.html', context)
    
    # For GET requests, show the reorder form
    return render(request, 'pdf_tools/reorder_pdf.html', context)
