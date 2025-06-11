from django.urls import path, include
from templates import *
from  . import views

urlpatterns = [
    path('', views.home, name='home'),
    path("Checklist/", views.ChecklistPagina, name="Checklist"),
    path('NovaChecklist/', views.criar_checklist, name="Nova-CheckList"),
    path('abrir-checklist/<int:checklist_id>/', views.abrir_checklist, name='abrir-checklist'),
    path('atualizar_status_item/', views.atualizar_status_item, name='atualizar_status_item'),
    path('deletar_lista/<str:item_type>/<int:objetoId>/', views.DeletarLista, name='Deletar_lista'),
    path('exportar_excel/', views.exportar_todas_planilhas, name='exportar_excel'),
    path('importar-planilha/', views.importar_planilha, name='importar_planilha'),

]
