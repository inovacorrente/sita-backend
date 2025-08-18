from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

# Create your models here.


def upload_documento_path(instance, filename):
    """Gera caminho: documentos/<matricula>/<id_veiculo>/<arquivo>.

    Facilita organização por usuário e veículo.
    """
    veiculo = instance.get_veiculo()
    matricula = veiculo.usuario.matricula
    ident_veiculo = veiculo.identificador_unico_veiculo
    return f'documentos/{matricula}/{ident_veiculo}/{filename}'


class Documento(models.Model):
    # GenericForeignKey para referenciar qualquer tipo de veículo
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        limit_choices_to={
            'app_label': 'app_veiculos',
            'model__in': [
                'taxiveiculo',
                'mototaxiveiculo',
                'transportemunicipalveiculo'
            ]
        }
    )
    object_id = models.PositiveIntegerField()
    veiculo = GenericForeignKey('content_type', 'object_id')

    documento = models.FileField(
        upload_to=upload_documento_path, verbose_name='Documento')
    data_criacao = models.DateTimeField(
        auto_now_add=True, verbose_name='Data de Criação')
    data_alteracao = models.DateTimeField(
        auto_now=True, verbose_name='Data de Alteração')

    def get_veiculo(self):
        """Retorna o objeto veículo associado."""
        return self.veiculo

    class Meta:
        verbose_name = 'Documento'
        verbose_name_plural = 'Documentos'
