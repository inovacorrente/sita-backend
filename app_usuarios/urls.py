from django.urls import path
from .views import CustomTokenObtainPairView
# """
# Configuração das rotas (URLs) para a aplicação de usuários.
# Define os endpoints disponíveis para operações relacionadas a usuários.
# """

urlpatterns = [
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
]
