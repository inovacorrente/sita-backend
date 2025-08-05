import logging

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, permissions, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from utils.app_usuarios.exceptions import ValidationErrorResponse
from utils.commons.exceptions import SuccessResponse
from utils.commons.validators import format_error_response
from utils.permissions.base import (IsAdminToCreateAdmin,
                                    IsSelfOrHasModelPermission)

from .models import UsuarioCustom
from .serializers import (CustomTokenObtainPairSerializer,
                          UsuarioAtivarDesativarSerializer,
                          UsuarioCustomCreateSerializer,
                          UsuarioCustomViewSerializer, UsuarioMeSerializer)

logger = logging.getLogger(__name__)


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
    Suporta busca por matrícula, nome, email e CPF.
    """
    queryset = UsuarioCustom.objects.all()
    serializer_class = UsuarioCustomViewSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['matricula', 'nome_completo', 'email', 'cpf']
    filterset_fields = ['is_active', 'is_staff', 'is_superuser']


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
        try:
            serializer = UsuarioMeSerializer(
                request.user,
                data=request.data,
                partial=True
            )
            if serializer.is_valid():
                serializer.save()
                logger.info(
                    f"Usuário {request.user.matricula} atualizou seus dados"
                )
                success_data = SuccessResponse.updated(
                    serializer.data,
                    "Dados atualizados com sucesso."
                )
                return Response(success_data, status=status.HTTP_200_OK)

            # Log dos erros de validação para debugging
            logger.warning(
                f"Erro de validação para usuário {request.user.matricula}: "
                f"{serializer.errors}"
            )

            # Usar o formatador padrão de erros de validação
            error_response = format_error_response(serializer.errors, 400)
            return Response(error_response, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error(
                f"Erro inesperado ao atualizar dados do usuário "
                f"{request.user.matricula}: {str(e)}"
            )
            # Usar o formatador padrão para erro interno do servidor
            error_response = format_error_response(
                "Ocorreu um erro inesperado. Tente novamente.", 500
            )
            return Response(
                error_response,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

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

    def patch(self, request, matricula, *args, **kwargs):
        """
        Ativa ou desativa um usuário.
        """
        data = request.data.copy()
        data['matricula'] = matricula
        serializer = UsuarioAtivarDesativarSerializer(data=data)
        serializer.is_valid(raise_exception=True)

        # Se admin, pode alterar qualquer usuário pela matrícula da URL
        if request.user.is_staff or request.user.is_superuser:
            if not matricula:
                error_response = ValidationErrorResponse.required_field(
                    'matricula'
                )
                return Response(
                    error_response,
                    status=status.HTTP_400_BAD_REQUEST
                )
            try:
                user = UsuarioCustom.objects.get(matricula=matricula)
            except UsuarioCustom.DoesNotExist:
                error_response = ValidationErrorResponse.user_not_found()
                return Response(
                    error_response,
                    status=status.HTTP_404_NOT_FOUND
                )
        else:
            # Usuário comum só pode alterar a si mesmo
            user = request.user
            if matricula != user.matricula:
                error_response = ValidationErrorResponse.permission_denied()
                return Response(
                    error_response,
                    status=status.HTTP_403_FORBIDDEN
                )

        user.is_active = serializer.validated_data['is_active']
        user.save()
        status_msg = (
            f'Usuário {"ativado" if user.is_active else "desativado"} '
            f'com sucesso.'
        )
        success_response = SuccessResponse.updated(
            {
                'matricula': user.matricula,
                'is_active': user.is_active
            },
            status_msg
        )
        return Response(success_response, status=status.HTTP_200_OK)
