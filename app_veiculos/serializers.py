"""
Serializers para o app de veículos do sistema SITA.
Inclui serializers para todos os tipos de veículos (Táxi, Mototáxi,
Transporte Municipal).
"""
from django.core.exceptions import ValidationError
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from app_usuarios.models import UsuarioCustom
from app_usuarios.serializers import UsuarioCustomViewSerializer
from utils.app_veiculos.validators import (
    validate_ano_fabricacao, validate_ano_limite_fabricacao,
    validate_anos_fabricacao_consistencia, validate_capacidade_transporte,
    validate_chassi, validate_cor_veiculo, validate_linha_transporte,
    validate_marca_modelo_length, validate_placa_br, validate_renavam,
    validate_usuario_exists, validate_veiculo_unique_fields)

from .models import MotoTaxiVeiculo, TaxiVeiculo, TransporteMunicipalVeiculo

# ============================================================================
# SERIALIZERS BASE
# ============================================================================


class VeiculoBaseSerializer(serializers.ModelSerializer):
    """
    Serializer base para todos os tipos de veículos.
    Contém validações comuns e campos compartilhados.
    """
    matricula_usuario = serializers.CharField(
        write_only=True,
        help_text="Matrícula ou email do usuário proprietário do veículo"
    )
    usuario_detalhes = UsuarioCustomViewSerializer(
        source='usuario',
        read_only=True,
        help_text="Detalhes do usuário proprietário"
    )
    identificador_unico_veiculo = serializers.CharField(
        read_only=True,
        help_text="Identificador único do veículo gerado automaticamente"
    )

    class Meta:
        fields = [
            'id',
            'identificador_unico_veiculo',
            'matricula_usuario',
            'usuario_detalhes',
            'placa',
            'renavam',
            'chassi',
            'marca',
            'modelo',
            'cor',
            'anoFabricacao',
            'anoLimiteFabricacao',
        ]
        extra_kwargs = {
            'placa': {
                'help_text': (
                    'Placa do veículo (formato brasileiro: '
                    'AAA-9999 ou AAA9A99)'
                )
            },
            'renavam': {
                'help_text': 'RENAVAM do veículo (11 dígitos)'
            },
            'chassi': {
                'help_text': 'Número do chassi (17 caracteres alfanuméricos)'
            },
            'marca': {
                'help_text': 'Marca do veículo'
            },
            'modelo': {
                'help_text': 'Modelo do veículo'
            },
            'cor': {
                'help_text': 'Cor do veículo'
            },
            'anoFabricacao': {
                'help_text': 'Ano de fabricação do veículo'
            },
            'anoLimiteFabricacao': {
                'help_text': 'Ano limite de fabricação do veículo'
            },
        }

    def validate_matricula_usuario(self, value):
        """Valida se o usuário existe e está ativo (por matrícula ou email)."""
        try:
            return validate_usuario_exists(value)
        except ValidationError as e:
            # Re-lança como ValidationError do DRF com mensagem específica
            raise serializers.ValidationError(str(e))

    def validate_placa(self, value):
        """Valida formato da placa brasileira."""
        return validate_placa_br(value)

    def validate_renavam(self, value):
        """Valida RENAVAM brasileiro."""
        return validate_renavam(value)

    def validate_chassi(self, value):
        """Valida número do chassi."""
        return validate_chassi(value)

    def validate_marca(self, value):
        """Valida marca do veículo."""
        return validate_marca_modelo_length(value, 'marca')

    def validate_modelo(self, value):
        """Valida modelo do veículo."""
        return validate_marca_modelo_length(value, 'modelo')

    def validate_cor(self, value):
        """Valida cor do veículo."""
        return validate_cor_veiculo(value)

    def validate_anoFabricacao(self, value):
        """Valida ano de fabricação."""
        return validate_ano_fabricacao(value)

    def validate_anoLimiteFabricacao(self, value):
        """Valida ano limite de fabricação."""
        return validate_ano_limite_fabricacao(value)

    def validate(self, attrs):
        """Validações cruzadas e gerais."""
        # Valida consistência entre anos de fabricação
        ano_fabricacao = attrs.get('anoFabricacao')
        ano_limite = attrs.get('anoLimiteFabricacao')

        if ano_fabricacao and ano_limite:
            validate_anos_fabricacao_consistencia(ano_fabricacao, ano_limite)

        # Valida unicidade dos campos críticos
        placa = attrs.get('placa')
        renavam = attrs.get('renavam')
        chassi = attrs.get('chassi')

        validate_veiculo_unique_fields(
            placa=placa,
            renavam=renavam,
            chassi=chassi,
            instance=self.instance
        )

        return attrs

    def create(self, validated_data):
        """Cria um novo veículo com o usuário associado."""
        try:
            matricula_usuario = validated_data.pop('matricula_usuario')

            # Busca o usuário pela matrícula
            try:
                usuario = UsuarioCustom.objects.get(
                    matricula=matricula_usuario
                )
            except UsuarioCustom.DoesNotExist:
                raise serializers.ValidationError({
                    'matricula_usuario': (
                        f"Usuário com matrícula '{matricula_usuario}' "
                        "não encontrado"
                    )
                })

            if not usuario.is_active:
                raise serializers.ValidationError({
                    'matricula_usuario': (
                        f"Usuário com matrícula '{matricula_usuario}' "
                        "está inativo"
                    )
                })

            validated_data['usuario'] = usuario
            return super().create(validated_data)

        except KeyError:
            raise serializers.ValidationError({
                'matricula_usuario': 'Matrícula do usuário é obrigatória'
            })

    def update(self, instance, validated_data):
        """Atualiza um veículo existente."""
        matricula_usuario = validated_data.pop('matricula_usuario', None)
        if matricula_usuario:
            try:
                usuario = UsuarioCustom.objects.get(
                    matricula=matricula_usuario
                )
            except UsuarioCustom.DoesNotExist:
                raise serializers.ValidationError({
                    'matricula_usuario': (
                        f"Usuário com matrícula '{matricula_usuario}' "
                        "não encontrado"
                    )
                })

            if not usuario.is_active:
                raise serializers.ValidationError({
                    'matricula_usuario': (
                        f"Usuário com matrícula '{matricula_usuario}' "
                        "está inativo"
                    )
                })

            validated_data['usuario'] = usuario
        return super().update(instance, validated_data)


