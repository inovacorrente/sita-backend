"""
Serializers para o app de veículos do sistema SITA.
Inclui serializers para todos os tipos de veículos (Táxi, Mototáxi,
Transporte Municipal).
"""
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
        help_text="Matrícula do usuário proprietário do veículo"
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
        """Valida se o usuário existe e está ativo."""
        return validate_usuario_exists(value)

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
        matricula_usuario = validated_data.pop('matricula_usuario')
        usuario = UsuarioCustom.objects.get(matricula=matricula_usuario)
        validated_data['usuario'] = usuario
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """Atualiza um veículo existente."""
        matricula_usuario = validated_data.pop('matricula_usuario', None)
        if matricula_usuario:
            usuario = UsuarioCustom.objects.get(matricula=matricula_usuario)
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
