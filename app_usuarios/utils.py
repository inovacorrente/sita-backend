
import datetime
import random


def gerar_grupos_padrao():
    """
    Retorna os grupos padrão para novos usuários.
    """
    return [
        'ADMINISTRADOR',
        'ATENDENTE ADMINISTRATIVO',
        'FISCAL',
        'CONDUTOR',
    ]


def gerar_matricula_para_usuario(usuario, usuario_model):
    ano = datetime.date.today().strftime('%Y')
    random_digits = f"{random.randint(0, 999):03d}"
    prefixo = f"{ano}{usuario.cpf[-3:]}{ano[-2:]}{random_digits}"
    return f"{prefixo}"
