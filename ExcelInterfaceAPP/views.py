from django.shortcuts import render
from django.contrib import messages
from .forms import *
from .models import *
from django.core.exceptions import ValidationError
from django.core.cache import cache
import pandas as pd

def home(request):
    q = request.GET.get('q')
    form = ExcelUploadForm()
    erro = None
    excel_dados = None
    abas_disponiveis = []
    abas_filtradas = []
    aba_selecionada = request.GET.get('aba')
    abas_sem_resultado = []  

    # Upload do Excel
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

                    # Limpa cache ao enviar novo Excel
                    cache.delete('excel_dfs')

                except ValidationError as e:
                    erro = str(e)
                except Exception as e:
                    erro = f"Erro ao processar o arquivo: {e}"


    try:
        dfs_por_aba = cache.get('excel_dfs')

        if not dfs_por_aba:
            ultimo_excel = Excel.objects.latest('data')
            caminho_arquivo = ultimo_excel.arquivo.path

            excel_dict = pd.read_excel(caminho_arquivo, sheet_name=None)
            dfs_por_aba = {
                aba: df.fillna("").loc[:, ~df.columns.str.contains('^Unnamed')]
                for aba, df in excel_dict.items()
            }

            cache.set('excel_dfs', dfs_por_aba, timeout=600)  # 10 minutos de cache

        abas_disponiveis = list(dfs_por_aba.keys())

        if q and not aba_selecionada:
            for nome_aba, df in dfs_por_aba.items():
                mask = df.astype(str).apply(lambda col: col.str.contains(q, case=False, na=False)).any(axis=1) 
                # Transforma pra string
                # Vetoriza  e trata colunas inteira invez de linha
                # de 800 ~ 1000ms para 20 ~ 100ms
                df_filtrado = df[mask]
                if not df_filtrado.empty:
                    abas_filtradas.append(nome_aba)

            aba = abas_filtradas[0] if abas_filtradas else abas_disponiveis[0]
        else:
            aba = aba_selecionada or abas_disponiveis[0]

        df = dfs_por_aba[aba]

        if q:
            df = df[df.apply(lambda row: row.astype(str).str.contains(q, case=False, na=False).any(), axis=1)]

        if not df.empty:
            excel_dados = df.to_dict(orient="records")
        else:
            erro = "Nenhum resultado encontrado."

        if q and not aba_selecionada:
            abas_filtradas = []
            abas_sem_resultado = []
            for nome_aba, df in dfs_por_aba.items():
                mask = df.astype(str).apply(lambda col: col.str.contains(q, case=False, na=False)).any(axis=1)
                df_filtrado = df[mask]
                if not df_filtrado.empty:
                    abas_filtradas.append(nome_aba)
                else:
                    abas_sem_resultado.append(nome_aba)

    except Excel.DoesNotExist:
        erro = "Nenhum arquivo Excel foi enviado ainda."
    except Exception as e:
        erro = f"Erro ao carregar o arquivo: {e}"

    contexto = {
        "erro": erro,
        "ExcelDados": excel_dados,
        "abas": abas_disponiveis,
        "abas_sem_resultado": abas_sem_resultado,   
        "aba_selecionada": aba,
        "form": form,
        "q": q
    }

    return render(request, 'ExcelInterface/table.html', contexto)
