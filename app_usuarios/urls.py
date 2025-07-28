from django.urls import path

from .views import (CustomTokenObtainPairView, UsuarioAtivarDesativarView,
                    UsuarioCustomCreateView, UsuarioCustomUpdateView)

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
        'ativar-desativar/<str:matricula>/',
        UsuarioAtivarDesativarView.as_view(),
        name='usuario_ativar_desativar'
    ),
    path('<str:matricula>/editar/',
         UsuarioCustomUpdateView.as_view(), name='usuario_editar'),
]
