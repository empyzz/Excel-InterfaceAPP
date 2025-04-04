import pandas as pd
from django import forms
from django.core.exceptions import ValidationError
from .models import *

class ExcelUploadForm(forms.ModelForm):
    class Meta:
        model = Excel
        fields = ["arquivo"]

    arquivo = forms.FileField(
        widget=forms.FileInput(
            attrs={
                "id": "formFileUpload",
                "class": "form-control",
                "name": "arquivo_excel"
            }
        )
    )