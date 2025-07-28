"""
Funções utilitárias para a aplicação de usuários.
Inclui métodos auxiliares como geração de matrícula para usuários.
"""

import datetime


def gerar_matricula_para_usuario(usuario, usuario_model):
    """
    Gera uma matrícula única para o usuário com base em seu grupo e data.

    Args:
        usuario: Instância do usuário para o qual a matrícula será gerada.
        usuario_model: Classe do modelo de usuário (usada para consultas).

    Retorna:
        str: Matrícula gerada de acordo com regras do sistema.

    Regras:
        - Para superusuários, a matrícula segue o padrão "<ano>ADM<sequencial>".
        - Para outros usuários, a matrícula segue o padrão "<data>-<grupo>-<sequencial>".
        - Caso o usuário não pertença a nenhum grupo, utiliza-se 'X' como identificador de grupo.
    """
    ano = datetime.date.today().strftime('%Y')

    # Mapeia nomes de grupos para abreviações padronizadas
    grupo_iniciais = {
        'FISCAL': 'FIS',
        'ATENDENTE ADMINISTRATIVO': 'ATD',
        'ADMINISTRADOR': 'ADM',
        'TAXISTA': 'TAX',
        'MOTOTAXISTA': 'MTX',
        'MOTOTRISTACONDUTOR': 'MTC',
    }

    # Matrícula especial para superusuário: <ano>ADM<sequencial>
    if hasattr(usuario, 'is_superuser') and usuario.is_superuser:
        prefixo = f"{ano}ADM"
        count = (
            usuario_model.objects.filter(
                matricula__startswith=prefixo
            ).count() + 1
        )
        return f"{prefixo}{count:03d}"

    # Obtém grupos do usuário, se houver
    if hasattr(usuario, 'groups'):
        if callable(getattr(usuario.groups, 'all', None)):
            grupos = usuario.groups.all()
        else:
            grupos = usuario.groups
    else:
        grupos = []
        
    # Gera as iniciais dos grupos; se não houver, usa 'X'
    if grupos:
        iniciais = ''.join([
            grupo_iniciais.get(
                g.name.upper(),  # Busca mapeamento pelo nome do grupo em caixa alta
                g.name[:3].upper()  # Se não houver mapeamento, usa os 3 primeiros caracteres do nome
            )
            for g in grupos
        ])
    else:
        iniciais = 'X'

    # Prefixo baseado na data e grupo: <data>-<grupo>-
    today = datetime.date.today().strftime('%Y%m%d')
    prefixo = f"{today}-{iniciais}-"

    # Conta quantos usuários já têm esse prefixo e gera um novo sequencial
    count = (
        usuario_model.objects.filter(
            matricula__startswith=prefixo
        ).count() + 1
    )

    return f"{prefixo}{count:03d}"
