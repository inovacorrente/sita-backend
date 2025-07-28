from django.contrib.auth.models import Group
from rest_framework import permissions, serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import UsuarioCustom
from .utils import validar_cpf, validar_email, validar_telefone


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Serializador customizado para o token JWT (access e refresh) usando o campo `matricula` no lugar do `username`.

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
        # Adicione claims extras se quiser
        # Inclui a matrícula no payload do token
        token['matricula'] = user.matricula
        # Inclui o email no payload do token
        token['email'] = user.email
        return token

    def validate(self, attrs):
        """
        Valida os dados de entrada (credenciais) para autenticação JWT.

        Substitui o campo `username` por `matricula` para compatibilidade com o SimpleJWT,
        que espera o campo `username` por padrão.

        Args:
            attrs (dict): Dados fornecidos na requisição (ex: matricula e password).

        Returns:
            dict: Dados de autenticação válidos, incluindo access e refresh tokens.
        """
        # Substitui username por matrícula
        attrs['username'] = attrs.get('matricula')
        return super().validate(attrs)


class UsuarioCustomCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    cpf = serializers.CharField(required=True)
    data_nascimento = serializers.DateField(required=True)
    sexo = serializers.ChoiceField(
        choices=[('M', 'Masculino'), ('F', 'Feminino'), ('O', 'Outro')],
        required=True
    )
    telefone = serializers.CharField(required=False, allow_blank=True)
    groups = serializers.PrimaryKeyRelatedField(
        queryset=Group.objects.all(), many=True, required=False
    )

    is_staff = serializers.BooleanField(required=False, default=False)
    is_superuser = serializers.BooleanField(required=False, default=False)

    class Meta:
        model = UsuarioCustom
        fields = [
            'nome_completo',
            'email',
            'cpf',
            'telefone',
            'password',
            'data_nascimento',
            'sexo',
            'groups',
            'is_staff',
            'is_superuser',
        ]

    def validate_cpf(self, value):
        """Valida formato e algoritmo do CPF usando validator-collection"""
        return validar_cpf(value)

    def validate_email(self, value):
        """Valida formato do email usando validator-collection"""
        return validar_email(value)

    def validate_telefone(self, value):
        """Valida formato do telefone usando validator-collection"""
        return validar_telefone(value)

    def create(self, validated_data):
        groups = validated_data.pop('groups', [])
        password = validated_data.pop('password')
        is_staff = validated_data.pop('is_staff', False)
        is_superuser = validated_data.pop('is_superuser', False)

        # Cria o usuário
        user = UsuarioCustom.objects.create_user(
            **validated_data,
            password=password,
            is_staff=is_staff,
            is_superuser=is_superuser
        )

        # Adiciona os grupos se fornecidos
        if groups:
            user.groups.set(groups)

        return user


class IsAdminToCreateAdmin(permissions.BasePermission):
    """
    Só permite criar usuários administradores
    (is_staff=True ou is_superuser=True)
    se o usuário autenticado também for administrador.
    """

    def has_permission(self, request, view):
        if request.method == 'POST':
            is_staff = request.data.get('is_staff')
            is_superuser = request.data.get('is_superuser')
            grupos_restritos = {'ADMINISTRADOR', 'ATENDENTE ADMINISTRATIVO'}
            grupos = request.data.get('groups', [])
            # Se vier como string (ex: "1"), transforma em lista
            if isinstance(grupos, str):
                try:
                    import json
                    grupos = json.loads(grupos)
                except Exception:
                    grupos = [grupos]
            # Busca nomes dos grupos se IDs forem passados
            from django.contrib.auth.models import Group
            nomes_grupos = set()
            if grupos:
                try:
                    grupos_qs = Group.objects.filter(pk__in=grupos)
                    nomes_grupos = set(g.name.upper() for g in grupos_qs)
                except Exception:
                    pass
            """
            Bloqueia se tentar criar admin,
            superuser ou usuário em grupo restrito
            """
            if (
                str(is_staff).lower() == 'true'
                or str(is_superuser).lower() == 'true'
                or (nomes_grupos & grupos_restritos)
            ):
                return request.user and request.user.is_authenticated and request.user.is_staff  # noqa: E501
        return True


class UsuarioAtivarDesativarSerializer(serializers.Serializer):
    matricula = serializers.CharField(required=True, allow_blank=True)
    is_active = serializers.BooleanField(required=True)
