from django import forms

class UploadFileForm(forms.Form):
    files = forms.FileField(
        required=False,
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['files'].widget.attrs.update({'multiple': 'multiple'})

class SingleFileForm(forms.Form):
    file = forms.FileField(
        required=True,
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'})
    )

class SplitPdfForm(forms.Form):
    file = forms.FileField(
        required=True,
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'})
    )
    split_ranges = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., 1-3,4-6'
        })
    )

class PdfToImageForm(forms.Form):
    file = forms.FileField(
        required=True,
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'})
    )
    format = forms.ChoiceField(
        choices=[('jpeg', 'JPEG'), ('png', 'PNG')],
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    dpi = forms.IntegerField(
        required=True,
        initial=200,
        min_value=72,
        max_value=600,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

class ImageToPdfForm(forms.Form):
    images = forms.FileField(
        required=True,
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['images'].widget.attrs.update({'multiple': 'multiple'})

class ReorderPdfForm(forms.Form):
    file = forms.FileField(
        required=True,
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'})
    )
