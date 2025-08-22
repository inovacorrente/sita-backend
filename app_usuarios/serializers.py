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
    Serializador customizado para autenticação via JWT utilizando `matricula` no lugar de `username`.

    Este serializer:
    - Permite login usando o campo `matricula`.
    - Adiciona claims extras no token (`matricula` e `email`).
    """

    @classmethod
    def get_token(cls, user):
        """
        Gera o token JWT (access e refresh) para o usuário autenticado.

        Args:
            user (UsuarioCustom): Usuário autenticado.

        Returns:
            Token: Objeto JWT com claims personalizadas.
        """
        token = super().get_token(user)
        token['matricula'] = user.matricula
        token['email'] = user.email
        return token

    def validate(self, attrs):
        """
        Valida as credenciais de login, substituindo o campo `username`
        pelo valor de `matricula` antes da autenticação.
        """
        attrs['username'] = attrs.get('matricula')
        return super().validate(attrs)


# ============================================================================
# SERIALIZERS PARA CRUD DE USUÁRIOS
# ============================================================================

class UsuarioCustomViewSerializer(serializers.ModelSerializer):
    """
    Serializador de exibição de dados de usuários.
    Inclui informações gerais, status e grupos atribuídos.
    """

    groups = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Group.objects.all(),
        required=False,
        help_text="Lista de IDs dos grupos aos quais o usuário pertence."
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
            'email': {'validators': [validar_email], 'help_text': "E-mail válido e único no sistema."},
            'cpf': {'validators': [validar_cpf], 'help_text': "CPF válido, apenas números."},
            'telefone': {'validators': [validar_telefone], 'help_text': "Número de telefone com DDD."}
        }


class UsuarioCustomCreateSerializer(serializers.ModelSerializer):
    """
    Serializador para criação e edição de usuários.

    Realiza:
    - Validações de CPF, e-mail, telefone e data de nascimento.
    - Validação de força de senha e confirmação.
    - Controle de permissões administrativas na criação.
    """
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        required=False,
        help_text="Senha (opcional). Se não fornecida, será definida como a matrícula."
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=False,
        help_text="Confirmação da senha (opcional)."
    )
    cpf = serializers.CharField(
        required=True,
        help_text="CPF válido (apenas números)."
    )
    data_nascimento = serializers.DateField(
        required=True,
        help_text="Data de nascimento no formato YYYY-MM-DD."
    )
    sexo = serializers.ChoiceField(
        choices=[('M', 'Masculino'), ('F', 'Feminino'), ('O', 'Outro')],
        required=True,
        help_text="Sexo do usuário: Masculino (M), Feminino (F) ou Outro (O)."
    )
    telefone = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Telefone com DDD (opcional)."
    )
    groups = serializers.PrimaryKeyRelatedField(
        queryset=Group.objects.all(),
        many=True,
        required=False,
        help_text="Lista de IDs dos grupos aos quais o usuário será adicionado."
    )
    is_staff = serializers.BooleanField(
        required=False,
        default=False,
        help_text="Permite acesso ao Django Admin."
    )
    is_superuser = serializers.BooleanField(
        required=False,
        default=False,
        help_text="Concede todas as permissões no sistema."
    )

    class Meta:
        model = UsuarioCustom
        fields = [
            'matricula', 'nome_completo', 'email', 'cpf', 'telefone', 'password',
            'password_confirm', 'data_nascimento', 'sexo', 'groups',
            'is_staff', 'is_superuser',
        ]
        extra_kwargs = {
            'nome_completo': {'help_text': 'Nome completo do usuário.'},
            'email': {'help_text': 'E-mail válido e único no sistema.'}
        }

    # ----------------------------
    # Validações de campos
    # ----------------------------
    def validate_cpf(self, value):
        """Valida formato, algoritmo e unicidade do CPF."""
        validated_cpf = validate_cpf(value)
        if self.instance:
            if UsuarioCustom.objects.filter(cpf=validated_cpf).exclude(pk=self.instance.pk).exists():
                raise serializers.ValidationError(
                    "Este CPF já está sendo usado por outro usuário.")
        else:
            if UsuarioCustom.objects.filter(cpf=validated_cpf).exists():
                raise serializers.ValidationError(
                    "Este CPF já está cadastrado no sistema.")
        return validated_cpf

    def validate_email(self, value):
        """Valida formato e unicidade do e-mail."""
        return validate_email_unique(value, self.instance)

    def validate_telefone(self, value):
        """Valida formato do telefone."""
        return validate_telefone_format(value)

    def validate_data_nascimento(self, value):
        """Valida se a data de nascimento está dentro do intervalo permitido."""
        return validate_data_nascimento_range(value)

    def validate_password(self, value):
        """Valida se a senha atende aos critérios de segurança."""
        return validate_password_strength(value)

    def validate(self, attrs):
        """Validações cruzadas e definição de senha padrão."""
        password = attrs.get('password')
        password_confirm = attrs.pop('password_confirm', None)

        if not self.instance:
            attrs = set_default_password_as_matricula(attrs)

        validate_password_confirmation(password, password_confirm)
        request = self.context.get('request')
        attrs = validate_admin_privileges(attrs, request)
        return attrs

    # ----------------------------
    # Criação e atualização
    # ----------------------------
    def create(self, validated_data):
        """Cria um novo usuário com os dados validados."""
        groups = validated_data.pop('groups', [])
        password = validated_data.pop('password', None)
        is_staff = validated_data.pop('is_staff', False)
        is_superuser = validated_data.pop('is_superuser', False)

        try:
            user = UsuarioCustom.objects.create_user(
                **validated_data,
                password=password,
                is_staff=is_staff,
                is_superuser=is_superuser
            )
            if groups:
                user.groups.set(groups)
            return user
        except Exception as e:
            raise serializers.ValidationError(
                f"Erro ao criar usuário: {str(e)}")

    def update(self, instance, validated_data):
        """Atualiza os dados de um usuário existente."""
        groups = validated_data.pop('groups', None)
        password = validated_data.pop('password', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)

        instance.save()

        if groups is not None:
            instance.groups.set(groups)

        return instance


# ============================================================================
# SERIALIZERS PARA FUNCIONALIDADES ESPECÍFICAS
# ============================================================================

class UsuarioMeSerializer(serializers.ModelSerializer):
    """
    Serializador para que o próprio usuário visualize e edite suas informações.
    Não permite alterar matrícula ou CPF.
    """

    class Meta:
        model = UsuarioCustom
        fields = [
            'nome_completo', 'email', 'matricula', 'cpf',
            'telefone', 'data_nascimento', 'sexo'
        ]
        read_only_fields = ['matricula', 'cpf']
        extra_kwargs = {
            'email': {'validators': [validar_email], 'help_text': "E-mail válido."},
            'telefone': {'validators': [validar_telefone], 'help_text': "Telefone com DDD."}
        }


class UsuarioAtivarDesativarSerializer(serializers.Serializer):
    """
    Serializador para ativar ou desativar um usuário.
    Este endpoint faz um toggle automatico do status is_active.
    """
    # Não precisamos de campos obrigatórios pois a matrícula vem da URL
    # e o is_active é alternado automaticamente
    pass


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
