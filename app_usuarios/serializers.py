from django.contrib.auth.models import Group
from rest_framework import permissions, serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import UsuarioCustom


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Adicione claims extras se quiser
        token['matricula'] = user.matricula
        token['email'] = user.email
        return token

    def validate(self, attrs):
        # Substitui username por matrícula
        attrs['username'] = attrs.get('matricula')
        return super().validate(attrs)


class UsuarioCustomCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    cpf = serializers.CharField(required=True)
    data_nascimento = serializers.DateField(required=True)
    sexo = serializers.CharField(required=True)
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

    def create(self, validated_data):
        groups = validated_data.pop(
            'groups', []) if 'groups' in validated_data else []
        password = validated_data.pop('password')
        is_staff = validated_data.pop('is_staff', False)
        is_superuser = validated_data.pop('is_superuser', False)
        # Cria o usuário sem grupos
        user = UsuarioCustom.objects.create_user(
            **validated_data,
            password=password,
            is_staff=is_staff,
            is_superuser=is_superuser
        )
        # Só depois adiciona os grupos
        if groups:
            user.groups.set(groups)
            user.save()
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
    is_active = serializers.BooleanField(required=True)
