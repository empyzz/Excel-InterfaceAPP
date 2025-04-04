from django.contrib import admin
from .models import *


class ExcelAdmin(admin.ModelAdmin):
    list_display = ('nome','arquivo','data')



admin.site.register(Excel, ExcelAdmin)