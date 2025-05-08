from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from .forms import *
from .models import *
from django.core.exceptions import ValidationError
from django.core.cache import cache
import pandas as pd
import json

def home(request):
    q = request.GET.get('q')
    form = ExcelUploadForm()
    erro = None
    excel_dados = None
    abas_disponiveis = []
    abas_filtradas = []
    abas_sem_resultado = []
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
        
        dfs_filtrados = {}
        if q:
            for nome_aba, df in dfs_por_aba.items():
                mask = df.astype(str).apply(lambda col: col.str.contains(q, case=False, na=False)).any(axis=1)
                df_filtrado = df[mask]
                dfs_filtrados[nome_aba] = df_filtrado

                if df_filtrado.empty:
                    abas_sem_resultado.append(nome_aba)
                else:
                    abas_filtradas.append(nome_aba)

            aba = aba_selecionada if aba_selecionada else (abas_filtradas[0] if abas_filtradas else abas_disponiveis[0])
            df = dfs_filtrados.get(aba, dfs_por_aba[aba])
        else:
            aba = aba_selecionada or abas_disponiveis[0]
            df = dfs_por_aba[aba]

        df = dfs_por_aba[aba]

        if q:
            df = df[df.apply(lambda row: row.astype(str).str.contains(q, case=False, na=False).any(), axis=1)]

        if not df.empty:
            excel_dados = df.to_dict(orient="records")
        else:
            erro = "Nenhum resultado encontrado."

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


def ChecklistPagina(request):
    checklists = Checklist.objects.all()
    return render(request, 'ExcelInterface/checklist.html', {'checklists': checklists})


def get_abas_do_excel(file_path):
    try:
        excel = pd.ExcelFile(file_path)
        return excel.sheet_names
    except Exception as e:
        return []


def criar_checklist(request):
    abas = []
    try:
        ultimo_excel = Excel.objects.latest('data')
        caminho_arquivo = ultimo_excel.arquivo.path
        abas = get_abas_do_excel(caminho_arquivo)
    except Excel.DoesNotExist:
        messages.warning(request, "Nenhum arquivo Excel foi enviado ainda.")
    except Exception as e:
        messages.error(request, f"Erro ao carregar abas do Excel: {e}")

    if request.method == 'POST':
        form = CheckListForm(request.POST, abas=abas)
        if form.is_valid():
            checklist = form.save()

            # Pega os itens do campo oculto (JSON)
            itens_json = request.POST.get('itens_json', '[]')
            try:
                itens = json.loads(itens_json)
                for item in itens:
                    ChecklistITEM.objects.create(
                        Lista=checklist,
                        nome_item=item.get('nome', ''),
                        descricaoItem=item.get('descricao', ''),
                    )
            except json.JSONDecodeError:
                messages.error(request, "Erro ao processar os itens adicionados.")

            messages.success(request, f"Checklist '{checklist.nome_lista}' criada com sucesso!")
            return redirect('Checklist')  # ou qualquer nome da URL da listagem
    else:
        form = CheckListForm(abas=abas)

    return render(request, 'ExcelInterface/Criarchecklist.html', {'form': form})
            
    
def atualizar_status_item(request):
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        novo_status = request.POST.get('status') == 'true'

        try:
            item = ChecklistITEM.objects.get(id=item_id)
            item.statusItem = novo_status
            item.save()
            return JsonResponse({'success': True})
        except ChecklistITEM.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Item não encontrado'})

    return JsonResponse({'success': False, 'error': 'Método inválido'})


def DeletarLista(request, item_type, objetoId):
    if request.method == "DELETE":
        print(f"Deletando item: {item_type} com ID {objetoId}")
        
        item = get_object_or_404(Checklist, pk=objetoId)
        item.delete()
        
        return JsonResponse({'message': 'Objeto excluído com sucesso.'}, status=200)
    return JsonResponse({'error': 'Método não permitido'}, status=405)