"""
Validadores para o app de veículos do sistema SITA.
Inclui validações específicas para dados de veículos brasileiros.
"""
import re
from datetime import datetime

from django.core.exceptions import ValidationError
from rest_framework import serializers

from app_usuarios.models import UsuarioCustom


def normalize_alphanumeric_upper(value: str) -> str:
    """
    Remove espaços nas extremidades e aplica uppercase.

    Args:
        value: String a ser normalizada

    Returns:
        String normalizada em uppercase e sem espaços nas extremidades
    """
    return value.strip().upper() if value is not None else value


def validate_placa_br(value: str) -> str:
    """
    Valida placa brasileira (padrão antigo e Mercosul).

    Padrões aceitos:
    - Antigo: AAA-9999 (3 letras + 4 números)
    - Mercosul: AAA9A99 (3 letras + 1 número + 1 letra + 2 números)

    Args:
        value: Placa a ser validada

    Returns:
        Placa normalizada (uppercase, sem espaços e hífen)

    Raises:
        ValidationError: Se a placa não atender aos padrões brasileiros
    """
    if not value:
        raise ValidationError("Placa não pode ser vazia")

    # Normaliza: remove espaços, hífen e converte para uppercase
    placa_limpa = re.sub(r'[^A-Z0-9]', '', normalize_alphanumeric_upper(value))

    # Padrão antigo: 3 letras + 4 números
    padrao_antigo = re.match(r'^[A-Z]{3}[0-9]{4}$', placa_limpa)

    # Padrão Mercosul: 3 letras + 1 número + 1 letra + 2 números
    padrao_mercosul = re.match(r'^[A-Z]{3}[0-9][A-Z][0-9]{2}$', placa_limpa)

    if not (padrao_antigo or padrao_mercosul):
        raise ValidationError(
            "Placa deve seguir o padrão brasileiro: "
            "AAA-9999 (antigo) ou AAA9A99 (Mercosul)"
        )

    return placa_limpa


def validate_renavam(value: str) -> str:
    """
    Valida RENAVAM brasileiro.

    O RENAVAM deve ter 11 dígitos numéricos e algoritmo de verificação válido.

    Args:
        value: RENAVAM a ser validado

    Returns:
        RENAVAM normalizado (apenas números)

    Raises:
        ValidationError: Se o RENAVAM for inválido
    """
    if not value:
        raise ValidationError("RENAVAM não pode ser vazio")

    # Remove caracteres não numéricos
    renavam_limpo = re.sub(r'[^0-9]', '', str(value))

    if len(renavam_limpo) != 11:
        raise ValidationError("RENAVAM deve conter exatamente 11 dígitos")

    # Valida dígito verificador
    if not _validar_digito_renavam(renavam_limpo):
        raise ValidationError("RENAVAM com dígito verificador inválido")

    return renavam_limpo


def _validar_digito_renavam(renavam: str) -> bool:
    """
    Valida o dígito verificador do RENAVAM.

    Args:
        renavam: RENAVAM com 11 dígitos

    Returns:
        True se o dígito verificador for válido
    """
    # Sequência para cálculo: 3, 2, 9, 8, 7, 6, 5, 4, 3, 2
    sequencia = [3, 2, 9, 8, 7, 6, 5, 4, 3, 2]

    # Calcula a soma dos produtos
    soma = sum(int(renavam[i]) * sequencia[i] for i in range(10))

    # Calcula o dígito verificador
    digito = 11 - (soma % 11)
    if digito >= 10:
        digito = 0

    return digito == int(renavam[10])


