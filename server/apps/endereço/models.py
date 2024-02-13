from django.db import models
from django.core.exceptions import ValidationError
from apps.usuario.models import User
import requests

class Endereco(models.Model):

    def validar_cep(cep):
        """
        Essa função serve para verificar se um CEP é válido! 
        verifica se está corretamente formatado e se o CEP existe!
        """
        if (len(str(cep).replace("-", "")) != 8) or not (str(cep).replace("-", "").isdigit()):
            raise ValidationError("CEP inválido!")
        else:
            response = requests.get(f"https://viacep.com.br/ws/{cep}/json/")
            data = response.json()
            if 'erro' in data:
                raise ValidationError("CEP inválido ou não encontrado")

    usuario = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="Usuário")
    bairro = models.CharField(max_length=100, null=False, blank=False)
    cidade = models.CharField(max_length=200, null=False, blank=False)
    estado = models.CharField(max_length=200, null=False, blank=False)
    logradouro = models.CharField(max_length=200, null=False, blank=False)
    numero = models.PositiveIntegerField(null=False, blank=False, verbose_name="Número")
    complemento = models.CharField(max_length=200, null=False, blank=False)
    cep = models.CharField(max_length=200, null=False, blank=False, validators=[validar_cep], verbose_name="CEP")

    def __str__(self):
        return self.cep

    class Meta:
        verbose_name_plural = "Endereços"