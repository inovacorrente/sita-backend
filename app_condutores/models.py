from django.db import models

from app_usuarios.models import UsuarioCustom

# Create your models here.


class Condutor(models.Model):
    """
    Modelo para armazenar informações de condutores.
    """
    usuario = models.OneToOneField(
        UsuarioCustom,
        on_delete=models.CASCADE,
        related_name='condutor',
        help_text='Usuário associado ao condutor',
    )
    categoria_cnh = models.CharField(
        max_length=4,
        blank=False,
        null=False,
        help_text='Ex: A, B, C, D, E, AD',
    )
    data_validade_cnh = models.DateField()
    data_emissao_cnh = models.DateField()
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'app_condutores'
        verbose_name = 'condutor'
        verbose_name_plural = 'condutores'

    def __str__(self):
        return f'Condutor: {self.usuario.nome_completo} - {self.categoria_cnh}'
