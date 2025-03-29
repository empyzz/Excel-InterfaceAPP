import pandas as pd
from django import forms
from django.core.exceptions import ValidationError


class ExcelUploadForm(forms.Form):
    arquivo_excel = forms.FileField(
        widget=forms.FileInput(
            attrs={
                'id': 'formFileUpload',
                'class': 'form-control',
                'name': 'arquivo_excel'
            }
        )
    )