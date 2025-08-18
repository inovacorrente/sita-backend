from django.contrib.auth.models import Group
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from utils.app_usuarios.validators import (set_default_password_as_matricula,
                                           validar_cpf, validar_email,
                                           validar_telefone,
                                           validate_admin_privileges,
                                           validate_cpf,
                                           validate_data_nascimento_range,
                                           validate_email_unique,
                                           validate_password_confirmation,
                                           validate_password_strength,
                                           validate_telefone_format)

from .models import UsuarioCustom

# ============================================================================
# AUTENTICAÇÃO
# ============================================================================


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Serializador customizado para o token JWT usando `matricula` no lugar
    do `username`.

    Esta classe estende o TokenObtainPairSerializer do SimpleJWT para:
    - Adicionar claims personalizados ao token (como matrícula e email).
    - Permitir login com o campo `matricula` em vez do tradicional `username`.
    """

    @classmethod
    def get_token(cls, user):
        """
        Gera o token JWT (access e refresh) para o usuário autenticado.
        Adiciona informações personalizadas (claims extras) ao token.

        Args:
            user (UsuarioCustom): Usuário autenticado.

        Returns:
            Token: Objeto de token JWT com claims customizadas.
        """
        token = super().get_token(user)
        # Adiciona claims extras
        token['matricula'] = user.matricula
        token['email'] = user.email
        return token

    def validate(self, attrs):
        """
        Valida os dados de entrada (credenciais) para autenticação JWT.

        Substitui o campo `username` por `matricula` para compatibilidade
        com o SimpleJWT, que espera o campo `username` por padrão.

        Args:
            attrs (dict): Dados fornecidos na requisição
                         (ex: matricula e password).

        Returns:
            dict: Dados de autenticação válidos, incluindo access e
                  refresh tokens.
        """
        # Substitui username por matrícula
        attrs['username'] = attrs.get('matricula')
        return super().validate(attrs)


# ============================================================================
# SERIALIZERS PARA CRUD DE USUÁRIOS
# ============================================================================

class UsuarioCustomViewSerializer(serializers.ModelSerializer):
    """
    Serializador para exibir os dados do usuário customizado.
    Inclui campos adicionais como grupos e permissões.
    Usado para listagem e visualização de usuários.
    """

    groups = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Group.objects.all(), required=False
    )

    class Meta:
        model = UsuarioCustom
        fields = [
            'nome_completo', 'email', 'matricula', 'cpf',
            'telefone', 'data_nascimento', 'sexo', 'is_active',
            'is_staff', 'is_superuser', 'groups'
        ]
        read_only_fields = ['matricula']
        extra_kwargs = {
            'email': {'validators': [validar_email]},
            'cpf': {'validators': [validar_cpf]},
            'telefone': {'validators': [validar_telefone]}
        }


class UsuarioCustomCreateSerializer(serializers.ModelSerializer):
    """
    Serializador para criação e edição de usuários.
    Inclui validações robustas e controle de criação de usuários
    administrativos.
    """
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        required=False,  # Senha não obrigatória - será gerada automaticamente
        help_text="Senha (opcional - se não fornecida, será igual à matrícula)"
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=False,  # Confirmação também não é obrigatória
        help_text="Confirmação da senha (opcional)"
    )
    cpf = serializers.CharField(
        required=True,
        help_text="CPF válido (apenas números ou com formatação)"
    )
    data_nascimento = serializers.DateField(
        required=True,
        help_text="Data de nascimento no formato YYYY-MM-DD"
    )
    sexo = serializers.ChoiceField(
        choices=[('M', 'Masculino'), ('F', 'Feminino'), ('O', 'Outro')],
        required=True
    )
    telefone = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Telefone com DDD (opcional)"
    )
    groups = serializers.PrimaryKeyRelatedField(
        queryset=Group.objects.all(),
        many=True,
        required=False,
        help_text="IDs dos grupos para atribuir ao usuário"
    )
    is_staff = serializers.BooleanField(
        required=False,
        default=False,
        help_text="Permite acesso ao Django Admin"
    )
    is_superuser = serializers.BooleanField(
        required=False,
        default=False,
        help_text="Concede todas as permissões do sistema"
    )

    class Meta:
        model = UsuarioCustom
        fields = [
            'nome_completo', 'email', 'cpf', 'telefone', 'password',
            'password_confirm', 'data_nascimento', 'sexo', 'groups',
            'is_staff', 'is_superuser',
        ]
        extra_kwargs = {
            'nome_completo': {
                'help_text': 'Nome completo do usuário'
            },
            'email': {
                'help_text': 'E-mail válido e único no sistema'
            }
        }

    def validate_cpf(self, value):
        """Valida formato e algoritmo do CPF e unicidade"""
        # Primeiro valida formato
        validated_cpf = validate_cpf(value)

        # Depois verifica unicidade
        if self.instance:  # Edição
            if UsuarioCustom.objects.filter(
                cpf=validated_cpf
            ).exclude(pk=self.instance.pk).exists():
                raise serializers.ValidationError(
                    "Este CPF já está sendo usado por outro usuário."
                )
        else:  # Criação
            if UsuarioCustom.objects.filter(cpf=validated_cpf).exists():
                raise serializers.ValidationError(
                    "Este CPF já está cadastrado no sistema."
                )

        return validated_cpf

    def validate_email(self, value):
        """Valida formato do email e unicidade"""
        return validate_email_unique(value, self.instance)

    def validate_telefone(self, value):
        """Valida formato do telefone"""
        return validate_telefone_format(value)

    def validate_data_nascimento(self, value):
        """Valida se a data de nascimento é válida"""
        return validate_data_nascimento_range(value)

    def validate_password(self, value):
        """Valida senha básica (se fornecida)"""
        return validate_password_strength(value)

    def validate(self, attrs):
        """Validações gerais e cruzadas"""
        # Valida confirmação de senha
        password = attrs.get('password')
        password_confirm = attrs.pop('password_confirm', None)

        # Define senha padrão como matrícula se necessário
        attrs = set_default_password_as_matricula(attrs)

        # Valida confirmação de senha
        validate_password_confirmation(password, password_confirm)

        # Valida privilégios administrativos
        request = self.context.get('request')
        attrs = validate_admin_privileges(attrs, request)

        return attrs

    def create(self, validated_data):
        """
        Cria um novo usuário com os dados validados.
        Se não foi fornecida senha, usa a matrícula como senha padrão.
        """
        groups = validated_data.pop('groups', [])
        password = validated_data.pop('password', None)
        is_staff = validated_data.pop('is_staff', False)
        is_superuser = validated_data.pop('is_superuser', False)

        try:
            # Cria o usuário
            user = UsuarioCustom.objects.create_user(
                **validated_data,
                password=password,  # Já foi definida no validate()
                is_staff=is_staff,
                is_superuser=is_superuser
            )

            # Adiciona os grupos se fornecidos
            if groups:
                user.groups.set(groups)

            return user

        except Exception as e:
            raise serializers.ValidationError(
                f"Erro ao criar usuário: {str(e)}"
            )

    def update(self, instance, validated_data):
        """
        Atualiza um usuário existente.
        """
        groups = validated_data.pop('groups', None)
        password = validated_data.pop('password', None)

        # Atualiza campos básicos
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # Atualiza senha se fornecida
        if password:
            instance.set_password(password)

        instance.save()

        # Atualiza grupos se fornecidos
        if groups is not None:
            instance.groups.set(groups)

        return instance


# ============================================================================
# SERIALIZERS PARA FUNCIONALIDADES ESPECÍFICAS
# ============================================================================

class UsuarioMeSerializer(serializers.ModelSerializer):
    """
    Serializador para o usuário ver e editar suas próprias informações.
    Remove campos administrativos e protege campos críticos.
    """

    class Meta:
        model = UsuarioCustom
        fields = [
            'nome_completo', 'email', 'matricula', 'cpf',
            'telefone', 'data_nascimento', 'sexo'
        ]
        read_only_fields = ['matricula', 'cpf']  # Imutáveis
        extra_kwargs = {
            'email': {'validators': [validar_email]},
            'telefone': {'validators': [validar_telefone]}
        }


class UsuarioAtivarDesativarSerializer(serializers.Serializer):
    """
    Serializador para ativar/desativar usuários.
    """
    matricula = serializers.CharField(required=True, allow_blank=True)
    is_active = serializers.BooleanField(required=True)


class LogoutSerializer(serializers.Serializer):
    """
    Serializador para logout (invalidação de refresh token).
    """
    refresh = serializers.CharField(
        required=True,
        help_text="Refresh token a ser invalidado"
    )

    def validate_refresh(self, value):
        """
        Valida se o refresh token foi fornecido.
        """
        if not value:
            raise serializers.ValidationError(
                "Refresh token é obrigatório."
            )
        return value


class TokenRefreshResponseSerializer(serializers.Serializer):
    """
    Serializador para resposta do refresh token.
    """
    access_token = serializers.CharField(help_text="Novo access token")
    token_type = serializers.CharField(help_text="Tipo do token (Bearer)")
    expires_in = serializers.IntegerField(
        help_text="Tempo de expiração em segundos"
    )
