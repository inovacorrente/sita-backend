import logging
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, permissions, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
    OpenApiParameter,
    OpenApiExample,
    OpenApiResponse
)

from utils.app_usuarios.exceptions import ValidationErrorResponse
from utils.commons.exceptions import SuccessResponse
from utils.commons.validators import format_error_response
from utils.permissions.base import (
    DjangoModelPermissionsWithView,
    IsAdminToCreateAdmin,
    IsSelfOrHasModelPermission
)

from .models import UsuarioCustom
from .serializers import (
    CustomTokenObtainPairSerializer,
    UsuarioCustomCreateSerializer,
    UsuarioCustomViewSerializer,
    UsuarioMeSerializer
)

logger = logging.getLogger(__name__)

# ============================================================================
# AUTENTICAÇÃO
# ============================================================================

@extend_schema(
    tags=["Autenticação"],
    summary="Autenticar usuário via JWT",
    description=(
        "Autentica o usuário usando matrícula e senha. "
        "Retorna tokens de acesso e refresh em caso de sucesso."
    ),
    request=CustomTokenObtainPairSerializer,
    responses={
        200: OpenApiResponse(description="Autenticação bem-sucedida"),
        401: OpenApiResponse(description="Credenciais inválidas"),
    },
    examples=[
        OpenApiExample(
            "Exemplo de requisição",
            value={"matricula": "20230001", "password": "senha123"},
            request_only=True
        ),
        OpenApiExample(
            "Exemplo de resposta",
            value={
                "access": "jwt_token_aqui",
                "refresh": "jwt_refresh_token_aqui",
                "mensagem": "Login realizado com sucesso"
            },
            response_only=True
        ),
    ]
)
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            success_data = SuccessResponse.login_success(response.data)
            return Response(success_data, status=status.HTTP_200_OK)
        return response


# ============================================================================
# CRUD DE USUÁRIOS
# ============================================================================

@extend_schema_view(
    get=extend_schema(
        tags=["Usuários"],
        summary="Listar usuários",
        description="Lista todos os usuários cadastrados. Requer autenticação e permissão.",
        parameters=[
            OpenApiParameter("search", str, description="Busca por matrícula, nome, email ou CPF"),
            OpenApiParameter("is_active", bool, description="Filtrar por status ativo"),
            OpenApiParameter("is_staff", bool, description="Filtrar por admin staff"),
            OpenApiParameter("is_superuser", bool, description="Filtrar por superusuário"),
        ],
        responses={200: UsuarioCustomViewSerializer(many=True)}
    )
)
class UsuarioCustomListView(generics.ListAPIView):
    queryset = UsuarioCustom.objects.all()
    serializer_class = UsuarioCustomViewSerializer
    permission_classes = [permissions.IsAuthenticated, DjangoModelPermissionsWithView]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['matricula', 'nome_completo', 'email', 'cpf']
    filterset_fields = ['is_active', 'is_staff', 'is_superuser']


@extend_schema_view(
    post=extend_schema(
        tags=["Usuários"],
        summary="Criar novo usuário",
        description="Cria um novo usuário. Apenas administradores podem criar outros administradores.",
        request=UsuarioCustomCreateSerializer,
        responses={
            201: UsuarioCustomViewSerializer,
            400: OpenApiResponse(description="Erro de validação"),
        }
    )
)
class UsuarioCustomCreateView(generics.CreateAPIView):
    queryset = UsuarioCustom.objects.all()
    serializer_class = UsuarioCustomCreateSerializer
    permission_classes = [IsAdminToCreateAdmin]


@extend_schema_view(
    get=extend_schema(
        tags=["Usuários"],
        summary="Detalhar usuário",
        description="Retorna os detalhes de um usuário específico pela matrícula. "
                    "Usuário comum só pode acessar seus próprios dados.",
        responses={
            200: UsuarioCustomViewSerializer,
            403: OpenApiResponse(description="Sem permissão"),
            404: OpenApiResponse(description="Usuário não encontrado"),
        }
    )
)
class UsuarioCustomDetailView(generics.RetrieveAPIView):
    queryset = UsuarioCustom.objects.all()
    serializer_class = UsuarioCustomViewSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'matricula'

    def get_object(self):
        obj = super().get_object()
        if not self.request.user.is_staff and obj != self.request.user:
            raise PermissionDenied("Você não tem permissão para ver estes dados.")
        return obj


