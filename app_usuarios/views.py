from rest_framework import generics, permissions, status
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
        matricula = request.data.get('matricula')
        # Se admin, pode passar a matrícula de qualquer usuário
        if request.user.is_staff or request.user.is_superuser:
            if not matricula:
                return Response(
                    {'detail': 'matricula é obrigatória para admin.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            try:
                user = UsuarioCustom.objects.get(matricula=matricula)
            except UsuarioCustom.DoesNotExist:
                return Response(
                    {'detail': 'Usuário não encontrado.'},
                    status=status.HTTP_404_NOT_FOUND
                )
        else:
            # Usuário comum só pode alterar a si mesmo
            user = request.user
            if matricula and matricula != user.matricula:
                return Response(
                    {'detail': 'Você só pode alterar seu próprio status.'},
                    status=status.HTTP_403_FORBIDDEN
                )
        user.is_active = serializer.validated_data['is_active']
        user.save()
        status_msg = (

            f'Usuário {"ativado" if user.is_active else "desativado"} com sucesso.'  # noqa
        )
        return Response({'detail': status_msg}, status=status.HTTP_200_OK)


class IsSelfOrHasModelPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj == request.user


class UsuarioCustomUpdateView(generics.UpdateAPIView):
    queryset = UsuarioCustom.objects.all()
    serializer_class = UsuarioCustomCreateSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        permissions.DjangoModelPermissions | IsSelfOrHasModelPermission
    ]