# ============================================================================
# SERIALIZERS ESPECÍFICOS POR TIPO DE VEÍCULO
# ============================================================================

class TaxiVeiculoSerializer(VeiculoBaseSerializer):
    """
    Serializer para veículos de táxi.
    Herda todas as validações e campos do VeiculoBaseSerializer.
    """

    class Meta(VeiculoBaseSerializer.Meta):
        model = TaxiVeiculo


class TaxiVeiculoCreateSerializer(TaxiVeiculoSerializer):
    """
    Serializer para criação de veículos de táxi.
    Remove campos de leitura para foco na criação.
    """

    class Meta(TaxiVeiculoSerializer.Meta):
        fields = [
            'matricula_usuario',
            'placa',
            'renavam',
            'chassi',
            'marca',
            'modelo',
            'cor',
            'anoFabricacao',
            'anoLimiteFabricacao',
        ]


class TaxiVeiculoViewSerializer(TaxiVeiculoSerializer):
    """
    Serializer para visualização de veículos de táxi.
    Inclui todos os campos para exibição completa.
    """
    pass


class MotoTaxiVeiculoSerializer(VeiculoBaseSerializer):
    """
    Serializer para veículos de mototáxi.
    Herda todas as validações e campos do VeiculoBaseSerializer.
    """

    class Meta(VeiculoBaseSerializer.Meta):
        model = MotoTaxiVeiculo


