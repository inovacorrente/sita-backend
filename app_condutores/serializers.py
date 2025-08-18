from datetime import date

from django.contrib.auth.models import Group
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from app_usuarios.models import UsuarioCustom
from app_usuarios.serializers import UsuarioCustomViewSerializer
from utils.app_condutores.validators import (
    validar_categoria_cnh,
    validar_condutor_update,
    validar_consistencia_datas_cnh,
    validar_data_emissao_cnh,
    validar_data_validade_cnh,
    validar_matricula_usuario
)

from .models import Condutor


class CondutorCreateSerializer(serializers.ModelSerializer):
    """
    Serializador para **criação** de condutores.

    Este serializer:
    - Recebe a matrícula de um usuário já existente (OneToOneField).
    - Valida se o usuário pertence ao grupo **CONDUTOR**.
    - Cria o registro de condutor associado.

    Campos:
        - matricula (str, obrigatório): Matrícula do usuário já existente.
        - categoria_cnh (str, obrigatório): Categoria da CNH (A, B, C, D, E, AD).
        - data_validade_cnh (date, obrigatório): Data de validade da CNH.
        - data_emissao_cnh (date, obrigatório): Data de emissão da CNH.
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
        """
        Valida se a categoria da CNH é válida.
        """
        return validar_categoria_cnh(value)

    def validate_data_emissao_cnh(self, value):
        """
        Valida se a data de emissão da CNH não está no futuro.
        """
        return validar_data_emissao_cnh(value)

    def validate_data_validade_cnh(self, value):
        """
        Valida se a CNH não está vencida.
        """
        return validar_data_validade_cnh(value)

    def validate(self, attrs):
        """
        Validações cruzadas envolvendo emissão e validade.
        """
        validar_consistencia_datas_cnh(
            attrs.get('data_emissao_cnh'),
            attrs.get('data_validade_cnh')
        )
        return attrs

    def validate_matricula(self, value):
        """
        Valida se a matrícula pertence a um usuário existente
        que ainda não possui condutor associado.
        """
        return validar_matricula_usuario(value)

    def create(self, validated_data):
        """
        Cria o condutor vinculado ao usuário informado.

        Passos:
            1. Busca o usuário pela matrícula.
            2. Valida se ele pertence ao grupo CONDUTOR.
            3. Cria e retorna o condutor.

        Raises:
            serializers.ValidationError: Caso o grupo CONDUTOR não exista
            ou o usuário não pertença a ele.
        """
        matricula = validated_data.pop('matricula')
        usuario = UsuarioCustom.objects.get(matricula=matricula)

        # Verifica se o grupo CONDUTOR existe
        try:
            grupo_condutor = Group.objects.get(name='CONDUTOR')
        except Group.DoesNotExist:
            raise serializers.ValidationError(
                {"matricula": "Grupo CONDUTOR não existe no sistema."}
            )

        # Verifica se o usuário pertence ao grupo
        if not usuario.groups.filter(id=grupo_condutor.id).exists():
            raise serializers.ValidationError(
                {"matricula": "Usuário não pertence ao grupo CONDUTOR."}
            )

        return Condutor.objects.create(usuario=usuario, **validated_data)


class CondutorListSerializer(serializers.ModelSerializer):
    """
    Serializador para listagem de condutores.

    Inclui informações básicas do usuário associado (via UsuarioCustomViewSerializer).
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
    Serializador para visualização detalhada de um condutor.

    Além das informações do condutor e do usuário, adiciona:
        - cnh_vencida (bool): Se a CNH já está vencida.
        - dias_para_vencimento (int): Dias restantes para vencer.
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
        """
        Retorna True se a data de validade da CNH já passou.
        """
        return obj.data_validade_cnh < date.today()

    @extend_schema_field(serializers.IntegerField)
    def get_dias_para_vencimento(self, obj) -> int:
        """
        Retorna quantos dias faltam para a CNH vencer.
        """
        return (obj.data_validade_cnh - date.today()).days


class CondutorUpdateSerializer(serializers.ModelSerializer):
    """
    Serializador para atualização de dados do condutor.

    Permite atualizar apenas:
        - categoria_cnh
        - data_validade_cnh
        - data_emissao_cnh
    """
    categoria_cnh = serializers.CharField(max_length=4)
    data_validade_cnh = serializers.DateField()
    data_emissao_cnh = serializers.DateField()

    class Meta:
        model = Condutor
        fields = ['categoria_cnh', 'data_validade_cnh', 'data_emissao_cnh']

    def validate_categoria_cnh(self, value):
        """
        Valida se a categoria da CNH é válida.
        """
        return validar_categoria_cnh(value)

    def validate_data_emissao_cnh(self, value):
        """
        Valida se a data de emissão da CNH não está no futuro.
        """
        return validar_data_emissao_cnh(value)

    def validate_data_validade_cnh(self, value):
        """
        Valida se a CNH não está vencida.
        """
        return validar_data_validade_cnh(value)

    def validate(self, attrs):
        """
        Validações cruzadas e regras específicas para atualização de condutores.
        """
        return validar_condutor_update(self.instance, attrs)
