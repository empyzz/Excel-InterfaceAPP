from django.shortcuts import render, HttpResponse
from django.contrib import messages
from .forms import *
from .models import *
from django.core.exceptions import ValidationError
import pandas as pd

def home(request):
    form = ExcelUploadForm()
    erro = None
    excel_dados = None
    abas_disponiveis = []
    aba_selecionada = request.GET.get('aba')

    if request.method == "POST":
        acao = request.POST.get("acao")
        if acao == "excel":
            form = ExcelUploadForm(request.POST, request.FILES)
            if form.is_valid():
                arquivo_excel = form.cleaned_data["arquivo"]

                try:
                    extensoes_validas = ['.xls', '.xlsx', 'xlsm']
                    if not any(arquivo_excel.name.endswith(ext) for ext in extensoes_validas):
                        raise ValidationError("O arquivo deve ser um Excel (.xls ou .xlsx).")

                    excel_obj = Excel(nome=arquivo_excel.name, arquivo=arquivo_excel)
                    excel_obj.save()

                except ValidationError as e:
                    erro = str(e)
                except Exception as e:
                    erro = f"Erro ao processar o arquivo: {e}"

    try:
        ultimo_excel = Excel.objects.latest('data')
        caminho_arquivo = ultimo_excel.arquivo.path

        excel_file = pd.ExcelFile(caminho_arquivo)
        abas_disponiveis = excel_file.sheet_names  

        aba = aba_selecionada or abas_disponiveis[0]  
        df = pd.read_excel(excel_file, sheet_name=aba)  

        if df.empty:
            erro = "O arquivo está vazio!"
        else:
            excel_dados = df.to_dict(orient="records")

    except Excel.DoesNotExist:
        erro = "Nenhum arquivo Excel foi enviado ainda."
    except Exception as e:
        erro = f"Erro ao carregar o arquivo: {e}"

    contexto = {
        "erro": erro,
        "ExcelDados": excel_dados,
        "abas": abas_disponiveis,
        "aba_selecionada": aba_selecionada,
        "form": form,
    }
    
    return render(request, 'ExcelInterface/table.html', contexto)