def validate_chassi(value: str) -> str:
    """
    Valida número do chassi (VIN - Vehicle Identification Number).

    O chassi deve ter exatamente 17 caracteres alfanuméricos,
    excluindo I, O e Q para evitar confusão.

    Args:
        value: Chassi a ser validado

    Returns:
        Chassi normalizado (uppercase, sem espaços)

    Raises:
        ValidationError: Se o chassi for inválido
    """
    if not value:
        raise ValidationError("Chassi não pode ser vazio")

    # Normaliza e remove espaços
    chassi_limpo = re.sub(
        r'[^A-Z0-9]', '', normalize_alphanumeric_upper(value))

    if len(chassi_limpo) != 17:
        raise ValidationError("Chassi deve conter exatamente 17 caracteres")

    # Verifica caracteres não permitidos (I, O, Q)
    caracteres_proibidos = ['I', 'O', 'Q']
    if any(char in chassi_limpo for char in caracteres_proibidos):
        raise ValidationError(
            "Chassi não pode conter as letras I, O ou Q"
        )

    return chassi_limpo


def validate_ano_fabricacao(value: int) -> int:
    """
    Valida ano de fabricação do veículo.

    Args:
        value: Ano de fabricação

    Returns:
        Ano validado

    Raises:
        ValidationError: Se o ano for inválido
    """
    ano_atual = datetime.now().year
    ano_minimo = 1900  # Primeiro automóvel produzido em massa

    if not isinstance(value, int):
        raise ValidationError("Ano de fabricação deve ser um número inteiro")

    if value < ano_minimo:
        raise ValidationError(
            f"Ano de fabricação não pode ser anterior a {ano_minimo}")

    if value > ano_atual + 1:  # Permite um ano à frente para lançamentos
        raise ValidationError(
            f"Ano de fabricação não pode ser superior a {ano_atual + 1}"
        )

    return value


def validate_ano_limite_fabricacao(value: int) -> int:
    """
    Valida ano limite de fabricação do veículo.

    Args:
        value: Ano limite de fabricação

    Returns:
        Ano validado

    Raises:
        ValidationError: Se o ano for inválido
    """
    return validate_ano_fabricacao(value)  # Mesmas regras


def validate_anos_fabricacao_consistencia(ano_fabricacao: int, ano_limite: int):
    """
    Valida a consistência entre ano de fabricação e ano limite.

    Args:
        ano_fabricacao: Ano de fabricação
        ano_limite: Ano limite de fabricação

    Raises:
        ValidationError: Se os anos forem inconsistentes
    """
    if ano_limite < ano_fabricacao:
        raise ValidationError(
            "Ano limite de fabricação não pode ser anterior ao ano de fabricação"
        )


def validate_capacidade_transporte(value: int) -> int:
    """
    Valida capacidade de passageiros para transporte municipal.

    Args:
        value: Capacidade de passageiros

    Returns:
        Capacidade validada

    Raises:
        ValidationError: Se a capacidade for inválida
    """
    if not isinstance(value, int):
        raise ValidationError("Capacidade deve ser um número inteiro")

    if value <= 0:
        raise ValidationError("Capacidade deve ser maior que zero")

    if value > 200:  # Limite razoável para transporte municipal
        raise ValidationError("Capacidade não pode exceder 200 passageiros")

    return value


def validate_marca_modelo_length(value: str, campo: str) -> str:
    """
    Valida comprimento de marca ou modelo.

    Args:
        value: Valor a ser validado
        campo: Nome do campo ('marca' ou 'modelo')

    Returns:
        Valor normalizado

    Raises:
        ValidationError: Se o valor for inválido
    """
    if not value or not value.strip():
        raise ValidationError(f"{campo.capitalize()} não pode ser vazio")

    value_limpo = value.strip()

    if len(value_limpo) < 2:
        raise ValidationError(
            f"{campo.capitalize()} deve ter pelo menos 2 caracteres")

    if len(value_limpo) > 50:
        raise ValidationError(
            f"{campo.capitalize()} não pode exceder 50 caracteres")

    return value_limpo


