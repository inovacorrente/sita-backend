from django.contrib.auth.models import Group
from rest_framework import permissions


# ============================================================================
# PERMISSIONS CUSTOMIZADAS
# ============================================================================
class IsSelfOrHasModelPermission(permissions.BasePermission):
    """
    Permissão que permite acesso se o usuário é o próprio objeto
    ou tem permissões de modelo Django.
    """

    def has_object_permission(self, request, view, obj):
        return obj == request.user


class IsAdminToCreateAdmin(permissions.BasePermission):
    """
    Só permite criar usuários administradores (is_staff=True ou
    is_superuser=True) se o usuário autenticado também for administrador.

    Também controla a atribuição de grupos restritos.
    """

    def has_permission(self, request, view):
        if request.method == 'POST':
            is_staff = request.data.get('is_staff')
            is_superuser = request.data.get('is_superuser')
            grupos_restritos = {'ADMINISTRADOR', 'ATENDENTE ADMINISTRATIVO'}
            grupos = request.data.get('groups', [])

            # Se vier como string (ex: "1"), transforma em lista
            if isinstance(grupos, str):
                try:
                    import json
                    grupos = json.loads(grupos)
                except Exception:
                    grupos = [grupos]

            # Busca nomes dos grupos se IDs forem passados
            nomes_grupos = set()
            if grupos:
                try:
                    grupos_qs = Group.objects.filter(pk__in=grupos)
                    nomes_grupos = set(g.name.upper() for g in grupos_qs)
                except Exception:
                    pass

            # Bloqueia se tentar criar admin, superuser ou usuário
            # em grupo restrito
            if (
                str(is_staff).lower() == 'true'
                or str(is_superuser).lower() == 'true'
                or (nomes_grupos & grupos_restritos)
            ):
                return (request.user and request.user.is_authenticated
                        and request.user.is_staff)

        return True
