from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import VeiculoViewSet

# Cria o roteador e registra o ViewSet
router = DefaultRouter()
urlpatterns = [
    # Inclui as URLs geradas automaticamente pelo roteador
    path('', include(router.urls)),
]
