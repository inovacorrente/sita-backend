"""
Validadores customizados para os serializers de condutores.
Contém todas as validações específicas de CNH e dados de condutores.
"""

from datetime import date

from rest_framework import serializers

from app_usuarios.models import UsuarioCustom

# ============================================================================
# VALIDADORES DE CAMPO ESPECÍFICOS PARA CONDUTORES
# ============================================================================


def validar_categoria_cnh(value):
    """
    Valida se a categoria da CNH é válida conforme padrões brasileiros.

    Args:
        value (str): Categoria da CNH a ser validada

    Returns:
        str: Categoria em maiúsculo se válida

    Raises:
        ValidationError: Se a categoria for inválida
    """
    if not value:
        raise serializers.ValidationError(
            "Categoria da CNH é obrigatória."
        )

    # Converte para maiúsculo e remove espaços
    categoria = value.upper().strip()

    # Categorias válidas conforme legislação brasileira
    categorias_validas = ['A', 'B', 'C', 'D', 'E', 'AD', 'AB', 'AC', 'AE']

    if categoria not in categorias_validas:
        categorias_texto = ', '.join(categorias_validas)
        raise serializers.ValidationError(
            f"Categoria CNH inválida. Categorias válidas: {categorias_texto}"
        )

    return categoria


def validar_data_emissao_cnh(value):
    """
    Valida se a data de emissão da CNH é válida.

    Args:
        value (date): Data de emissão da CNH

    Returns:
        date: Data de emissão validada

    Raises:
        ValidationError: Se a data for inválida
    """
    if not value:
        raise serializers.ValidationError(
            "Data de emissão da CNH é obrigatória."
        )

    # Verifica se a data não é futura
    if value > date.today():
        raise serializers.ValidationError(
            "Data de emissão da CNH não pode ser futura."
        )

    # Verifica se a data não é muito antiga (CNH criada há mais de 50 anos)
    data_limite = date.today().replace(year=date.today().year - 50)
    if value < data_limite:
        raise serializers.ValidationError(
            "Data de emissão muito antiga. Verifique a data informada."
        )

    return value


def validar_data_validade_cnh(value):
    """
    Valida se a data de validade da CNH é válida.

    Args:
        value (date): Data de validade da CNH

    Returns:
        date: Data de validade validada

    Raises:
        ValidationError: Se a CNH estiver vencida
    """
    if not value:
        raise serializers.ValidationError(
            "Data de validade da CNH é obrigatória."
        )

    # Verifica se a CNH não está vencida
    if value < date.today():
        raise serializers.ValidationError(
            "CNH está vencida. É necessário renovar antes do cadastro."
        )

    return value


def validar_consistencia_datas_cnh(data_emissao, data_validade):
    """
    Valida se as datas de emissão e validade da CNH são consistentes.

    Args:
        data_emissao (date): Data de emissão da CNH
        data_validade (date): Data de validade da CNH

    Raises:
        ValidationError: Se as datas forem inconsistentes
    """
    if data_emissao and data_validade:
        if data_emissao >= data_validade:
            raise serializers.ValidationError({
                'data_validade_cnh': (
                    'Data de validade deve ser posterior à data de emissão.'
                )
            })


def validar_matricula_usuario(value):
    """
    Valida se a matrícula do usuário existe e pode ser condutor.

    Args:
        value (str): Matrícula do usuário

    Returns:
        str: Matrícula validada

    Raises:
        ValidationError: Se a matrícula for inválida ou usuário já for condutor
    """
    if not value:
        raise serializers.ValidationError(
            "Matrícula do usuário é obrigatória."
        )

    # Remove espaços e converte para maiúsculo
    matricula = value.strip().upper()

    # Verifica se o usuário existe
    try:
        usuario = UsuarioCustom.objects.get(matricula=matricula)
    except UsuarioCustom.DoesNotExist:
        raise serializers.ValidationError(
            "Usuário com esta matrícula não foi encontrado."
        )

    # Verifica se o usuário já é um condutor
    if hasattr(usuario, 'condutor'):
        raise serializers.ValidationError(
            "Este usuário já está cadastrado como condutor."
        )

    return matricula


# ============================================================================
# VALIDADORES COMPOSTOS
# ============================================================================


def validar_dados_cnh_completos(data):
    """
    Valida todos os dados da CNH em conjunto.

    Args:
        data (dict): Dicionário com dados da CNH

    Returns:
        dict: Dados validados

    Raises:
        ValidationError: Se houver inconsistências nos dados
    """
    categoria = data.get('categoria_cnh')
    data_emissao = data.get('data_emissao_cnh')
    data_validade = data.get('data_validade_cnh')

    # Valida campos individuais
    if categoria:
        validar_categoria_cnh(categoria)

    if data_emissao:
        validar_data_emissao_cnh(data_emissao)

    if data_validade:
        validar_data_validade_cnh(data_validade)

    # Valida consistência entre datas
    validar_consistencia_datas_cnh(data_emissao, data_validade)

    return data


def validar_condutor_update(instance, data):
    """
    Valida atualização de dados do condutor.

    Args:
        instance: Instância atual do condutor
        data (dict): Novos dados para atualização

    Returns:
        dict: Dados validados para atualização
    """
    # Pega dados atuais se não fornecidos na atualização
    data_emissao = data.get('data_emissao_cnh', instance.data_emissao_cnh)
    data_validade = data.get('data_validade_cnh', instance.data_validade_cnh)

    # Valida consistência das datas
    validar_consistencia_datas_cnh(data_emissao, data_validade)

    return data
