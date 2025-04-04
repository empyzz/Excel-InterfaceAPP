from django.db import models

# Create your models here.

class Excel(models.Model):
    nome = models.CharField(max_length=50)
    arquivo = models.FileField(upload_to="uploads/excel")
    data = models.DateField(auto_now_add=True)
    
    def __str__(self):
        return self.nome