@extend_schema_view(
    put=extend_schema(
        tags=["Usuários"],
        summary="Atualizar usuário",
        description="Atualiza os dados de um usuário pela matrícula.",
        request=UsuarioCustomCreateSerializer,
        responses={200: UsuarioCustomViewSerializer}
    ),
    patch=extend_schema(
        tags=["Usuários"],
        summary="Atualização parcial de usuário",
        description="Atualiza parcialmente os dados de um usuário pela matrícula.",
        request=UsuarioCustomCreateSerializer,
        responses={200: UsuarioCustomViewSerializer}
    )
)
class UsuarioCustomUpdateView(generics.UpdateAPIView):
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

@extend_schema(tags=["Usuários"], methods=["GET", "PUT", "PATCH"])
class UsuarioMeView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UsuarioMeSerializer

    @extend_schema(
        summary="Obter meus dados",
        description="Retorna os dados do usuário autenticado.",
        responses={200: UsuarioMeSerializer}
    )
    def get(self, request):
        serializer = UsuarioMeSerializer(request.user)
        success_data = SuccessResponse.retrieved(
            serializer.data,
            "Dados do usuário recuperados com sucesso."
        )
        return Response(success_data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Atualizar meus dados",
        description="Atualiza os dados do usuário autenticado.",
        request=UsuarioMeSerializer,
        responses={200: UsuarioMeSerializer, 400: OpenApiResponse(description="Erro de validação")}
    )
    def put(self, request):
        try:
            serializer = UsuarioMeSerializer(request.user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                logger.info(f"Usuário {request.user.matricula} atualizou seus dados")
                success_data = SuccessResponse.updated(serializer.data, "Dados atualizados com sucesso.")
                return Response(success_data, status=status.HTTP_200_OK)

            logger.warning(f"Erro de validação para usuário {request.user.matricula}: {serializer.errors}")
            error_response = format_error_response(serializer.errors, 400)
            return Response(error_response, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error(f"Erro inesperado ao atualizar dados do usuário {request.user.matricula}: {str(e)}")
            error_response = format_error_response("Ocorreu um erro inesperado. Tente novamente.", 500)
            return Response(error_response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(
        summary="Atualização parcial dos meus dados",
        description="Atualiza parcialmente os dados do usuário autenticado.",
        request=UsuarioMeSerializer,
        responses={200: UsuarioMeSerializer}
    )
    def patch(self, request):
        return self.put(request)


@extend_schema(
    tags=["Usuários"],
    summary="Ativar/Desativar usuário",
    description="Alterna o status de ativo (`is_active`) de um usuário. "
                "Admins podem alterar qualquer usuário, usuários comuns apenas a si mesmos.",
    parameters=[OpenApiParameter("matricula", str, OpenApiParameter.PATH, description="Matrícula do usuário")],
    responses={
        200: OpenApiResponse(description="Status alterado com sucesso"),
        403: OpenApiResponse(description="Sem permissão"),
        404: OpenApiResponse(description="Usuário não encontrado")
    }
)
class UsuarioAtivarDesativarView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, matricula, *args, **kwargs):
        if not matricula:
            error_response = ValidationErrorResponse.required_field('matricula')
            return Response(error_response, status=status.HTTP_400_BAD_REQUEST)

        if request.user.is_staff or request.user.is_superuser:
            try:
                user = UsuarioCustom.objects.get(matricula=matricula)
            except UsuarioCustom.DoesNotExist:
                error_response = ValidationErrorResponse.user_not_found()
                return Response(error_response, status=status.HTTP_404_NOT_FOUND)
        else:
            user = request.user
            if matricula != user.matricula:
                error_response = ValidationErrorResponse.permission_denied()
                return Response(error_response, status=status.HTTP_403_FORBIDDEN)

        user.is_active = not user.is_active
        user.save()

        logger.info(
            f"Usuário {user.matricula} foi {'ativado' if user.is_active else 'desativado'} "
            f"por {request.user.matricula}"
        )

        status_msg = f'Usuário {"ativado" if user.is_active else "desativado"} com sucesso.'
        success_response = SuccessResponse.updated(
            {'matricula': user.matricula, 'is_active': user.is_active},
            status_msg
        )
        return Response(success_response, status=status.HTTP_200_OK)
