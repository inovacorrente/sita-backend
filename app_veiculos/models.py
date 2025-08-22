import random
import string

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.files.base import ContentFile
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
        'app_usuarios.UsuarioCustom',
        on_delete=models.CASCADE,
        related_name='%(class)s_veiculos',  # Usar nome da classe dinâmico
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


class BannerIdentificacao(models.Model):
    """
    Modelo para armazenar banners de identificação dos veículos.
    """
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        help_text="Tipo do modelo do veículo"
    )
    object_id = models.PositiveIntegerField(
        help_text="ID do veículo"
    )
    veiculo = GenericForeignKey('content_type', 'object_id')

    arquivo_banner = models.ImageField(
        upload_to='banners_identificacao/',
        help_text="Arquivo do banner com QR Code"
    )
    qr_url = models.URLField(
        max_length=500,
        help_text="URL codificada no QR Code"
    )
    data_criacao = models.DateTimeField(
        auto_now_add=True,
        help_text="Data de criação do banner"
    )
    data_atualizacao = models.DateTimeField(
        auto_now=True,
        help_text="Data da última atualização"
    )
    ativo = models.BooleanField(
        default=True,
        help_text="Indica se o banner está ativo"
    )

    class Meta:
        verbose_name = "Banner de Identificação"
        verbose_name_plural = "Banners de Identificação"
        db_table = 'banner_identificacao'
        unique_together = ['content_type', 'object_id']

    def __str__(self):
        if self.veiculo:
            identificador = self.veiculo.identificador_unico_veiculo
            placa = self.veiculo.placa
            return f"Banner - {placa} ({identificador})"
        return f"Banner #{self.id}"

    def gerar_banner(self):
        """
        Gera um novo banner com QR Code para o veículo.
        """
        from utils.app_veiculos.qr_code import criar_banner_com_qr
        from utils.commons.urls import get_veiculo_info_url

        # Construir URL para visualização das informações do veículo
        identificador = self.veiculo.identificador_unico_veiculo
        qr_url = get_veiculo_info_url(identificador)

        # Gerar banner
        banner_io = criar_banner_com_qr(
            identificador_veiculo=self.veiculo.identificador_unico_veiculo,
            placa=self.veiculo.placa,
            usuario_id=self.veiculo.usuario.id,
            qr_url=qr_url
        )

        # Salvar arquivo
        identificador = self.veiculo.identificador_unico_veiculo
        placa = self.veiculo.placa
        filename = f"banner_{identificador}_{placa}.png"
        self.arquivo_banner.save(
            filename,
            ContentFile(banner_io.read()),
            save=False
        )

        self.qr_url = qr_url
        self.save()
