
import datetime
import random
import re

from rest_framework import serializers
from validator_collection import errors, validators


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


def validar_cpf(value):
    """Valida formato e algoritmo do CPF usando validator-collection"""
    # Remove caracteres não numéricos
    cpf = re.sub(r'\D', '', value)

    # Verifica se tem exatamente 11 dígitos
    if not re.match(r'^\d{11}$', cpf):
        raise serializers.ValidationError("CPF deve ter 11 dígitos.")

    # Verifica se todos os dígitos são iguais (regex)
    if re.match(r'^(\d)\1{10}$', cpf):
        raise serializers.ValidationError("CPF inválido.")

    # Usa validator-collection para validar algoritmo do CPF
    try:
        # A biblioteca não tem validador específico para CPF,
        # então mantemos nossa validação
        def calcular_digito(cpf_parcial, peso_inicial):
            soma = sum(int(digito) * peso for digito, peso in
                       zip(cpf_parcial, range(peso_inicial, 1, -1)))
            resto = soma % 11
            return 0 if resto < 2 else 11 - resto

        # Calcula os dígitos verificadores
        primeiro_digito = calcular_digito(cpf[:9], 10)
        segundo_digito = calcular_digito(cpf[:10], 11)

        # Verifica se os dígitos calculados conferem
        if cpf[9:11] != f"{primeiro_digito}{segundo_digito}":
            raise serializers.ValidationError("CPF inválido.")

        # Valida como string numérica usando validator-collection
        validators.numeric(cpf, minimum=10000000000, maximum=99999999999)

    except (errors.InvalidValueError, ValueError):
        raise serializers.ValidationError("CPF inválido.")

    return cpf


def validar_email(value):
    """Valida formato do email usando validator-collection"""
    try:
        # Valida formato do email
        validators.email(value)
    except (errors.InvalidValueError, ValueError):
        raise serializers.ValidationError("Email inválido.")

    return value


def validar_telefone(value):
    """Valida formato do telefone usando validator-collection"""
    if value:
        # Remove caracteres não numéricos
        telefone = re.sub(r'\D', '', value)

        try:
            # Valida como string numérica
            validators.numeric(telefone)

            # Verifica tamanho (10 ou 11 dígitos)
            if len(telefone) < 10 or len(telefone) > 11:
                raise serializers.ValidationError(
                    "Telefone deve ter 10 ou 11 dígitos."
                )

            # Valida se começa com códigos válidos
            if len(telefone) == 11:
                # Celular: deve começar com 9
                if not telefone[2:3] == '9':
                    raise serializers.ValidationError(
                        "Celular deve começar com 9 após o DDD."
                    )
            elif len(telefone) == 10:
                # Fixo: não deve começar com 9
                if telefone[2:3] == '9':
                    raise serializers.ValidationError(
                        "Telefone fixo não deve começar com 9."
                    )

        except (errors.InvalidValueError, ValueError):
            raise serializers.ValidationError("Telefone inválido.")

        return telefone
    return value
