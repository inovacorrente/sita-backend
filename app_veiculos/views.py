"""
Views para o app de veículos do sistema SITA.
Inclui ViewSets para todos os tipos de veículos com permissões do Django.
"""
import logging

from django.db.models import Q
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from utils.app_veiculos.exceptions import (VeiculoSuccessResponse,
                                           VeiculoValidationErrorResponse,
                                           handle_veiculo_validation_error)
from utils.permissions.base import DjangoModelPermissionsWithView

from .models import MotoTaxiVeiculo, TaxiVeiculo, TransporteMunicipalVeiculo
from .serializers import (MotoTaxiVeiculoCreateSerializer,
                          MotoTaxiVeiculoSerializer,
                          MotoTaxiVeiculoViewSerializer,
                          TaxiVeiculoCreateSerializer, TaxiVeiculoSerializer,
                          TaxiVeiculoViewSerializer,
                          TransporteMunicipalVeiculoCreateSerializer,
                          TransporteMunicipalVeiculoSerializer,
                          TransporteMunicipalVeiculoViewSerializer,
                          VeiculoResumoSerializer)

logger = logging.getLogger(__name__)


# ============================================================================
# VIEWSETS BASE
# ============================================================================

class BaseVeiculoViewSet(ModelViewSet):
    """
    ViewSet base para todos os tipos de veículos.
    Contém funcionalidades comuns e permissões padrão.
    """
    permission_classes = [DjangoModelPermissionsWithView]
    lookup_field = 'identificador_unico_veiculo'

    def get_serializer_class(self):
        """Retorna o serializer apropriado baseado na ação."""
        if self.action == 'create':
            return self.create_serializer_class
        elif self.action in ['retrieve', 'list']:
            return self.view_serializer_class
        return self.serializer_class

    def get_queryset(self):
        """Retorna o queryset com filtros aplicados."""
        queryset = self.model.objects.all()

        # Filtra por permissões do usuário
        if not self.request.user.is_staff:
            # Usuários não-administradores só veem seus próprios veículos
            queryset = queryset.filter(usuario=self.request.user)

        # Filtro por usuário (matricula) - apenas para admins
        matricula = self.request.query_params.get('matricula', None)
        if matricula and self.request.user.is_staff:
            queryset = queryset.filter(usuario__matricula=matricula)

        # Filtro por placa
        placa = self.request.query_params.get('placa', None)
        if placa:
            queryset = queryset.filter(placa__icontains=placa)

        # Filtro por marca
        marca = self.request.query_params.get('marca', None)
        if marca:
            queryset = queryset.filter(marca__icontains=marca)

        # Filtro por modelo
        modelo = self.request.query_params.get('modelo', None)
        if modelo:
            queryset = queryset.filter(modelo__icontains=modelo)

        # Busca geral
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(placa__icontains=search) |
                Q(marca__icontains=search) |
                Q(modelo__icontains=search) |
                Q(cor__icontains=search) |
                Q(usuario__nome_completo__icontains=search) |
                Q(identificador_unico_veiculo__icontains=search)
            )

        return queryset.select_related('usuario')

    @action(detail=False, methods=['get'])
    def meus_veiculos(self, request):
        """Retorna apenas os veículos do usuário logado."""
        try:
            queryset = self.model.objects.filter(usuario=request.user)

            # Aplica filtros específicos do tipo de veículo
            if hasattr(self, 'get_queryset_filters'):
                queryset = self.get_queryset_filters(queryset)

            # Aplica filtros de busca
            search = request.query_params.get('search', None)
            if search:
                queryset = queryset.filter(
                    Q(placa__icontains=search) |
                    Q(marca__icontains=search) |
                    Q(modelo__icontains=search) |
                    Q(cor__icontains=search) |
                    Q(identificador_unico_veiculo__icontains=search)
                )

            # Paginação
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.view_serializer_class(page, many=True)
                paginated_response = self.get_paginated_response(
                    serializer.data
                )

                response_data = VeiculoSuccessResponse.veiculos_listados(
                    data=paginated_response.data,
                    count=queryset.count()
                )
                return Response(response_data, status=status.HTTP_200_OK)

            # Sem paginação
            serializer = self.view_serializer_class(queryset, many=True)
            response_data = VeiculoSuccessResponse.veiculos_listados(
                data=serializer.data,
                count=queryset.count()
            )

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Erro ao listar meus veículos: {str(e)}")
            error_response = handle_veiculo_validation_error(e)
            return Response(error_response, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request, *args, **kwargs):
        """Cria um novo veículo."""
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            instance = serializer.save()

            # Log da criação
            logger.info(
                f"Veículo {self.tipo_veiculo} criado: "
                f"{instance.identificador_unico_veiculo} por {request.user}"
            )

            # Retorna dados completos do veículo criado
            view_serializer = self.view_serializer_class(instance)
            response_data = VeiculoSuccessResponse.veiculo_created(
                data=view_serializer.data,
                tipo_veiculo=self.tipo_veiculo
            )

            return Response(response_data, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(
                f"Erro ao criar veículo {self.tipo_veiculo}: {str(e)}"
            )
            error_response = handle_veiculo_validation_error(e)
            return Response(error_response, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, *args, **kwargs):
        """Recupera um veículo específico."""
        try:
            instance = self.get_object()

            # Verifica se o usuário tem permissão para ver este veículo
            if not request.user.is_staff and instance.usuario != request.user:
                error_response = VeiculoValidationErrorResponse.acesso_negado(
                    "Você só pode visualizar seus próprios veículos."
                )
                return Response(
                    error_response, status=status.HTTP_403_FORBIDDEN
                )

            serializer = self.get_serializer(instance)

            response_data = VeiculoSuccessResponse.veiculo_retrieved(
                data=serializer.data,
                tipo_veiculo=self.tipo_veiculo
            )

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Erro ao recuperar veículo: {str(e)}")
            error_response = (
                VeiculoValidationErrorResponse.veiculo_nao_encontrado(
                    kwargs.get('identificador_unico_veiculo', 'N/A')
                )
            )
            return Response(error_response, status=status.HTTP_404_NOT_FOUND)

    def update(self, request, *args, **kwargs):
        """Atualiza um veículo."""
        try:
            partial = kwargs.pop('partial', False)
            instance = self.get_object()

            # Verifica se o usuário tem permissão para editar este veículo
            if not request.user.is_staff and instance.usuario != request.user:
                error_response = VeiculoValidationErrorResponse.acesso_negado(
                    "Você só pode editar seus próprios veículos."
                )
                return Response(
                    error_response, status=status.HTTP_403_FORBIDDEN
                )

            serializer = self.get_serializer(
                instance, data=request.data, partial=partial
            )
            serializer.is_valid(raise_exception=True)
            updated_instance = serializer.save()

            # Log da atualização
            logger.info(
                f"Veículo {self.tipo_veiculo} atualizado: "
                f"{updated_instance.identificador_unico_veiculo} "
                f"por {request.user}"
            )

            # Retorna dados completos do veículo atualizado
            view_serializer = self.view_serializer_class(updated_instance)
            response_data = VeiculoSuccessResponse.veiculo_updated(
                data=view_serializer.data,
                tipo_veiculo=self.tipo_veiculo
            )

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Erro ao atualizar veículo: {str(e)}")
            error_response = handle_veiculo_validation_error(e)
            return Response(error_response, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        """Remove um veículo."""
        try:
            instance = self.get_object()

            # Verifica se o usuário tem permissão para deletar este veículo
            if not request.user.is_staff and instance.usuario != request.user:
                error_response = VeiculoValidationErrorResponse.acesso_negado(
                    "Você só pode deletar seus próprios veículos."
                )
                return Response(
                    error_response, status=status.HTTP_403_FORBIDDEN
                )

            identificador = instance.identificador_unico_veiculo

            # Log da remoção
            logger.info(
                f"Veículo {self.tipo_veiculo} removido: "
                f"{identificador} por {request.user}"
            )

            self.perform_destroy(instance)

            response_data = VeiculoSuccessResponse.veiculo_deleted(
                tipo_veiculo=self.tipo_veiculo
            )

            return Response(response_data, status=status.HTTP_204_NO_CONTENT)

        except Exception as e:
            logger.error(f"Erro ao remover veículo: {str(e)}")
            error_response = (
                VeiculoValidationErrorResponse.veiculo_nao_encontrado(
                    kwargs.get('identificador_unico_veiculo', 'N/A')
                )
            )
            return Response(error_response, status=status.HTTP_404_NOT_FOUND)

    def list(self, request, *args, **kwargs):
        """Lista veículos com filtros opcionais."""
        try:
            queryset = self.filter_queryset(self.get_queryset())

            # Paginação
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                paginated_response = self.get_paginated_response(
                    serializer.data
                )

                # Customiza a resposta paginada
                response_data = VeiculoSuccessResponse.veiculos_listados(
                    data=paginated_response.data,
                    count=queryset.count()
                )
                return Response(response_data, status=status.HTTP_200_OK)

            # Sem paginação
            serializer = self.get_serializer(queryset, many=True)
            response_data = VeiculoSuccessResponse.veiculos_listados(
                data=serializer.data,
                count=queryset.count()
            )

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Erro ao listar veículos: {str(e)}")
            error_response = handle_veiculo_validation_error(e)
            return Response(error_response, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def resumo(self, request):
        """Retorna lista resumida de veículos para performance."""
        try:
            queryset = self.filter_queryset(self.get_queryset())
            serializer = VeiculoResumoSerializer(queryset, many=True)

            response_data = VeiculoSuccessResponse.veiculos_listados(
                data=serializer.data,
                count=queryset.count()
            )

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Erro ao listar resumo de veículos: {str(e)}")
            error_response = handle_veiculo_validation_error(e)
            return Response(error_response, status=status.HTTP_400_BAD_REQUEST)


# ============================================================================
# VIEWSETS ESPECÍFICOS POR TIPO DE VEÍCULO
# ============================================================================

class TaxiVeiculoViewSet(BaseVeiculoViewSet):
    """
    ViewSet para veículos de táxi.
    Fornece operações CRUD completas com permissões do Django.
    """
    model = TaxiVeiculo
    queryset = TaxiVeiculo.objects.all()
    serializer_class = TaxiVeiculoSerializer
    create_serializer_class = TaxiVeiculoCreateSerializer
    view_serializer_class = TaxiVeiculoViewSerializer
    tipo_veiculo = "táxi"


class MotoTaxiVeiculoViewSet(BaseVeiculoViewSet):
    """
    ViewSet para veículos de mototáxi.
    Fornece operações CRUD completas com permissões do Django.
    """
    model = MotoTaxiVeiculo
    queryset = MotoTaxiVeiculo.objects.all()
    serializer_class = MotoTaxiVeiculoSerializer
    create_serializer_class = MotoTaxiVeiculoCreateSerializer
    view_serializer_class = MotoTaxiVeiculoViewSerializer
    tipo_veiculo = "mototáxi"


class TransporteMunicipalVeiculoViewSet(BaseVeiculoViewSet):
    """
    ViewSet para veículos de transporte municipal.
    Fornece operações CRUD completas com permissões do Django.
    Inclui filtros específicos para linha e capacidade.
    """
    model = TransporteMunicipalVeiculo
    queryset = TransporteMunicipalVeiculo.objects.all()
    serializer_class = TransporteMunicipalVeiculoSerializer
    create_serializer_class = TransporteMunicipalVeiculoCreateSerializer
    view_serializer_class = TransporteMunicipalVeiculoViewSerializer
    tipo_veiculo = "transporte municipal"

    def get_queryset_filters(self, queryset):
        """Aplica filtros específicos do transporte municipal."""
        # Filtro por linha
        linha = self.request.query_params.get('linha', None)
        if linha:
            queryset = queryset.filter(linha__icontains=linha)

        # Filtro por capacidade mínima
        capacidade_min = self.request.query_params.get('capacidade_min', None)
        if capacidade_min:
            try:
                queryset = queryset.filter(capacidade__gte=int(capacidade_min))
            except ValueError:
                pass

        # Filtro por capacidade máxima
        capacidade_max = self.request.query_params.get('capacidade_max', None)
        if capacidade_max:
            try:
                queryset = queryset.filter(capacidade__lte=int(capacidade_max))
            except ValueError:
                pass

        return queryset

    def get_queryset(self):
        """Estende o queryset base com filtros específicos."""
        queryset = super().get_queryset()
        return self.get_queryset_filters(queryset)

    @action(detail=False, methods=['get'])
    def por_linha(self, request):
        """Lista veículos agrupados por linha."""
        try:
            queryset = self.filter_queryset(self.get_queryset())

            # Agrupa por linha
            linhas = {}
            for veiculo in queryset:
                linha = veiculo.linha
                if linha not in linhas:
                    linhas[linha] = []

                linhas[linha].append(
                    VeiculoResumoSerializer(veiculo).data
                )

            response_data = VeiculoSuccessResponse.veiculos_listados(
                data={
                    'linhas': linhas,
                    'total_linhas': len(linhas),
                    'total_veiculos': queryset.count()
                }
            )

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Erro ao agrupar veículos por linha: {str(e)}")
            error_response = handle_veiculo_validation_error(e)
            return Response(error_response, status=status.HTTP_400_BAD_REQUEST)
