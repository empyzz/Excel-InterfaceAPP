from django.shortcuts import render, HttpResponse
from django.contrib import messages
import pandas as pd
import openpyxl
from .forms import *

# Create your views here.

from django.core.exceptions import ValidationError
import pandas as pd

def home(request):
    form = ExcelUploadForm()
    dados = None
    erro = None

    if request.method == "POST":
        form = ExcelUploadForm(request.POST, request.FILES)

        if form.is_valid():
            arquivo_excel = form.cleaned_data["arquivo_excel"]

            try:
                extensoes_validas = ['.xls', '.xlsx']
                if not any(arquivo_excel.name.endswith(ext) for ext in extensoes_validas):
                    raise ValidationError("O arquivo deve ser um Excel (.xls ou .xlsx).")

                df = pd.read_excel(arquivo_excel)

                if df.empty:
                    raise ValidationError("O arquivo está vazio!")

                dados = df.to_dict(orient='records')

            except ValidationError as e:
                erro = str(e)
                print(erro)
            except Exception as e:
                erro = f"Erro ao processar o arquivo: {e}"

        return render(request, 'ExcelInterface/table.html', {
            'form': form,
            'dados': dados,
            'erro': erro if erro else None
        })

    return render(request, 'ExcelInterface/table.html', {'form': form, 'dados': dados})