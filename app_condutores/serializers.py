from datetime import date

from django.contrib.auth.models import Group
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from app_usuarios.models import UsuarioCustom
from app_usuarios.serializers import UsuarioCustomViewSerializer
from utils.app_condutores.validators import (validar_categoria_cnh,
                                             validar_condutor_update,
                                             validar_consistencia_datas_cnh,
                                             validar_data_emissao_cnh,
                                             validar_data_validade_cnh,
                                             validar_matricula_usuario)

from .models import Condutor


class CondutorCreateSerializer(serializers.ModelSerializer):
    """
    Serializer para criação de condutores.
    Utiliza matrícula do usuário existente via OneToOneField.
    """
    matricula = serializers.CharField(max_length=50, write_only=True)

    class Meta:
        model = Condutor
        fields = [
            'matricula', 'categoria_cnh', 'data_validade_cnh',
            'data_emissao_cnh'
        ]
        extra_kwargs = {
            'categoria_cnh': {
                'help_text': 'Categoria da CNH: A, B, C, D, E, AD'
            },
        }

    def validate_categoria_cnh(self, value):
        """Valida se a categoria da CNH é válida."""
        return validar_categoria_cnh(value)

    def validate_data_emissao_cnh(self, value):
        """Valida se a data de emissão da CNH não é futura."""
        return validar_data_emissao_cnh(value)

    def validate_data_validade_cnh(self, value):
        """Valida se a CNH não está vencida."""
        return validar_data_validade_cnh(value)

    def validate(self, attrs):
        """Validações que envolvem múltiplos campos."""
        data_emissao = attrs.get('data_emissao_cnh')
        data_validade = attrs.get('data_validade_cnh')
        validar_consistencia_datas_cnh(data_emissao, data_validade)
        return attrs

    def validate_matricula(self, value):
        """Valida se o usuário existe e não é já um condutor."""
        return validar_matricula_usuario(value)

    def create(self, validated_data):
        """Cria o condutor associado ao usuário existente."""
        matricula = validated_data.pop('matricula')
        usuario = UsuarioCustom.objects.get(matricula=matricula)

        # Só permite criar condutor se o usuário já estiver no grupo CONDUTOR
        try:
            grupo_condutor = Group.objects.get(name='CONDUTOR')
        except Group.DoesNotExist:
            raise serializers.ValidationError(
                {"matricula": "Grupo CONDUTOR não existe no sistema."})

        if not usuario.groups.filter(id=grupo_condutor.id).exists():
            raise serializers.ValidationError(
                {"matricula": "Usuário não pertence ao grupo CONDUTOR."})

        # Cria o condutor
        condutor = Condutor.objects.create(usuario=usuario, **validated_data)
        return condutor


class CondutorListSerializer(serializers.ModelSerializer):
    """
    Serializer para listagem de condutores.
    Inclui informações básicas do usuário associado.
    """
    usuario = UsuarioCustomViewSerializer(read_only=True)

    class Meta:
        model = Condutor
        fields = [
            'usuario', 'categoria_cnh', 'data_validade_cnh',
            'data_emissao_cnh', 'data_criacao'
        ]


class CondutorDetailSerializer(serializers.ModelSerializer):
    """
    Serializer para detalhes completos de um condutor.
    Inclui todas as informações do usuário e condutor.
    """
    usuario = UsuarioCustomViewSerializer(read_only=True)
    cnh_vencida = serializers.SerializerMethodField()
    dias_para_vencimento = serializers.SerializerMethodField()

    class Meta:
        model = Condutor
        fields = [
            'usuario', 'categoria_cnh', 'data_validade_cnh',
            'data_emissao_cnh', 'cnh_vencida', 'dias_para_vencimento',
            'data_criacao', 'data_atualizacao'
        ]

    @extend_schema_field(serializers.BooleanField)
    def get_cnh_vencida(self, obj) -> bool:
        """Retorna se a CNH está vencida."""
        return obj.data_validade_cnh < date.today()

    @extend_schema_field(serializers.IntegerField)
    def get_dias_para_vencimento(self, obj) -> int:
        """Retorna quantos dias faltam para a CNH vencer."""
        diferenca = obj.data_validade_cnh - date.today()
        return diferenca.days


class CondutorUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer para atualização de dados do condutor.
    Permite atualizar apenas dados específicos do condutor, não do usuário.
    """
    categoria_cnh = serializers.CharField(max_length=4)
    data_validade_cnh = serializers.DateField()
    data_emissao_cnh = serializers.DateField()

    class Meta:
        model = Condutor
        fields = ['categoria_cnh', 'data_validade_cnh', 'data_emissao_cnh']

    def validate_categoria_cnh(self, value):
        """Valida se a categoria da CNH é válida."""
        return validar_categoria_cnh(value)

    def validate_data_emissao_cnh(self, value):
        """Valida se a data de emissão da CNH não é futura."""
        return validar_data_emissao_cnh(value)

    def validate_data_validade_cnh(self, value):
        """Valida se a CNH não está vencida."""
        return validar_data_validade_cnh(value)

    def validate(self, attrs):
        """Validações que envolvem múltiplos campos."""
        return validar_condutor_update(self.instance, attrs)