class MotoTaxiVeiculoCreateSerializer(MotoTaxiVeiculoSerializer):
    """
    Serializer para criação de veículos de mototáxi.
    Remove campos de leitura para foco na criação.
    """

    class Meta(MotoTaxiVeiculoSerializer.Meta):
        fields = [
            'matricula_usuario',
            'placa',
            'renavam',
            'chassi',
            'marca',
            'modelo',
            'cor',
            'anoFabricacao',
            'anoLimiteFabricacao',
        ]


class MotoTaxiVeiculoViewSerializer(MotoTaxiVeiculoSerializer):
    """
    Serializer para visualização de veículos de mototáxi.
    Inclui todos os campos para exibição completa.
    """
    pass


class TransporteMunicipalVeiculoSerializer(VeiculoBaseSerializer):
    """
    Serializer para veículos de transporte municipal.
    Inclui campos específicos como linha e capacidade.
    """

    class Meta(VeiculoBaseSerializer.Meta):
        model = TransporteMunicipalVeiculo
        fields = VeiculoBaseSerializer.Meta.fields + [
            'linha',
            'capacidade',
        ]
        extra_kwargs = {
            **VeiculoBaseSerializer.Meta.extra_kwargs,
            'linha': {
                'help_text': 'Linha ou rota do transporte municipal'
            },
            'capacidade': {
                'help_text': 'Capacidade máxima de passageiros'
            },
        }

    def validate_linha(self, value):
        """Valida linha/rota do transporte."""
        return validate_linha_transporte(value)

    def validate_capacidade(self, value):
        """Valida capacidade de passageiros."""
        return validate_capacidade_transporte(value)


class TransporteMunicipalVeiculoCreateSerializer(
    TransporteMunicipalVeiculoSerializer
):
    """
    Serializer para criação de veículos de transporte municipal.
    Remove campos de leitura para foco na criação.
    """

    class Meta(TransporteMunicipalVeiculoSerializer.Meta):
        fields = [
            'matricula_usuario',
            'placa',
            'renavam',
            'chassi',
            'marca',
            'modelo',
            'cor',
            'anoFabricacao',
            'anoLimiteFabricacao',
            'linha',
            'capacidade',
        ]


class TransporteMunicipalVeiculoViewSerializer(
    TransporteMunicipalVeiculoSerializer
):
    """
    Serializer para visualização de veículos de transporte municipal.
    Inclui todos os campos para exibição completa.
    """
    pass


# ============================================================================
# SERIALIZERS PARA LISTAGEM E BUSCA
# ============================================================================

class VeiculoResumoSerializer(serializers.ModelSerializer):
    """
    Serializer resumido para listagens de veículos.
    Inclui apenas campos essenciais para performance.
    """
    usuario_nome = serializers.CharField(
        source='usuario.nome_completo',
        read_only=True
    )
    tipo_veiculo = serializers.SerializerMethodField()

    class Meta:
        model = TaxiVeiculo  # Modelo base para campos comuns
        fields = [
            'id',
            'identificador_unico_veiculo',
            'placa',
            'marca',
            'modelo',
            'cor',
            'anoFabricacao',
            'usuario_nome',
            'tipo_veiculo',
        ]

    def get_tipo_veiculo(self, obj):
        """Retorna o tipo do veículo baseado na classe."""
        if isinstance(obj, TaxiVeiculo):
            return 'Táxi'
        elif isinstance(obj, MotoTaxiVeiculo):
            return 'Mototáxi'
        elif isinstance(obj, TransporteMunicipalVeiculo):
            return 'Transporte Municipal'
        return 'Desconhecido'


# ============================================================================
# SERIALIZERS PARA BANNER DE IDENTIFICAÇÃO
# ============================================================================

