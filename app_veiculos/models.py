import random
import string

from django.db import models

# Create your models here.


def gerar_identificador_unico():
    """
    Gera um identificador único alfanumérico de 8 caracteres,
    excluindo caracteres ambíguos como 'O', '0', 'I', 'L', e '1'.
    """
    caracteres = string.ascii_uppercase + string.digits
    caracteres = caracteres.replace('O', '').replace('0', '')\
        .replace('I', '').replace('L', '').replace('1', '')
    return ''.join(random.choices(caracteres, k=8))


class VeiculoBase(models.Model):
    usuario = models.ForeignKey(
        'app_usuarios.Usuario',
        on_delete=models.CASCADE,
        related_name='veiculos',
        verbose_name='Usuário'
    )
    identificador_unico_veiculo = models.CharField(
        max_length=8,
        unique=True,
        default=gerar_identificador_unico,
        editable=False,
        verbose_name='Identificador Único do Veículo',
        help_text=(
            'Código único para identificação do veículo '
            '(alfanumérico de 8 caracteres)'
        )
    )
    placa = models.CharField(
        max_length=10,
        unique=True,
        verbose_name='Placa'
    )
    renavam = models.CharField(
        max_length=20,
        unique=True,
        verbose_name='RENAVAM'
    )
    chassi = models.CharField(
        max_length=17,
        unique=True,
        verbose_name='Chassi'
    )
    marca = models.CharField(
        max_length=50,
        verbose_name='Marca'
    )
    modelo = models.CharField(
        max_length=50,
        verbose_name='Modelo'
    )
    cor = models.CharField(
        max_length=30,
        verbose_name='Cor'
    )
    anoFabricacao = models.PositiveIntegerField(
        verbose_name='Ano de Fabricação'
    )
    anoLimiteFabricacao = models.PositiveIntegerField(
        verbose_name='Ano Limite de Fabricação'
    )

    class Meta:
        abstract = True
        verbose_name = 'Veículo (Base)'
        verbose_name_plural = 'Veículos (Base)'

    def __str__(self):  # noqa: D401
        return (
            f'{self.identificador_unico_veiculo} - {self.modelo} '
            f'({self.placa})'
        )


class TaxiVeiculo(VeiculoBase):  # noqa: D101
    class Meta:
        verbose_name = 'Táxi'
        verbose_name_plural = 'Táxis'


class MotoTaxiVeiculo(VeiculoBase):  # noqa: D101

    class Meta:
        verbose_name = 'Mototáxi'
        verbose_name_plural = 'Mototáxis'


class TransporteMunicipalVeiculo(VeiculoBase):  # noqa: D101
    linha = models.CharField(
        max_length=50,
        verbose_name='Linha / Rota',
        help_text='Identificação da linha ou rota do transporte municipal'
    )
    capacidade = models.PositiveIntegerField(
        verbose_name='Capacidade',
        help_text='Número máximo de passageiros'
    )

    class Meta:
        verbose_name = 'Transporte Municipal'
        verbose_name_plural = 'Transportes Municipais'
