from rest_framework import generics, permissions, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from .exceptions import SuccessResponse
from .models import UsuarioCustom
from .serializers import (CustomTokenObtainPairSerializer,
                          IsAdminToCreateAdmin,
                          UsuarioAtivarDesativarSerializer,
                          UsuarioCustomCreateSerializer,
                          UsuarioCustomViewSerializer, UsuarioMeSerializer)

# ============================================================================
# PERMISSIONS CUSTOMIZADAS
# ============================================================================


class IsSelfOrHasModelPermission(permissions.BasePermission):
    """
    Permissão que permite acesso se o usuário é o próprio objeto
    ou tem permissões de modelo Django.
    """

    def has_object_permission(self, request, view, obj):
        return obj == request.user


# ============================================================================
# AUTENTICAÇÃO
# ============================================================================

class CustomTokenObtainPairView(TokenObtainPairView):
    """
    View para autenticação JWT usando matrícula ao invés de username.
    """
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        """
        Sobrescreve o método post para retornar resposta padronizada
        """
        response = super().post(request, *args, **kwargs)

        if response.status_code == 200:
            # Sucesso na autenticação
            success_data = SuccessResponse.login_success(response.data)
            return Response(success_data, status=status.HTTP_200_OK)

        # Em caso de erro, o manipulador de exceções já trata
        return response


# ============================================================================
# CRUD DE USUÁRIOS
# ============================================================================

class UsuarioCustomListView(generics.ListAPIView):
    """
    View para listar todos os usuários.
    Requer autenticação.
    """
    queryset = UsuarioCustom.objects.all()
    serializer_class = UsuarioCustomViewSerializer
    permission_classes = [permissions.IsAuthenticated]


class UsuarioCustomCreateView(generics.CreateAPIView):
    """
    View para criar novos usuários.
    Apenas admins podem criar outros admins.
    """
    queryset = UsuarioCustom.objects.all()
    serializer_class = UsuarioCustomCreateSerializer
    permission_classes = [IsAdminToCreateAdmin]


class UsuarioCustomDetailView(generics.RetrieveAPIView):
    """
    View para exibir detalhes de um usuário específico.
    - Admins podem ver qualquer usuário
    - Usuários comuns só podem ver seus próprios dados
    """
    queryset = UsuarioCustom.objects.all()
    serializer_class = UsuarioCustomViewSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'matricula'

    def get_object(self):
        """
        Retorna o objeto usuário, aplicando regras de permissão.
        """
        obj = super().get_object()

        # Se não for admin, só pode ver os próprios dados
        if not self.request.user.is_staff and obj != self.request.user:
            raise PermissionDenied(
                "Você não tem permissão para ver estes dados."
            )

        return obj


class UsuarioCustomUpdateView(generics.UpdateAPIView):
    """
    View para atualizar dados de usuários.
    - Admins podem editar qualquer usuário
    - Usuários comuns só podem editar seus próprios dados
    """
    queryset = UsuarioCustom.objects.all()
    serializer_class = UsuarioCustomCreateSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        permissions.DjangoModelPermissions | IsSelfOrHasModelPermission
    ]
    lookup_field = 'matricula'


# ============================================================================
# FUNCIONALIDADES ESPECÍFICAS
# ============================================================================

class UsuarioMeView(APIView):
    """
    View para o usuário autenticado gerenciar suas próprias informações.
    - GET: Ver próprios dados
    - PUT/PATCH: Atualizar próprios dados (campos limitados)
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """
        Retorna os dados do usuário autenticado.
        """
        serializer = UsuarioMeSerializer(request.user)
        success_data = SuccessResponse.retrieved(
            serializer.data,
            "Dados do usuário recuperados com sucesso."
        )
        return Response(success_data, status=status.HTTP_200_OK)

    def put(self, request):
        """
        Permite ao usuário atualizar seus próprios dados.
        """
        serializer = UsuarioMeSerializer(
            request.user,
            data=request.data,
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            success_data = SuccessResponse.updated(
                serializer.data,
                "Dados atualizados com sucesso."
            )
            return Response(success_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        """
        Permite ao usuário atualizar parcialmente seus próprios dados.
        """
        return self.put(request)


class UsuarioAtivarDesativarView(APIView):
    """
    View para ativar/desativar usuários.
    - Admins podem ativar/desativar qualquer usuário
    - Usuários comuns só podem alterar seu próprio status
    """
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request):
        """
        Ativa ou desativa um usuário.
        """
        serializer = UsuarioAtivarDesativarSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        matricula = request.data.get('matricula')

        # Se admin, pode passar a matrícula de qualquer usuário
        if request.user.is_staff or request.user.is_superuser:
            if not matricula:
                return Response(
                    {'detail': 'matricula é obrigatória para admin.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            try:
                user = UsuarioCustom.objects.get(matricula=matricula)
            except UsuarioCustom.DoesNotExist:
                return Response(
                    {'detail': 'Usuário não encontrado.'},
                    status=status.HTTP_404_NOT_FOUND
                )
        else:
            # Usuário comum só pode alterar a si mesmo
            user = request.user
            if matricula and matricula != user.matricula:
                return Response(
                    {'detail': 'Você só pode alterar seu próprio status.'},
                    status=status.HTTP_403_FORBIDDEN
                )

        user.is_active = serializer.validated_data['is_active']
        user.save()
        status_msg = (
            f'Usuário {"ativado" if user.is_active else "desativado"} '
            f'com sucesso.'
        )
        return Response({'detail': status_msg}, status=status.HTTP_200_OK)
