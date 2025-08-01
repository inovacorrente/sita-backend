from django.urls import path

from .views import (  # Autenticação; CRUD de Usuários; Funcionalidades específicas
    CustomTokenObtainPairView, UsuarioAtivarDesativarView,
    UsuarioCustomCreateView, UsuarioCustomDetailView, UsuarioCustomListView,
    UsuarioCustomUpdateView, UsuarioMeView)

urlpatterns = [
    # Autenticação
    path(
        'login/',
        CustomTokenObtainPairView.as_view(),
        name='token_obtain_pair'
    ),

    # Usuário - próprias informações
    path(
        'me/',
        UsuarioMeView.as_view(),
        name='usuario_me'
    ),

    # CRUD de Usuários
    path(
        'usuarios/',
        UsuarioCustomListView.as_view(),
        name='usuario_list'
    ),
    path(
        'register/',
        UsuarioCustomCreateView.as_view(),
        name='usuario_register'
    ),
    path(
        '<str:matricula>/',
        UsuarioCustomDetailView.as_view(),
        name='usuario_detail'
    ),
    path(
        '<str:matricula>/editar/',
        UsuarioCustomUpdateView.as_view(),
        name='usuario_editar'
    ),

    # Funcionalidades específicas
    path(
        'ativar-desativar/<str:matricula>/',
        UsuarioAtivarDesativarView.as_view(),
        name='usuario_ativar_desativar'
    ),
]
