"""
URLs para o app de veículos do sistema SITA.
Define as rotas para todos os tipos de veículos.
"""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (BannerIdentificacaoViewSet, MotoTaxiVeiculoViewSet,
                    TaxiVeiculoViewSet, TransporteMunicipalVeiculoViewSet,
                    info_veiculo_publico)

# Cria o roteador e registra os ViewSets
router = DefaultRouter()

# Registra cada tipo de veículo com seu próprio endpoint
router.register(r'taxis', TaxiVeiculoViewSet, basename='taxi-veiculo')
router.register(
    r'mototaxis', MotoTaxiVeiculoViewSet, basename='mototaxi-veiculo'
)
router.register(
    r'transporte-municipal',
    TransporteMunicipalVeiculoViewSet,
    basename='transporte-municipal-veiculo'
)

# Registra o ViewSet para banners
router.register(r'banners', BannerIdentificacaoViewSet, basename='banner')

urlpatterns = [
    # Inclui as URLs geradas automaticamente pelo roteador
    path('', include(router.urls)),

    # URL pública para visualizar informações do veículo via QR Code
    path(
        'veiculo/<str:identificador_veiculo>/info/',
        info_veiculo_publico,
        name='info_veiculo_publico'
    ),
]
