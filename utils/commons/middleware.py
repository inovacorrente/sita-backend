"""
Middleware para configuração de URLs dinâmicas do projeto SITA.
Garante que as URLs sejam construídas corretamente em diferentes ambientes.
"""
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin


class URLContextMiddleware(MiddlewareMixin):
    """
    Middleware que adiciona informações de contexto de URL ao request.
    Útil para construção de URLs completas em views e serializers.
    """

    def process_request(self, request):
        """
        Adiciona informações de contexto ao request.
        """
        # Adicionar informações de protocolo e host
        request.is_secure_connection = request.is_secure()
        request.host_with_port = request.get_host()

        # Determinar URL base
        scheme = 'https' if request.is_secure() else 'http'
        request.base_url = f"{scheme}://{request.get_host()}"

        # Adicionar informação de ambiente
        request.is_production = not settings.DEBUG

        return None

    def process_response(self, request, response):
        """
        Adiciona headers de CORS para media files se necessário.
        """
        # Adicionar headers CORS para arquivos de media em desenvolvimento
        if (settings.DEBUG and
                hasattr(request, 'path') and
                request.path.startswith(settings.MEDIA_URL)):
            response['Access-Control-Allow-Origin'] = '*'
            response['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
            response['Access-Control-Allow-Headers'] = 'Content-Type'

        return response
