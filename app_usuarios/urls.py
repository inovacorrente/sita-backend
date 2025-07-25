from django.urls import path

from .views import CustomTokenObtainPairView, UsuarioCustomCreateView

urlpatterns = [
    path('login/', CustomTokenObtainPairView.as_view(),
         name='token_obtain_pair'),
    path('register/', UsuarioCustomCreateView.as_view(), name='usuario_register'),
]
