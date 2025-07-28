from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

"""
Serializadores para o modelo de usuário customizado.
Responsável por converter instâncias de UsuarioCustom para formatos como JSON e vice-versa.
"""

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Serializador customizado para o token JWT (access e refresh) usando o campo `matricula` no lugar do `username`.

    Esta classe estende o TokenObtainPairSerializer do SimpleJWT para:
    - Adicionar claims personalizados ao token (como matrícula e email).
    - Permitir login com o campo `matricula` em vez do tradicional `username`.
    """

    @classmethod
    def get_token(cls, user):
        """
        Gera o token JWT (access e refresh) para o usuário autenticado.
        Adiciona informações personalizadas (claims extras) ao token.

        Args:
            user (UsuarioCustom): Usuário autenticado.

        Returns:
            Token: Objeto de token JWT com claims customizadas.
        """
        token = super().get_token(user)
        # Adicione claims extras se quiser
        token['matricula'] = user.matricula  # Inclui a matrícula no payload do token
        token['email'] = user.email          # Inclui o email no payload do token
        return token

    def validate(self, attrs):
        """
        Valida os dados de entrada (credenciais) para autenticação JWT.

        Substitui o campo `username` por `matricula` para compatibilidade com o SimpleJWT,
        que espera o campo `username` por padrão.

        Args:
            attrs (dict): Dados fornecidos na requisição (ex: matricula e password).

        Returns:
            dict: Dados de autenticação válidos, incluindo access e refresh tokens.
        """
        # Substitui username por matrícula
        attrs['username'] = attrs.get('matricula')
        return super().validate(attrs)
