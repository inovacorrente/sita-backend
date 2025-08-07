"""
Validadores customizados para os serializers de usuários.
Contém todas as validações específicas de campos.
"""

import re
from datetime import date, timedelta

from rest_framework import serializers
from validator_collection import errors, validators

from app_usuarios.models import UsuarioCustom

# ============================================================================
# VALIDADORES DE CAMPO BÁSICOS
# ============================================================================


def validar_cpf(value):
    """Valida formato e algoritmo do CPF usando validator-collection"""
    # Remove caracteres não numéricos
    cpf = re.sub(r'\D', '', value)

    # Verifica se tem exatamente 11 dígitos
    if not re.match(r'^\d{11}$', cpf):
        raise serializers.ValidationError(
            "CPF deve conter exatamente 11 dígitos numéricos."
        )

    # Verifica se todos os dígitos são iguais (regex)
    if re.match(r'^(\d)\1{10}$', cpf):
        raise serializers.ValidationError(
            "CPF não pode ter todos os dígitos iguais."
        )

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
            raise serializers.ValidationError(
                "CPF inválido. Verifique os dígitos e tente novamente."
            )

        # Valida como string numérica usando validator-collection
        validators.numeric(cpf, minimum=00000000000, maximum=99999999999)

    except (errors.CannotCoerceError, errors.MinimumValueError,
            errors.MaximumValueError, ValueError):
        raise serializers.ValidationError(
            "CPF inválido. Verifique os dígitos e tente novamente."
        )

    return cpf


def validar_email(value):
    """Valida formato do email usando validator-collection"""
    try:
        # Valida formato do email
        validators.email(value)
    except (errors.InvalidEmailError, ValueError):
        raise serializers.ValidationError(
            "Formato de e-mail inválido. Use o formato: exemplo@dominio.com"
        )

    return value


def validar_telefone(value):
    """
    Valida formato do telefone usando validator-collection.

    Retorna apenas os dígitos do telefone se válido.
    Em caso de erro, retorna mensagem padronizada conforme API SITA.
    """
    if value:
        telefone = re.sub(r'\D', '', value)
        try:
            validators.numeric(telefone)
            if len(telefone) < 10 or len(telefone) > 11:
                raise serializers.ValidationError({
                    "success": False,
                    "error": {
                        "code": "INVALID_PHONE_LENGTH",
                        "message": (
                            "Telefone deve ter 10 ou 11 dígitos com DDD. "
                            "Exemplo: (11) 99999-9999"
                        ),
                        "details": {"telefone": telefone}
                    }
                })
            if len(telefone) == 11:
                if not telefone[2:3] == '9':
                    raise serializers.ValidationError({
                        "success": False,
                        "error": {
                            "code": "INVALID_CELLPHONE_FORMAT",
                            "message": (
                                "Número de celular deve começar com 9 "
                                "após o DDD. Exemplo: (11) 99999-9999"
                            ),
                            "details": {"telefone": telefone}
                        }
                    })
            elif len(telefone) == 10:
                if telefone[2:3] == '9':
                    raise serializers.ValidationError({
                        "success": False,
                        "error": {
                            "code": "INVALID_LANDLINE_FORMAT",
                            "message": (
                                "Telefone fixo não deve começar com 9 "
                                "após o DDD. Exemplo: (11) 3333-4444"
                            ),
                            "details": {"telefone": telefone}
                        }
                    })
        except (errors.CannotCoerceError, ValueError):
            raise serializers.ValidationError({
                "success": False,
                "error": {
                    "code": "INVALID_PHONE_FORMAT",
                    "message": (
                        "Formato de telefone inválido. "
                        "Use apenas números com DDD."
                    ),
                    "details": {"telefone": value}
                }
            })
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
        raise serializers.ValidationError(str(e))


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
                    "Este e-mail já está sendo usado por outro usuário."
                )
        else:  # Criação
            if UsuarioCustom.objects.filter(
                email=validated_email
            ).exists():
                raise serializers.ValidationError(
                    "Este e-mail já está cadastrado no sistema."
                )

        return validated_email
    except serializers.ValidationError:
        # Re-raise validation errors from validar_email
        raise
    except Exception as e:
        raise serializers.ValidationError(f"Erro ao validar e-mail: {str(e)}")


def validate_telefone_format(value):
    """Valida formato do telefone"""
    if value:  # Só valida se foi fornecido
        try:
            return validar_telefone(value)
        except serializers.ValidationError:
            # Re-raise validation errors from validar_telefone
            raise
        except Exception as e:
            raise serializers.ValidationError(
                f"Erro ao validar telefone: {str(e)}"
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
            "Data de nascimento muito antiga (máximo 120 anos)."
        )

    if value > idade_minima:
        raise serializers.ValidationError(
            "Usuário deve ter pelo menos 16 anos para se cadastrar."
        )

    return value


def validate_password_strength(value):
    """Valida senha básica (se fornecida)"""
    # Se senha foi fornecida, faz validação básica
    if value and len(value) < 8:
        raise serializers.ValidationError(
            "A senha deve ter pelo menos 8 caracteres para maior segurança."
        )
    return value


def validate_password_confirmation(password, password_confirm):
    """Valida confirmação de senha"""
    if password and password_confirm:
        if password != password_confirm:
            raise serializers.ValidationError({
                'password_confirm': (
                    'As senhas não coincidem. '
                    'Verifique se foram digitadas corretamente.'
                )
            })
    elif (password and password_confirm is not None
          and not password_confirm):
        raise serializers.ValidationError({
            'password_confirm': (
                'Confirmação de senha é obrigatória quando '
                'uma senha é fornecida.'
            )
        })


def set_default_password_as_matricula(attrs):
    """Define senha padrão como matrícula se não fornecida"""
    if not attrs.get('password'):
        # Gera matrícula temporária se não estiver disponível
        matricula = getattr(attrs, 'matricula', None)
        if not matricula:
            # Se não há matrícula, usa um padrão temporário
            attrs['password'] = 'temp123456'
        else:
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
