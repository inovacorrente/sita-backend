"""
Views para o app de veículos do sistema SITA.
Inclui ViewSets para todos os tipos de veículos com permissões do Django.
"""
import logging
import os
from io import BytesIO

import qrcode
from django.conf import settings
from django.core.files.base import ContentFile
from django.db.models import Q
from django.http import Http404, HttpResponse
from django.utils import timezone
from drf_spectacular.utils import (OpenApiParameter, OpenApiResponse,
                                   extend_schema, extend_schema_view)
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from utils.app_veiculos.exceptions import (VeiculoSuccessResponse,
                                           VeiculoValidationErrorResponse,
                                           handle_veiculo_validation_error)
from utils.permissions.base import DjangoModelPermissionsWithView

from .models import (BannerIdentificacao, MotoTaxiVeiculo, TaxiVeiculo,
                     TransporteMunicipalVeiculo)
from .serializers import (BannerCreateSerializer,
                          BannerIdentificacaoSerializer,
                          MotoTaxiVeiculoCreateSerializer,
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


# ============================================================================
# VIEWS PARA BANNER DE IDENTIFICAÇÃO
# ============================================================================


@extend_schema_view(
    retrieve=extend_schema(
        parameters=[
            OpenApiParameter(
                name='identificador_unico_veiculo',
                location=OpenApiParameter.PATH,
                description='Identificador único do veículo',
                required=True,
                type=str
            )
        ]
    ),
    create=extend_schema(
        request=BannerCreateSerializer,
        responses={
            201: BannerIdentificacaoSerializer,
            400: OpenApiResponse(description='Dados inválidos fornecidos'),
            403: OpenApiResponse(description='Sem permissão'),
            404: OpenApiResponse(description='Veículo não encontrado'),
        },
        description='Cria um novo banner de identificação para um veículo',
        summary='Criar banner de identificação'
    )
)
class BannerIdentificacaoViewSet(ModelViewSet):
    """
    ViewSet para gerenciamento de banners de identificação.
    """
    queryset = BannerIdentificacao.objects.select_related(
        'content_type'
    )
    serializer_class = BannerIdentificacaoSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissionsWithView]
    filterset_fields = ['ativo']
    search_fields = [
        # GenericForeignKey não suporta lookup direto nos search_fields
    ]
    ordering = ['-data_criacao']
    lookup_field = 'identificador_unico_veiculo'

    def get_object(self):
        """
        Sobrescreve get_object para buscar banner pelo identificador único
        do veículo.
        """
        lookup_value = self.kwargs[self.lookup_url_kwarg or self.lookup_field]

        # Buscar o banner pelo identificador único do veículo
        from django.shortcuts import get_object_or_404

        # Buscar diretamente pelo identificador único
        banner = get_object_or_404(
            BannerIdentificacao,
            identificador_unico_veiculo=lookup_value
        )

        return banner

    def get_queryset(self):
        """
        Filtra banners baseado nas permissões do usuário.
        Para GenericForeignKey, precisamos fazer o filtro de forma diferente.
        """
        queryset = super().get_queryset()

        if not self.request.user.is_staff:
            # Usuários comuns só veem seus próprios banners
            # Como GenericForeignKey não permite filtro direto,
            # vamos buscar IDs dos veículos do usuário
            from django.contrib.contenttypes.models import ContentType

            user_vehicle_ids = []

            # Buscar IDs de cada tipo de veículo do usuário
            for model_class in [TaxiVeiculo, MotoTaxiVeiculo,
                                TransporteMunicipalVeiculo]:
                content_type = ContentType.objects.get_for_model(model_class)
                vehicle_ids = list(
                    model_class.objects.filter(usuario=self.request.user)
                    .values_list('id', flat=True)
                )
                for vehicle_id in vehicle_ids:
                    user_vehicle_ids.append({
                        'content_type': content_type,
                        'object_id': vehicle_id
                    })

            # Filtrar banners apenas dos veículos do usuário
            if user_vehicle_ids:
                from django.db.models import Q
                q_filter = Q()
                for vehicle in user_vehicle_ids:
                    q_filter |= Q(
                        content_type=vehicle['content_type'],
                        object_id=vehicle['object_id']
                    )
                queryset = queryset.filter(q_filter)
            else:
                # Se não tem veículos, retorna queryset vazio
                queryset = queryset.none()

        return queryset

    def create(self, request, *args, **kwargs):
        """
        Cria um novo banner de identificação.
        """
        serializer = BannerCreateSerializer(
            data=request.data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)

        veiculo = serializer.veiculo_instance
        content_type = serializer.content_type_instance

        try:
            # Desativar banner anterior se existir
            BannerIdentificacao.objects.filter(
                content_type=content_type,
                object_id=veiculo.id,
                ativo=True
            ).update(ativo=False)

            # Criar novo banner
            banner = BannerIdentificacao.objects.create(
                content_type=content_type,
                object_id=veiculo.id
            )
            banner.gerar_banner()

            result_serializer = BannerIdentificacaoSerializer(banner)

            logger.info(
                f"Banner criado com sucesso para veículo "
                f"{veiculo.identificador_unico_veiculo}"
            )
            response_data = VeiculoSuccessResponse.veiculo_created(
                result_serializer.data, "banner de identificação"
            )
            return Response(response_data, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(f"Erro ao criar banner: {str(e)}")
            error_response = VeiculoValidationErrorResponse.erro_interno(
                {"detail": str(e)}
            )
            return Response(
                error_response, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'])
    def regenerar(self, request, identificador_unico_veiculo=None):
        """
        Regenera o banner de identificação.
        Remove o arquivo anterior antes de gerar um novo.
        """
        banner = self.get_object()

        try:
            # Guardar informações do arquivo antigo antes da regeneração
            arquivo_antigo_path = None
            arquivo_antigo_name = None

            if banner.arquivo_banner:
                try:
                    arquivo_antigo_path = str(banner.arquivo_banner.path)
                    arquivo_antigo_name = str(banner.arquivo_banner.name)
                    logger.info(
                        f"Arquivo atual antes da regeneração: "
                        f"{arquivo_antigo_name}"
                    )
                except (ValueError, OSError):
                    # Arquivo pode não existir fisicamente
                    logger.warning("Erro ao acessar arquivo antigo")

            # Regenerar o banner (isso cria um novo arquivo)
            banner.gerar_banner()

            # Recarregar o banner do banco para ter o arquivo atualizado
            banner.refresh_from_db()

            novo_arquivo_path = None
            if banner.arquivo_banner:
                try:
                    novo_arquivo_path = str(banner.arquivo_banner.path)
                    logger.info(
                        f"Novo arquivo após regeneração: "
                        f"{banner.arquivo_banner.name}"
                    )
                except (ValueError, OSError):
                    pass

            # Remover o arquivo antigo se existir e for diferente do novo
            if (arquivo_antigo_path and
                    os.path.exists(arquivo_antigo_path) and
                    arquivo_antigo_path != novo_arquivo_path):

                try:
                    os.remove(arquivo_antigo_path)
                    logger.info(
                        f"Arquivo antigo removido: {arquivo_antigo_name}"
                    )

                    # Tentar remover diretório se estiver vazio
                    diretorio = os.path.dirname(arquivo_antigo_path)
                    try:
                        if (os.path.exists(diretorio) and
                                not os.listdir(diretorio)):
                            os.rmdir(diretorio)
                            logger.info(
                                f"Diretório vazio removido: {diretorio}"
                            )
                    except OSError:
                        pass  # Diretório não vazio ou erro

                except (OSError, ValueError) as e:
                    logger.warning(
                        f"Erro ao remover arquivo antigo: {str(e)}"
                    )
            elif arquivo_antigo_path:
                logger.info(
                    f"Arquivo antigo não removido - "
                    f"Existe: {os.path.exists(arquivo_antigo_path)}, "
                    f"Diferente: {arquivo_antigo_path != novo_arquivo_path}"
                )

            serializer = self.get_serializer(banner)

            logger.info(
                f"Banner regenerado para veículo "
                f"{banner.veiculo.identificador_unico_veiculo}"
            )
            response_data = VeiculoSuccessResponse.veiculo_updated(
                serializer.data, "banner de identificação"
            )
            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(
                f"Erro ao regenerar banner {identificador_unico_veiculo}: "
                f"{str(e)}"
            )
            error_response = VeiculoValidationErrorResponse.erro_interno(
                {"detail": str(e)}
            )
            return Response(
                error_response, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['get'])
    def download(self, request, identificador_unico_veiculo=None):
        """
        Faz download do arquivo do banner.
        """
        banner = self.get_object()

        if not banner.arquivo_banner:
            raise Http404("Arquivo do banner não encontrado")

        try:
            response = HttpResponse(
                banner.arquivo_banner.read(), content_type='image/png'
            )
            filename = (
                f"banner_{banner.veiculo.identificador_unico_veiculo}.png"
            )
            response['Content-Disposition'] = (
                f'attachment; filename="{filename}"'
            )

            logger.info(
                f"Download do banner para veículo "
                f"{banner.veiculo.identificador_unico_veiculo}"
            )
            return response

        except Exception as e:
            logger.error(
                f"Erro no download do banner {identificador_unico_veiculo}: "
                f"{str(e)}"
            )
            raise Http404("Erro ao acessar arquivo do banner")

    @action(detail=True, methods=['get'])
    def url_completa(self, request, identificador_unico_veiculo=None):
        """
        Retorna URLs completas para o banner e informações do veículo.
        """
        from utils.commons.urls import build_media_url, get_veiculo_info_url

        banner = self.get_object()

        try:
            # URL completa do arquivo do banner
            banner_url = ""
            if banner.arquivo_banner:
                banner_url = build_media_url(
                    banner.arquivo_banner.url,
                    request
                )

            # URL completa das informações do veículo (QR Code)
            veiculo_info_url = get_veiculo_info_url(
                banner.veiculo.identificador_unico_veiculo,
                request
            )

            identificador = banner.veiculo.identificador_unico_veiculo
            data = {
                'banner_id': banner.id,
                'identificador_veiculo': identificador,
                'placa': banner.veiculo.placa,
                'banner_url': banner_url,
                'qr_url': veiculo_info_url,
                'ativo': banner.ativo,
                'data_criacao': banner.data_criacao,
                'data_atualizacao': banner.data_atualizacao
            }

            response_data = VeiculoSuccessResponse.veiculo_encontrado(
                data, "URLs completas do banner"
            )
            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(
                f"Erro ao obter URLs do banner {identificador_unico_veiculo}: "
                f"{str(e)}"
            )
            error_response = VeiculoValidationErrorResponse.erro_interno(
                {"detail": str(e)}
            )
            return Response(
                error_response, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def por_veiculo(self, request):
        """
        Busca banner por identificador único do veículo.
        """
        from django.contrib.contenttypes.models import ContentType

        identificador_veiculo = request.query_params.get(
            'identificador_veiculo'
        )

        if not identificador_veiculo:
            error_response = VeiculoValidationErrorResponse.campo_obrigatorio(
                {"identificador_veiculo": ["Este campo é obrigatório."]}
            )
            return Response(error_response, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Buscar o veículo em todos os tipos
            veiculo = None
            content_type = None

            for model_class in [TaxiVeiculo, MotoTaxiVeiculo,
                                TransporteMunicipalVeiculo]:
                try:
                    veiculo = model_class.objects.select_related(
                        'usuario'
                    ).get(identificador_unico_veiculo=identificador_veiculo)
                    content_type = ContentType.objects.get_for_model(
                        model_class
                    )
                    break
                except model_class.DoesNotExist:
                    continue

            if not veiculo:
                error_response = (
                    VeiculoValidationErrorResponse.veiculo_nao_encontrado(
                        identificador_veiculo
                    )
                )
                return Response(
                    error_response, status=status.HTTP_404_NOT_FOUND
                )

            # Buscar banner ativo
            banner = BannerIdentificacao.objects.filter(
                content_type=content_type,
                object_id=veiculo.id,
                ativo=True
            ).first()

            if not banner:
                error_response = (
                    VeiculoValidationErrorResponse.veiculo_nao_encontrado(
                        "Banner não encontrado para este veículo"
                    )
                )
                return Response(
                    error_response, status=status.HTTP_404_NOT_FOUND
                )

            # Verificar permissão
            if (not request.user.is_staff and
                    veiculo.usuario != request.user):
                error_response = VeiculoValidationErrorResponse.acesso_negado()
                return Response(
                    error_response, status=status.HTTP_403_FORBIDDEN
                )

            serializer = self.get_serializer(banner)
            response_data = VeiculoSuccessResponse.veiculo_encontrado(
                serializer.data
            )
            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Erro na busca do banner: {str(e)}")
            error_response = VeiculoValidationErrorResponse.erro_interno()
            return Response(
                error_response, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class InfoVeiculoPublicoView(ModelViewSet):
    """
    View para visualizar informações básicas do veículo via QR Code.
    Requer autenticação e permissões adequadas.
    """
    queryset = BannerIdentificacao.objects.select_related('content_type')
    serializer_class = BannerIdentificacaoSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissionsWithView]
    lookup_field = 'identificador_veiculo'
    http_method_names = ['get']  # Apenas GET permitido

    def retrieve(self, request, *args, **kwargs):
        """
        Retorna informações básicas do veículo pelo identificador único.
        """
        identificador_veiculo = kwargs.get('identificador_veiculo')

        try:
            from django.contrib.contenttypes.models import ContentType

            # Buscar em todos os tipos de veículo
            veiculo = None
            content_type = None

            for model_class in [TaxiVeiculo, MotoTaxiVeiculo,
                                TransporteMunicipalVeiculo]:
                try:
                    veiculo = model_class.objects.select_related(
                        'usuario'
                    ).get(
                        identificador_unico_veiculo=identificador_veiculo
                    )
                    content_type = ContentType.objects.get_for_model(
                        model_class
                    )
                    break
                except model_class.DoesNotExist:
                    continue

            if not veiculo:
                error_msg = (
                    VeiculoValidationErrorResponse.veiculo_nao_encontrado(
                        identificador_veiculo
                    )
                )
                return Response(error_msg, status=status.HTTP_404_NOT_FOUND)

            # Verificar se tem banner ativo
            banner = BannerIdentificacao.objects.filter(
                content_type=content_type,
                object_id=veiculo.id,
                ativo=True
            ).first()

            if not banner:
                error_msg = (
                    VeiculoValidationErrorResponse.veiculo_nao_encontrado(
                        "Informações não disponíveis"
                    )
                )
                return Response(error_msg, status=status.HTTP_404_NOT_FOUND)

            # Retornar apenas informações públicas básicas
            data = {
                'identificador_unico': veiculo.identificador_unico_veiculo,
                'placa': veiculo.placa,
                'marca': veiculo.marca,
                'modelo': veiculo.modelo,
                'cor': veiculo.cor,
                'ano_fabricacao': veiculo.anoFabricacao,
                'tipo_veiculo': veiculo.__class__.__name__,
                'proprietario': {
                    'nome': veiculo.usuario.nome_completo,
                    # Não incluir informações sensíveis como CPF, etc.
                },
                'data_verificacao': timezone.now().isoformat()
            }

            # Adicionar informações específicas por tipo
            if isinstance(veiculo, TransporteMunicipalVeiculo):
                data['linha'] = veiculo.linha
                data['capacidade'] = veiculo.capacidade

            logger.info(
                f"Consulta de informações do veículo "
                f"{identificador_veiculo} por {request.user}"
            )
            response_data = VeiculoSuccessResponse.veiculo_encontrado(
                data, "Informações do veículo"
            )
            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(
                f"Erro na consulta do veículo "
                f"{identificador_veiculo}: {str(e)}"
            )
            error_response = VeiculoValidationErrorResponse.erro_interno()
            return Response(
                error_response, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# Instância da view para uso nas URLs
info_veiculo_publico = InfoVeiculoPublicoView.as_view({'get': 'retrieve'})
