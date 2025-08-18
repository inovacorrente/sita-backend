
import logging
import os

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, permissions, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import (TokenObtainPairView,
                                            TokenRefreshView)

from utils.app_usuarios.exceptions import ValidationErrorResponse
from utils.commons.exceptions import SuccessResponse
from utils.commons.validators import format_error_response
from utils.permissions.base import (DjangoModelPermissionsWithView,
                                    IsAdminToCreateAdmin,
                                    IsSelfOrHasModelPermission)

from .models import UsuarioCustom
from .serializers import (CustomTokenObtainPairSerializer, LogoutSerializer,
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


class CustomTokenRefreshView(TokenRefreshView):
    """
    View para renovar token JWT.
    """

    def post(self, request, *args, **kwargs):
        """
        Sobrescreve o método post para retornar resposta padronizada
        """
        try:
            response = super().post(request, *args, **kwargs)

            if response.status_code == 200:
                success_data = SuccessResponse.retrieved(
                    {
                        'access_token': response.data.get('access'),
                        'token_type': 'Bearer',
                        'expires_in': int(os.environ.get(
                            'ACCESS_TOKEN_EXPIRES_IN', 3600
                        ))
                    },
                    "Token renovado com sucesso."
                )
                return Response(success_data, status=status.HTTP_200_OK)

            return response

        except TokenError as e:
            logger.warning(f"Erro ao renovar token: {str(e)}")
            error_response = format_error_response(
                "Token de refresh inválido ou expirado.", 401
            )
            return Response(
                error_response,
                status=status.HTTP_401_UNAUTHORIZED
            )


class LogoutView(GenericAPIView):
    """
    View para logout (invalidar refresh token).
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = LogoutSerializer

    def post(self, request):
        """
        Invalida o refresh token para fazer logout.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            refresh_token = serializer.validated_data['refresh']

            token = RefreshToken(refresh_token)
            token.blacklist()

            logger.info(
                f"Usuário {request.user.matricula} fez logout"
            )

            success_data = SuccessResponse.deleted(
                "Logout realizado com sucesso."
            )
            return Response(success_data, status=status.HTTP_200_OK)

        except TokenError as e:
            logger.warning(
                f"Erro ao fazer logout para usuário "
                f"{request.user.matricula}: {str(e)}"
            )
            error_response = format_error_response(
                "Token inválido.", 400
            )
            return Response(
                error_response,
                status=status.HTTP_400_BAD_REQUEST
            )


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
    permission_classes = [permissions.IsAuthenticated,
                          DjangoModelPermissionsWithView]
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
    permission_classes = [IsAdminToCreateAdmin, DjangoModelPermissionsWithView]


class UsuarioCustomDetailView(generics.RetrieveAPIView):
    """
    View para exibir detalhes de um usuário específico.
    - Admins podem ver qualquer usuário
    - Usuários comuns só podem ver seus próprios dados
    """
    queryset = UsuarioCustom.objects.all()
    serializer_class = UsuarioCustomViewSerializer
    permission_classes = [permissions.IsAuthenticated,
                          DjangoModelPermissionsWithView]
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
    serializer_class = UsuarioMeSerializer  # Para documentação API

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


class UsuarioAtivarDesativarView(GenericAPIView):
    """
    View para ativar/desativar usuários.
    - Admins podem ativar/desativar qualquer usuário
    - Usuários comuns só podem alterar seu próprio status
    - Alterna automaticamente o status is_active (toggle)
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UsuarioAtivarDesativarSerializer

    def patch(self, request, matricula, *args, **kwargs):
        data = {"matricula": matricula}
        data.update(request.data)
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        """
        Alterna o status is_active do usuário
        (ativa se inativo, desativa se ativo).
        """
        # Validar se matrícula foi fornecida
        if not matricula:
            error_response = ValidationErrorResponse.required_field(
                'matricula'
            )
            return Response(
                error_response,
                status=status.HTTP_400_BAD_REQUEST
            )

        # Se admin, pode alterar qualquer usuário pela matrícula da URL
        if request.user.is_staff or request.user.is_superuser:
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

        # Alternar o status is_active (toggle)
        user.is_active = not user.is_active
        user.save()

        # Log da operação
        logger.info(
            f"Usuário {user.matricula} foi "
            f"{'ativado' if user.is_active else 'desativado'} "
            f"por {request.user.matricula}"
        )

        status_msg = (
            f'Usuário {"ativado" if user.is_active else "desativado"} '
            f'com sucesso.'
        )
        success_response = SuccessResponse.updated(
            {
                'matricula': user.matricula,
                'is_active': user.is_active,
            },
            status_msg
        )
        return Response(success_response, status=status.HTTP_200_OK)
