from django.db import models
from apps.usuario.models import User

class Cliente(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Usuário")
    codigo_cadastro = models.PositiveIntegerField(null=False, blank=False, verbose_name="Código de Cadastro")
    data_criacao = models.DateTimeField(auto_now_add=True, null=False, blank=False, verbose_name='Data de Criação')

    def __str__(self):
        return 
