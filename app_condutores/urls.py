from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CondutorViewSet

# Cria o roteador e registra o ViewSet
router = DefaultRouter()
router.register(r'condutores', CondutorViewSet, basename='condutor')

urlpatterns = [
    # Inclui as URLs geradas automaticamente pelo roteador
    path('', include(router.urls)),
]
