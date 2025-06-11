from django.db import models

# Create your models here.

class Excel(models.Model):
    nome = models.CharField(max_length=50)
    arquivo = models.FileField(upload_to="uploads/excel")
    data = models.DateField(auto_now_add=True)
    
    def __str__(self):
        return self.nome
    

class CheckboxStatus(models.Model):
    aba = models.CharField(max_length=100)
    linha_index = models.IntegerField()
    coluna = models.CharField(max_length=100)
    checked = models.BooleanField(default=False)

    class Meta:
        unique_together = ('aba', 'linha_index', 'coluna')


class TextStatus(models.Model):
    aba = models.CharField(max_length=100)
    linha_index = models.IntegerField()
    coluna = models.CharField(max_length=100)
    texto = models.CharField(max_length=50)

    class Meta:
        unique_together = ('aba', 'linha_index', 'coluna')


class Checklist(models.Model):
    excel = models.ForeignKey(Excel, on_delete=models.CASCADE, related_name="checklist")
    aba = models.CharField(max_length=100)
    nome_lista = models.CharField(max_length=100)
    descricao_lista = models.TextField(blank=True)
    data_criacao = models.DateField(auto_now_add=True)
    
    def __str__(self):
        return f"Checklist para {self.excel} - {self.nome_lista} ({self.aba})"
    
    
class ChecklistITEM(models.Model):
    Lista = models.ForeignKey(Checklist, on_delete=models.CASCADE, related_name="ItemLista")
    nome_item = models.CharField(max_length=255)
    statusItem = models.BooleanField(default=False)
    descricaoItem = models.TextField(blank=True)
    
    
    def __str__(self):
        return f"{self.nome_item} - {self.Lista} "