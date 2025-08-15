"""
URLs para o app de veículos do sistema SITA.
Define as rotas para todos os tipos de veículos.
"""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (MotoTaxiVeiculoViewSet, TaxiVeiculoViewSet,
                    TransporteMunicipalVeiculoViewSet)

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

urlpatterns = [
    # Inclui as URLs geradas automaticamente pelo roteador
    path('', include(router.urls)),
]
