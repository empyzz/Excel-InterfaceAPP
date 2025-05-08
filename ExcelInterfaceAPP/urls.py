from django.urls import path, include
from templates import *
from  . import views

urlpatterns = [
    path('', views.home, name='home'),
    path("Checklist/", views.ChecklistPagina, name="Checklist"),
    path('NovaChecklist/', views.criar_checklist, name="Nova-CheckList"),
    path('atualizar_status_item/', views.atualizar_status_item, name='atualizar_status_item'),
    path('deletar_lista/<str:item_type>/<int:objetoId>/', views.DeletarLista, name='Atualizar_Status_item'),
]
