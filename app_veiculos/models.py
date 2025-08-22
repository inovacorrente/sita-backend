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


def upload_banner_to(instance, filename):
    """
    Gera o caminho dinâmico para upload do banner baseado no tipo de veículo.

    Padrão: banners_identificacao/veiculo/{tipo_veiculo}/
             {identificador_veiculo}/
    """
    # Obter o veículo
    veiculo = (instance.get_veiculo() if hasattr(instance, 'get_veiculo')
               else None)

    if not veiculo:
        # Fallback para o padrão antigo se não conseguir obter o veículo
        return f'banners_identificacao/{filename}'

    # Mapear tipos de veículo para nomes de diretório
    tipo_veiculo_map = {
        'TaxiVeiculo': 'taxi',
        'MotoTaxiVeiculo': 'mototaxi',
        'TransporteMunicipalVeiculo': 'transporte_municipal'
    }

    # Obter nome do tipo de veículo
    tipo_veiculo = veiculo.__class__.__name__
    tipo_dir = tipo_veiculo_map.get(tipo_veiculo, 'outro')

    # Obter identificador do veículo
    identificador = veiculo.identificador_unico_veiculo

    # Construir caminho
    return (f'banners_identificacao/veiculo/{tipo_dir}/'
            f'{identificador}/{filename}')


class BannerIdentificacao(models.Model):
    """
    Modelo para armazenar banners de identificação dos veículos.
    """
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        help_text="Tipo do modelo do veículo",
        related_name='banners_identificacao',
        editable=False,
    )
    object_id = models.PositiveIntegerField(
        help_text="ID do veículo (campo legado para compatibilidade)",
        editable=False,
        null=True,
        blank=True
    )
    identificador_unico_veiculo = models.CharField(
        max_length=8,
        help_text="Identificador único do veículo",
        editable=False,
        db_index=True
    )
    veiculo = GenericForeignKey('content_type', 'object_id')

    arquivo_banner = models.ImageField(
        upload_to=upload_banner_to,
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
        unique_together = ['content_type', 'identificador_unico_veiculo']

    @property
    def veiculo_por_identificador(self):
        """
        Retorna o veículo baseado no identificador único.
        """
        if not self.content_type or not self.identificador_unico_veiculo:
            return None

        model_class = self.content_type.model_class()
        try:
            return model_class.objects.get(
                identificador_unico_veiculo=self.identificador_unico_veiculo
            )
        except model_class.DoesNotExist:
            return None

    def get_veiculo(self):
        """
        Método unificado para obter o veículo.
        Prioriza o identificador único, mas fallback para object_id
        se necessário.
        """
        # Primeiro tenta pelo identificador único
        veiculo = self.veiculo_por_identificador
        if veiculo:
            return veiculo

        # Fallback para o GenericForeignKey tradicional (compatibilidade)
        return self.veiculo

    def save(self, *args, **kwargs):
        """
        Sobrescreve save para garantir consistência entre object_id e
        identificador_unico_veiculo.
        """
        # Se temos identificador único mas não object_id, buscar object_id
        if (self.identificador_unico_veiculo and not self.object_id and
                self.content_type):
            veiculo = self.veiculo_por_identificador
            if veiculo:
                self.object_id = veiculo.id

        # Se temos object_id mas não identificador único, buscar identificador
        elif (self.object_id and not self.identificador_unico_veiculo and
              self.content_type):
            veiculo = self.veiculo
            if veiculo:
                self.identificador_unico_veiculo = (
                    veiculo.identificador_unico_veiculo
                )

        super().save(*args, **kwargs)

    def __str__(self):
        veiculo = self.get_veiculo()
        if veiculo:
            identificador = veiculo.identificador_unico_veiculo
            placa = veiculo.placa
            return f"Banner - {placa} ({identificador})"
        return f"Banner #{self.id}"

    def gerar_banner(self):
        """
        Gera um novo banner com QR Code para o veículo.
        """
        from utils.app_veiculos.qr_code import criar_banner_com_qr
        from utils.commons.urls import get_veiculo_info_url

        veiculo = self.get_veiculo()
        if not veiculo:
            raise ValueError("Veículo não encontrado para gerar banner")

        # Construir URL para visualização das informações do veículo
        identificador = veiculo.identificador_unico_veiculo
        qr_url = get_veiculo_info_url(identificador)

        # Gerar banner
        banner_io = criar_banner_com_qr(
            identificador_veiculo=veiculo.identificador_unico_veiculo,
            placa=veiculo.placa,
            usuario_id=veiculo.usuario.id,
            qr_url=qr_url
        )

        # Salvar arquivo
        identificador = veiculo.identificador_unico_veiculo
        placa = veiculo.placa
        filename = f"banner_{identificador}_{placa}.png"
        self.arquivo_banner.save(
            filename,
            ContentFile(banner_io.read()),
            save=False
        )

        self.qr_url = qr_url
        self.save()
