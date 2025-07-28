from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    """
    Views (controladores) para a aplicação de usuários.
    Gerenciam as requisições HTTP e as respostas para operações relacionadas a usuários.

    Esta view estende a `TokenObtainPairView` da biblioteca SimpleJWT para utilizar
    um serializador customizado (`CustomTokenObtainPairSerializer`) que permite autenticação
    baseada no campo `matricula` ao invés do campo padrão `username`.

    Utilização:
        - Endpoint responsável por gerar os tokens de acesso (`access`) e atualização (`refresh`)
          para usuários autenticados com matrícula e senha.

    Exemplo de requisição (POST):
        {
            "matricula": "20240726-ADM-001",
            "password": "senha123"
        }

    Retorno esperado:
        {
            "refresh": "token_refresh...",
            "access": "token_access..."
        }
    """
