from django.db import models

from app_veiculos.models import Veiculo

# Create your models here.


def upload_documento_path(instance, filename):
    """Gera caminho: documentos/<matricula>/<id_veiculo>/<arquivo>.

    Facilita organização por usuário e veículo.
    """
    matricula = instance.veiculo.usuario.matricula
    ident_veiculo = instance.veiculo.identificador_unico_veiculo
    return f'documentos/{matricula}/{ident_veiculo}/{filename}'


class Documento(models.Model):
    veiculo = models.ForeignKey(
        Veiculo,
        on_delete=models.CASCADE,
        related_name='documentos',
        verbose_name='Veículo'
    )
    documento = models.FileField(
        upload_to=upload_documento_path, verbose_name='Documento')
    data_criacao = models.DateTimeField(
        auto_now_add=True, verbose_name='Data de Criação')
    data_alteracao = models.DateTimeField(
        auto_now=True, verbose_name='Data de Alteração')

    class Meta:
        verbose_name = 'Documento'
    verbose_name_plural = 'Documentos'
