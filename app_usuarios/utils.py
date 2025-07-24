
import datetime


def gerar_matricula_para_usuario(usuario, usuario_model):
    today = datetime.date.today().strftime('%Y%m%d')
    grupo_iniciais = {
        'FISCAL': 'FIS',
        'ATENDENTE ADMINISTRATIVO': 'ATD',
        'ADMINISTRADOR': 'ADM',
        'TAXISTA': 'TAX',
        'MOTOTAXISTA': 'MTX',
        'MOTOTRISTACONDUTOR': 'MTC',
    }
    grupos = usuario.groups.all()
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
    prefixo = f"{today}-{iniciais}-"
    count = (
        usuario_model.objects.filter(
            matricula__startswith=prefixo
        ).count() + 1
    )
    return f"{prefixo}{count:03d}"
