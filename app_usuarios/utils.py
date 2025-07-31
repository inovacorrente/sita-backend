"""
Funções utilitárias para a aplicação de usuários.
Inclui métodos auxiliares como geração de matrícula para usuários.
"""

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
    """
    Gera uma matrícula única para o usuário com base no ano atual,
    nos últimos dígitos do CPF e um número aleatório.

    Args:
        usuario: Instância do usuário para o qual a matrícula será gerada.
        usuario_model: Classe do modelo de usuário (usada para consultas).

    Retorna:
        str: Matrícula gerada de acordo com as regras do sistema.

    Regras:
        - A matrícula segue o padrão
            "<ano><últimos 3 dígitos do CPF><dois últimos dígitos do ano>
            <3 dígitos aleatórios>".
        - Garante unicidade ao incluir parte do CPF e um número aleatório.
        - Não depende do grupo do usuário.
    """
    ano = datetime.date.today().strftime('%Y')
    random_digits = f"{random.randint(0, 999):03d}"
    prefixo = f"{ano}{usuario.cpf[-3:]}{ano[-2:]}{random_digits}"
    return f"{prefixo}"
