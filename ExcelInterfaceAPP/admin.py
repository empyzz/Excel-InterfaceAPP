from django.contrib import admin
from .models import *


class ExcelAdmin(admin.ModelAdmin):
    list_display = ('nome', 'arquivo', 'data')


class ChecklistAdmin(admin.ModelAdmin):
    list_display = ('nome_lista', 'excel', 'aba', 'data_criacao')
    search_fields = ('nome_lista', 'aba')
    list_filter = ('data_criacao', 'excel')


class ChecklistItemAdmin(admin.ModelAdmin):
    list_display = ('nome_item', 'Lista', 'statusItem')
    list_filter = ('statusItem',)
    search_fields = ('nome_item', 'Lista__nome_lista')


admin.site.register(Excel, ExcelAdmin)
admin.site.register(Checklist, ChecklistAdmin)
admin.site.register(ChecklistITEM, ChecklistItemAdmin)