class BannerIdentificacaoSerializer(serializers.ModelSerializer):
    """
    Serializer para banner de identificação de veículos.
    """
    identificador_veiculo = serializers.CharField(
        source='identificador_unico_veiculo',
        read_only=True,
        help_text="Identificador único do veículo"
    )
    veiculo_placa = serializers.CharField(
        source='veiculo.placa',
        read_only=True
    )
    veiculo_marca = serializers.CharField(
        source='veiculo.marca',
        read_only=True
    )
    veiculo_modelo = serializers.CharField(
        source='veiculo.modelo',
        read_only=True
    )
    veiculo_tipo = serializers.SerializerMethodField()
    proprietario_nome = serializers.CharField(
        source='veiculo.usuario.nome_completo',
        read_only=True
    )
    banner_url_completa = serializers.SerializerMethodField()
    qr_url_completa = serializers.SerializerMethodField()

    class Meta:
        from .models import BannerIdentificacao
        model = BannerIdentificacao
        fields = [
            'identificador_veiculo',
            'veiculo_placa',
            'veiculo_marca',
            'veiculo_modelo',
            'veiculo_tipo',
            'proprietario_nome',
            'arquivo_banner',
            'banner_url_completa',
            'qr_url',
            'qr_url_completa',
            'data_criacao',
            'data_atualizacao',
            'ativo'
        ]
        read_only_fields = [
            'content_type',
            'object_id',
            'arquivo_banner',
            'qr_url',
            'data_criacao',
            'data_atualizacao'
        ]

    @extend_schema_field(serializers.CharField())
    def get_veiculo_tipo(self, obj) -> str:
        """
        Retorna o tipo do veículo baseado no content_type.
        """
        if obj.content_type:
            return obj.content_type.model
        return None

    @extend_schema_field(serializers.URLField())
    def get_banner_url_completa(self, obj) -> str:
        """
        Retorna URL completa do arquivo do banner.
        """
        from utils.commons.urls import build_media_url

        if not obj.arquivo_banner:
            return None

        request = self.context.get('request')
        return build_media_url(obj.arquivo_banner.url, request)

    @extend_schema_field(serializers.URLField())
    def get_qr_url_completa(self, obj) -> str:
        """
        Retorna URL completa para informações do veículo (QR Code).
        """
        from utils.commons.urls import get_veiculo_info_url

        if not obj.veiculo:
            return None

        request = self.context.get('request')
        return get_veiculo_info_url(
            obj.veiculo.identificador_unico_veiculo,
            request
        )


class BannerCreateSerializer(serializers.Serializer):
    """
    Serializer para criação de banner de identificação.
    """
    identificador_veiculo = serializers.CharField(max_length=8)

    def validate_identificador_veiculo(self, value):
        """
        Valida se o veículo existe e se o usuário tem permissão.
        """
        from django.contrib.contenttypes.models import ContentType

        # Buscar em todos os tipos de veículo
        veiculo = None
        content_type = None

        for model_class in [TaxiVeiculo, MotoTaxiVeiculo,
                            TransporteMunicipalVeiculo]:
            try:
                veiculo = model_class.objects.get(
                    identificador_unico_veiculo=value
                )
                content_type = ContentType.objects.get_for_model(model_class)
                break
            except model_class.DoesNotExist:
                continue

        if not veiculo:
            raise serializers.ValidationError("Veículo não encontrado.")

        # Verificar se usuário tem permissão (se necessário)
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            user = request.user
            if not user.is_staff and veiculo.usuario != user:
                raise serializers.ValidationError(
                    "Você não tem permissão para criar banner deste veículo."
                )

        # Verificar se já existe banner ativo
        from .models import BannerIdentificacao
        existing_banner = BannerIdentificacao.objects.filter(
            content_type=content_type,
            object_id=veiculo.id,
            ativo=True
        ).first()

        if existing_banner:
            raise serializers.ValidationError(
                "Veículo já possui banner ativo."
            )

        # Salvar instâncias para uso posterior
        self.veiculo_instance = veiculo
        self.content_type_instance = content_type
        return value
