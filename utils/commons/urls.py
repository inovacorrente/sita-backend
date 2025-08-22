"""
Utilitários para construção de URLs dinâmicas do projeto SITA.
Centraliza a lógica de geração de URLs completas para diferentes ambientes.
"""
from django.conf import settings
from django.urls import reverse


def build_absolute_url(view_name: str, kwargs: dict = None,
                       request=None) -> str:
    """
    Constrói uma URL absoluta baseada nas configurações do projeto.

    Args:
        view_name: Nome da view para reverse()
        kwargs: Argumentos para a URL
        request: Request object (opcional) para obter domínio atual

    Returns:
        URL absoluta completa
    """
    # Construir URL relativa
    try:
        relative_url = reverse(view_name, kwargs=kwargs or {})
    except Exception:
        # Fallback para URL manual se reverse falhar
        if kwargs and 'identificador_veiculo' in kwargs:
            identificador = kwargs['identificador_veiculo']
            relative_url = f"/api/veiculos/veiculo/{identificador}/info/"
        else:
            raise ValueError(f"Não foi possível gerar URL para {view_name}")

    # Obter base URL
    base_url = get_base_url(request)

    return f"{base_url}{relative_url}"


def get_base_url(request=None) -> str:
    """
    Obtém a URL base do projeto baseada nas configurações e contexto.

    Args:
        request: Request object (opcional) para obter domínio atual

    Returns:
        URL base (ex: 'https://meudominio.com' ou 'http://localhost:8000')
    """
    # 1. Prioridade: usar request se disponível (mais confiável)
    if request is not None:
        scheme = 'https' if request.is_secure() else 'http'
        host = request.get_host()
        return f"{scheme}://{host}"

    # 2. Segunda prioridade: SITE_DOMAIN configurado
    if hasattr(settings, 'SITE_DOMAIN') and settings.SITE_DOMAIN:
        protocol = get_protocol_from_settings()
        return f"{protocol}://{settings.SITE_DOMAIN}"

    # 3. Terceira prioridade: primeiro ALLOWED_HOST
    if (hasattr(settings, 'ALLOWED_HOSTS') and
            settings.ALLOWED_HOSTS and
            settings.ALLOWED_HOSTS[0] != '*'):
        host = settings.ALLOWED_HOSTS[0]
        protocol = 'https' if not settings.DEBUG else 'http'
        return f"{protocol}://{host}"

    # 4. Fallback: desenvolvimento local
    return "http://localhost:8000"


def get_protocol_from_settings() -> str:
    """
    Determina o protocolo (http/https) baseado nas configurações de segurança.

    Returns:
        'https' ou 'http'
    """
    # Verificar configurações de HTTPS
    if getattr(settings, 'SECURE_SSL_REDIRECT', False):
        return 'https'

    # Em produção (DEBUG=False), usar HTTPS por padrão
    if not settings.DEBUG:
        return 'https'

    # Em desenvolvimento, usar HTTP
    return 'http'


def build_media_url(media_path: str, request=None) -> str:
    """
    Constrói URL completa para arquivos de media.

    Args:
        media_path: Caminho relativo do arquivo de media
        request: Request object (opcional)

    Returns:
        URL completa para o arquivo de media
    """
    if not media_path:
        return ""

    # Garantir que media_path comece com /
    if not media_path.startswith('/'):
        if not media_path.startswith(settings.MEDIA_URL.lstrip('/')):
            media_path = f"{settings.MEDIA_URL.rstrip('/')}/{media_path}"
        media_path = f"/{media_path.lstrip('/')}"

    base_url = get_base_url(request)
    return f"{base_url}{media_path}"


def get_veiculo_info_url(identificador_veiculo: str,
                         request=None) -> str:
    """
    Constrói URL para visualização pública de informações do veículo.

    Args:
        identificador_veiculo: Identificador único do veículo
        request: Request object (opcional)

    Returns:
        URL completa para informações do veículo
    """
    return build_absolute_url(
        'info_veiculo_publico',
        {'identificador_veiculo': identificador_veiculo},
        request
    )
