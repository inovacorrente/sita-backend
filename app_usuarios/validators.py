"""
Validadores customizados para os serializers de usuários.
Contém todas as validações específicas de campos.
"""

import re
from datetime import date, timedelta

from rest_framework import serializers
from validator_collection import errors, validators

from .models import UsuarioCustom

# ============================================================================
# VALIDADORES DE CAMPO BÁSICOS
# ============================================================================


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


# ============================================================================
# VALIDADORES DE SERIALIZER
# ============================================================================

def validate_cpf(value):
    """Valida formato e algoritmo do CPF"""
    try:
        return validar_cpf(value)
    except Exception as e:
        raise serializers.ValidationError(f"CPF inválido: {str(e)}")


def validate_email_unique(value, instance=None):
    """Valida formato do email e unicidade"""
    try:
        validated_email = validar_email(value)

        # Verifica se já existe outro usuário com este email
        if instance:  # Edição
            if UsuarioCustom.objects.filter(
                email=validated_email
            ).exclude(pk=instance.pk).exists():
                raise serializers.ValidationError(
                    "Este e-mail já está em uso por outro usuário."
                )
        else:  # Criação
            if UsuarioCustom.objects.filter(
                email=validated_email
            ).exists():
                raise serializers.ValidationError(
                    "Este e-mail já está em uso."
                )

        return validated_email
    except Exception as e:
        raise serializers.ValidationError(f"E-mail inválido: {str(e)}")


def validate_telefone_format(value):
    """Valida formato do telefone"""
    if value:  # Só valida se foi fornecido
        try:
            return validar_telefone(value)
        except Exception as e:
            raise serializers.ValidationError(
                f"Telefone inválido: {str(e)}"
            )
    return value


def validate_data_nascimento_range(value):
    """Valida se a data de nascimento é válida"""
    hoje = date.today()
    idade_maxima = hoje - timedelta(days=365 * 120)  # 120 anos
    idade_minima = hoje - timedelta(days=365 * 16)   # 16 anos

    if value > hoje:
        raise serializers.ValidationError(
            "A data de nascimento não pode ser no futuro."
        )

    if value < idade_maxima:
        raise serializers.ValidationError(
            "Data de nascimento muito antiga."
        )

    if value > idade_minima:
        raise serializers.ValidationError(
            "Usuário deve ter pelo menos 16 anos."
        )

    return value


def validate_password_strength(value):
    """Valida senha básica (se fornecida)"""
    # Se senha foi fornecida, faz validação básica
    if value and len(value) < 3:
        raise serializers.ValidationError(
            "A senha deve ter pelo menos 3 caracteres."
        )
    return value


def validate_password_confirmation(password, password_confirm):
    """Valida confirmação de senha"""
    if password and password_confirm:
        if password != password_confirm:
            raise serializers.ValidationError({
                'password_confirm': 'As senhas não coincidem.'
            })
    elif (password and password_confirm is not None
          and not password_confirm):
        raise serializers.ValidationError({
            'password_confirm': 'Confirmação de senha é obrigatória.'
        })


def set_default_password_as_matricula(attrs):
    """
    Define senha padrão como matrícula se não foi fornecida senha.

    Args:
        attrs (dict): Dados validados do serializer

    Returns:
        dict: Dados com senha definida (se necessário)
    """
    password = attrs.get('password')
    matricula = attrs.get('matricula')

    # Se não foi fornecida senha, usa a matrícula como senha padrão
    if not password and matricula:
        attrs['password'] = matricula

    return attrs


def validate_admin_privileges(attrs, request):
    """
    Valida privilégios administrativos baseado no usuário da requisição.

    Args:
        attrs (dict): Dados validados do serializer
        request: Objeto request com usuário autenticado

    Returns:
        dict: Dados com privilégios ajustados
    """
    if request and not request.user.is_staff:
        # Remove campos administrativos se não for admin
        attrs.pop('is_staff', None)
        attrs.pop('is_superuser', None)
        attrs.pop('groups', None)

    # Lógica de negócio: superuser deve ser staff
    if attrs.get('is_superuser') and not attrs.get('is_staff'):
        attrs['is_staff'] = True  # Auto-corrige

    return attrs
