from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import UsuarioCustom
from .serializers import (CustomTokenObtainPairSerializer,
                          IsAdminToCreateAdmin,
                          UsuarioAtivarDesativarSerializer,
                          UsuarioCustomCreateSerializer)


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class UsuarioCustomCreateView(generics.CreateAPIView):
    queryset = UsuarioCustom.objects.all()
    serializer_class = UsuarioCustomCreateSerializer

    # Permite apenas admins criarem outros admins
    permission_classes = [IsAdminToCreateAdmin]


# View para ativar/desativar o próprio usuário autenticado
class UsuarioAtivarDesativarView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request):
        serializer = UsuarioAtivarDesativarSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        user.is_active = serializer.validated_data['is_active']
        user.save()
        status_msg = (
            f'Usuário {"ativado" if user.is_active else "desativado"} com sucesso.'
        )
        return Response({'detail': status_msg})
