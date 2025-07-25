from rest_framework import generics
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import UsuarioCustom
from .serializers import (CustomTokenObtainPairSerializer,
                          IsAdminToCreateAdmin, UsuarioCustomCreateSerializer)


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class UsuarioCustomCreateView(generics.CreateAPIView):
    queryset = UsuarioCustom.objects.all()
    serializer_class = UsuarioCustomCreateSerializer

    # Permite apenas admins criarem outros admins
    permission_classes = [IsAdminToCreateAdmin]
