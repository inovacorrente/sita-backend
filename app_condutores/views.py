from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, status, viewsets
from rest_framework.exceptions import NotFound
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from utils.commons.exceptions import SuccessResponse

from .models import Condutor
from .serializers import (CondutorCreateSerializer, CondutorDetailSerializer,
                          CondutorListSerializer, CondutorUpdateSerializer)

# Create your views here.


class CondutorViewSet(mixins.CreateModelMixin,
                      mixins.RetrieveModelMixin,
                      mixins.UpdateModelMixin,
                      mixins.ListModelMixin,
                      viewsets.GenericViewSet):
    """
    ViewSet para operações CRUD de condutores (sem DELETE).
    Utiliza diferentes serializers baseado na ação.
    Usa matrícula do usuário como lookup field.

    Ações permitidas:
    - CREATE: Criar novo condutor
    - RETRIEVE: Buscar condutor específico por matrícula, nome ou CPF
    - UPDATE/PATCH: Atualizar dados do condutor por matrícula
    - LIST: Listar condutores
    """
    queryset = Condutor.objects.select_related('usuario').all()
    serializer_class = CondutorListSerializer  # Serializer padrão
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['categoria_cnh']
    search_fields = ['usuario__nome_completo', 'usuario__matricula']
    ordering_fields = ['data_criacao', 'data_atualizacao']
    ordering = ['-data_criacao']
    lookup_field = 'usuario__matricula'
    lookup_url_kwarg = 'matricula'

    def get_object(self):
        """
        Retorna o objeto condutor baseado em múltiplos critérios de busca.
        Permite buscar por matrícula, nome completo ou CPF do usuário.
        """
        lookup_value = self.kwargs.get(self.lookup_url_kwarg)

        if not lookup_value:
            raise NotFound("Parâmetro de busca não fornecido.")

        # Busca por matrícula, nome ou CPF
        queryset = self.get_queryset()

        try:
            # Tenta buscar por matrícula primeiro
            obj = queryset.get(usuario__matricula=lookup_value)
        except Condutor.DoesNotExist:
            try:
                # Se não encontrar por matrícula, busca por nome completo
                obj = queryset.get(
                    Q(usuario__nome_completo__icontains=lookup_value)
                )
            except Condutor.DoesNotExist:
                try:
                    # Se não encontrar por nome, busca por CPF
                    obj = queryset.get(usuario__cpf=lookup_value)
                except Condutor.DoesNotExist:
                    raise NotFound(
                        f"Condutor não encontrado com matrícula, nome ou CPF: "
                        f"{lookup_value}"
                    )

        # Verifica permissões
        self.check_object_permissions(self.request, obj)
        return obj

    def get_serializer_class(self):
        """
        Retorna a classe de serializer apropriada baseada na ação.
        """
        if self.action == 'create':
            return CondutorCreateSerializer
        elif self.action in ['retrieve']:
            return CondutorDetailSerializer
        elif self.action in ['update', 'partial_update']:
            return CondutorUpdateSerializer
        else:  # list e outras ações
            return CondutorListSerializer

    def create(self, request, *args, **kwargs):
        """
        Cria um novo condutor e retorna resposta de sucesso padronizada.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        condutor = serializer.save()

        # Serializa os dados para retorno
        response_serializer = CondutorDetailSerializer(condutor)
        success_data = SuccessResponse.created(
            response_serializer.data,
            "Condutor criado com sucesso."
        )
        return Response(success_data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, *args, **kwargs):
        """
        Recupera dados detalhados de um condutor específico.
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        success_data = SuccessResponse.retrieved(
            serializer.data,
            "Dados do condutor recuperados com sucesso."
        )
        return Response(success_data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        """
        Atualiza dados do condutor e retorna resposta de sucesso padronizada.
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=partial
        )
        serializer.is_valid(raise_exception=True)
        condutor = serializer.save()

        # Serializa os dados para retorno
        response_serializer = CondutorDetailSerializer(condutor)
        success_data = SuccessResponse.updated(
            response_serializer.data,
            "Dados do condutor atualizados com sucesso."
        )
        return Response(success_data, status=status.HTTP_200_OK)
