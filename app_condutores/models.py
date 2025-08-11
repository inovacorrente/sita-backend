from django.db import models

from app_usuarios.models import UsuarioCustom

# Create your models here.


class Condutor(models.Model):
    """
    Modelo para armazenar informações de condutores.
    Cada condutor está vinculado a um usuário do sistema.
    """
    usuario = models.OneToOneField(
        UsuarioCustom,
        on_delete=models.CASCADE,
        related_name='condutor',
        help_text='Usuário associado a este condutor.'
    )
    categoria_cnh = models.CharField(
        max_length=4,
        blank=False,
        null=False,
        help_text='Categoria da CNH do condutor. Exemplos: A, B, C, D, E, AD.'
    )
    data_validade_cnh = models.DateField(
        help_text='Data de validade da CNH (formato AAAA-MM-DD).'
    )
    data_emissao_cnh = models.DateField(
        help_text='Data de emissão da CNH (formato AAAA-MM-DD).'
    )
    data_criacao = models.DateTimeField(
        auto_now_add=True,
        help_text='Data e hora em que o registro do condutor foi criado.'
    )
    data_atualizacao = models.DateTimeField(
        auto_now=True,
        help_text='Data e hora da última atualização das informações do condutor.'
    )

    class Meta:
        verbose_name = 'condutor'
        verbose_name_plural = 'condutores'

    def __str__(self):
        """
        Retorna a representação textual do condutor,
        incluindo o nome do usuário e a categoria da CNH.
        """
        return f'Condutor: {self.usuario.nome_completo} - {self.categoria_cnh}'
