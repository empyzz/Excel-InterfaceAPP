import pandas as pd
from django import forms
from django.forms import inlineformset_factory
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
    
    
class CheckListForm(forms.ModelForm):
    class Meta:
        model = Checklist
        fields = ['aba', 'nome_lista', 'descricao_lista']
        widgets = {
            'nome_lista': forms.TextInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'Nome da Lista'
            }),
            'descricao_lista': forms.TextInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'Descrição da Lista'
            }),
        }

    def __init__(self, *args, **kwargs):
        abas = kwargs.pop('abas', [])
        super().__init__(*args, **kwargs)

        self.fields['aba'] = forms.ChoiceField(
            choices=[(aba, aba) for aba in abas],
            label="Aba do Excel",
            widget=forms.Select(attrs={
                'class': 'select select-bordered w-full'
            })
        )
        
class CheckListItemForm(forms.ModelForm):
    class Meta:
        model = ChecklistITEM
        fields = ['nome_item', 'statusItem', 'descricaoItem']        
        

ChecklistItemFormSet = inlineformset_factory(
    Checklist,
    ChecklistITEM,
    form=CheckListItemForm,
    extra=1,  # Quantos campos em branco aparecem inicialmente
    can_delete=True
)