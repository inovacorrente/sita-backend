
import datetime


def gerar_matricula_para_usuario(usuario, usuario_model):
    ano = datetime.date.today().strftime('%Y')
    grupo_iniciais = {
        'FISCAL': 'FIS',
        'ATENDENTE ADMINISTRATIVO': 'ATD',
        'ADMINISTRADOR': 'ADM',
        'TAXISTA': 'TAX',
        'MOTOTAXISTA': 'MTX',
        'MOTOTRISTACONDUTOR': 'MTC',
    }
    # Matrícula especial para superusuário
    if hasattr(usuario, 'is_superuser') and usuario.is_superuser:
        prefixo = f"{ano}ADM"
        count = (
            usuario_model.objects.filter(
                matricula__startswith=prefixo
            ).count() + 1
        )
        return f"{prefixo}{count:03d}"
    if hasattr(usuario, 'groups') and callable(getattr(usuario.groups, 'all', None)):  # noqa: E501
        grupos = usuario.groups.all()
    elif hasattr(usuario, 'groups'):
        grupos = usuario.groups  # já é lista
    else:
        grupos = []
    if grupos:
        iniciais = ''.join([
            grupo_iniciais.get(
                g.name.upper(),
                g.name[:3].upper()
            )
            for g in grupos
        ])
    else:
        iniciais = 'X'
    today = datetime.date.today().strftime('%Y%m%d')
    prefixo = f"{today}-{iniciais}-"
    count = (
        usuario_model.objects.filter(
            matricula__startswith=prefixo
        ).count() + 1
    )
    return f"{prefixo}{count:03d}"