def validate_cor_veiculo(value: str) -> str:
    """
    Valida cor do veículo.

    Args:
        value: Cor a ser validada

    Returns:
        Cor normalizada

    Raises:
        ValidationError: Se a cor for inválida
    """
    if not value or not value.strip():
        raise ValidationError("Cor não pode ser vazia")

    cor_limpa = value.strip().title()  # Primeira letra maiúscula

    if len(cor_limpa) < 3:
        raise ValidationError("Cor deve ter pelo menos 3 caracteres")

    if len(cor_limpa) > 30:
        raise ValidationError("Cor não pode exceder 30 caracteres")

    return cor_limpa


def validate_linha_transporte(value: str) -> str:
    """
    Valida linha/rota de transporte municipal.

    Args:
        value: Linha/rota a ser validada

    Returns:
        Linha normalizada

    Raises:
        ValidationError: Se a linha for inválida
    """
    if not value or not value.strip():
        raise ValidationError("Linha/rota não pode ser vazia")

    linha_limpa = value.strip().upper()

    if len(linha_limpa) > 50:
        raise ValidationError("Linha/rota não pode exceder 50 caracteres")

    return linha_limpa


def validate_usuario_exists(matricula: str) -> UsuarioCustom:
    """
    Valida se o usuário existe pela matrícula.

    Args:
        matricula: Matrícula do usuário

    Returns:
        Objeto UsuarioCustom

    Raises:
        ValidationError: Se o usuário não existir ou estiver inativo
    """
    if not matricula:
        raise ValidationError("Matrícula do usuário é obrigatória")

    # Normaliza a matrícula (apenas remove espaços)
    matricula_limpa = matricula.strip()

    try:
        usuario = UsuarioCustom.objects.get(matricula=matricula_limpa)
    except UsuarioCustom.DoesNotExist:
        raise ValidationError(
            f"Usuário com matrícula '{matricula_limpa}' não encontrado"
        )

    if not usuario.is_active:
        raise ValidationError(
            f"Usuário com matrícula '{matricula_limpa}' está inativo"
        )

    return usuario


def validate_veiculo_unique_fields(
    placa: str = None,
    renavam: str = None,
    chassi: str = None,
    instance=None
):
    """
    Valida unicidade dos campos placa, renavam e chassi.

    Args:
        placa: Placa do veículo
        renavam: RENAVAM do veículo
        chassi: Chassi do veículo
        instance: Instância atual (para updates)

    Raises:
        ValidationError: Se algum campo não for único
    """
    from app_veiculos.models import (MotoTaxiVeiculo, TaxiVeiculo,
                                     TransporteMunicipalVeiculo)

    # Lista de todas as classes de veículos
    classes_veiculo = [TaxiVeiculo,
                       MotoTaxiVeiculo, TransporteMunicipalVeiculo]

    erros = {}

    # Verifica placa
    if placa:
        for classe in classes_veiculo:
            query = classe.objects.filter(placa=placa)
            if instance:
                query = query.exclude(pk=instance.pk)
            if query.exists():
                veiculo_existente = query.first()
                erros['placa'] = (
                    f"Esta placa já está cadastrada no veículo "
                    f"{veiculo_existente.identificador_unico_veiculo}"
                )
                break

    # Verifica RENAVAM
    if renavam:
        for classe in classes_veiculo:
            query = classe.objects.filter(renavam=renavam)
            if instance:
                query = query.exclude(pk=instance.pk)
            if query.exists():
                veiculo_existente = query.first()
                erros['renavam'] = (
                    f"Este RENAVAM já está cadastrado no veículo "
                    f"{veiculo_existente.identificador_unico_veiculo}"
                )
                break

    # Verifica chassi
    if chassi:
        for classe in classes_veiculo:
            query = classe.objects.filter(chassi=chassi)
            if instance:
                query = query.exclude(pk=instance.pk)
            if query.exists():
                veiculo_existente = query.first()
                erros['chassi'] = (
                    f"Este chassi já está cadastrado no veículo "
                    f"{veiculo_existente.identificador_unico_veiculo}"
                )
                break

    if erros:
        raise serializers.ValidationError(erros)
