from django.urls import path

from .views import (CustomTokenObtainPairView, UsuarioAtivarDesativarView,
                    UsuarioCustomCreateView)

urlpatterns = [
    path(
        'login/',
        CustomTokenObtainPairView.as_view(),
        name='token_obtain_pair'
    ),
    path(
        'register/',
        UsuarioCustomCreateView.as_view(),
        name='usuario_register'
    ),
    path(
        'usuario/ativar-desativar/',
        UsuarioAtivarDesativarView.as_view(),
        name='usuario_ativar_desativar'
    ),
]
