"""
Exceções e respostas específicas para o app de veículos do sistema SITA.
Inclui classes utilitárias para respostas padronizadas e exceções customizadas.
"""
from rest_framework.exceptions import ValidationError as DRFValidationError

from utils.commons.exceptions import SuccessResponse, ValidationErrorResponse


class VeiculoSuccessResponse(SuccessResponse):
    """
    Classe específica para respostas de sucesso relacionadas a veículos.
    Estende a classe base com mensagens contextualizadas.
    """

    @staticmethod
    def veiculo_created(data, tipo_veiculo="veículo"):
        """Resposta para criação bem-sucedida de veículo."""
        return SuccessResponse.created(
            data=data,
            message=f"{tipo_veiculo.capitalize()} cadastrado com sucesso."
        )

    @staticmethod
    def veiculo_updated(data, tipo_veiculo="veículo"):
        """Resposta para atualização bem-sucedida de veículo."""
        return SuccessResponse.updated(
            data=data,
            message=f"{tipo_veiculo.capitalize()} atualizado com sucesso."
        )

    @staticmethod
    def veiculo_retrieved(data, tipo_veiculo="veículo"):
        """Resposta para recuperação bem-sucedida de veículo."""
        return SuccessResponse.retrieved(
            data=data,
            message=f"Dados do {tipo_veiculo} recuperados com sucesso."
        )

    @staticmethod
    def veiculo_deleted(tipo_veiculo="veículo"):
        """Resposta para remoção bem-sucedida de veículo."""
        return SuccessResponse.deleted(
            message=f"{tipo_veiculo.capitalize()} removido com sucesso."
        )

    @staticmethod
    def veiculo_transferido(data):
        """Resposta para transferência bem-sucedida de veículo."""
        return {
            'success': True,
            'status_code': 200,
            'message': "Veículo transferido com sucesso.",
            'data': data
        }

    @staticmethod
    def veiculos_listados(data, count=None):
        """Resposta para listagem de veículos."""
        message = "Veículos listados com sucesso."
        if count is not None:
            message = f"{count} veículo(s) encontrado(s)."

        return SuccessResponse.retrieved(
            data=data,
            message=message
        )


class VeiculoValidationErrorResponse(ValidationErrorResponse):
    """
    Classe específica para respostas de erro de validação de veículos.
    Estende a classe base com mensagens contextualizadas.
    """

    @staticmethod
    def placa_invalida(placa_informada):
        """Resposta para placa inválida."""
        return {
            'success': False,
            'status_code': 400,
            'message': "Placa do veículo inválida.",
            'errors': {
                'placa': (
                    "A placa deve seguir o padrão brasileiro: "
                    "AAA-9999 (antigo) ou AAA9A99 (Mercosul)"
                )
            },
            'details': f"Placa informada: '{placa_informada}'"
        }

    @staticmethod
    def renavam_invalido(renavam_informado):
        """Resposta para RENAVAM inválido."""
        return {
            'success': False,
            'status_code': 400,
            'message': "RENAVAM do veículo inválido.",
            'errors': {
                'renavam': (
                    "O RENAVAM deve conter exatamente 11 dígitos "
                    "com dígito verificador válido"
                )
            },
            'details': f"RENAVAM informado: '{renavam_informado}'"
        }

    @staticmethod
    def chassi_invalido(chassi_informado):
        """Resposta para chassi inválido."""
        return {
            'success': False,
            'status_code': 400,
            'message': "Chassi do veículo inválido.",
            'errors': {
                'chassi': (
                    "O chassi deve conter exatamente 17 caracteres "
                    "alfanuméricos, excluindo I, O e Q"
                )
            },
            'details': f"Chassi informado: '{chassi_informado}'"
        }

    @staticmethod
    def veiculo_duplicado(campo, valor):
        """Resposta para veículo com dados duplicados."""
        return {
            'success': False,
            'status_code': 400,
            'message': f"Já existe um veículo com este {campo}.",
            'errors': {
                campo: f"Este {campo} já está cadastrado no sistema"
            },
            'details': f"{campo.capitalize()} informado: '{valor}'"
        }

    @staticmethod
    def veiculo_nao_encontrado(identificador):
        """Resposta para veículo não encontrado."""
        return {
            'success': False,
            'status_code': 404,
            'message': "Veículo não encontrado.",
            'errors': {
                'identificador': (
                    "Nenhum veículo encontrado com este identificador"
                )
            },
            'details': f"Identificador informado: '{identificador}'"
        }

    @staticmethod
    def usuario_nao_encontrado_para_veiculo(matricula):
        """Resposta para usuário não encontrado para veículo."""
        return {
            'success': False,
            'status_code': 404,
            'message': "Usuário proprietário não encontrado.",
            'errors': {
                'matricula_usuario': (
                    "Nenhum usuário encontrado com esta matrícula"
                )
            },
            'details': f"Matrícula informada: '{matricula}'"
        }

    @staticmethod
    def usuario_inativo_para_veiculo(matricula):
        """Resposta para usuário inativo para veículo."""
        return {
            'success': False,
            'status_code': 400,
            'message': "Usuário proprietário está inativo.",
            'errors': {
                'matricula_usuario': (
                    "O usuário com esta matrícula está inativo no sistema"
                )
            },
            'details': (
                f"Matrícula: '{matricula}'. "
                "Entre em contato com o administrador."
            )
        }

    @staticmethod
    def ano_fabricacao_invalido(ano_informado):
        """Resposta para ano de fabricação inválido."""
        return {
            'success': False,
            'status_code': 400,
            'message': "Ano de fabricação inválido.",
            'errors': {
                'anoFabricacao': (
                    "O ano de fabricação deve estar entre 1900 e o ano atual"
                )
            },
            'details': f"Ano informado: {ano_informado}"
        }

    @staticmethod
    def anos_inconsistentes(ano_fabricacao, ano_limite):
        """Resposta para anos de fabricação inconsistentes."""
        return {
            'success': False,
            'status_code': 400,
            'message': "Anos de fabricação inconsistentes.",
            'errors': {
                'anoLimiteFabricacao': (
                    "O ano limite não pode ser anterior ao ano de fabricação"
                )
            },
            'details': (
                f"Ano de fabricação: {ano_fabricacao}, "
                f"Ano limite: {ano_limite}"
            )
        }

    @staticmethod
    def capacidade_invalida(capacidade_informada):
        """Resposta para capacidade inválida."""
        return {
            'success': False,
            'status_code': 400,
            'message': "Capacidade de passageiros inválida.",
            'errors': {
                'capacidade': (
                    "A capacidade deve ser um número inteiro "
                    "entre 1 e 200 passageiros"
                )
            },
            'details': f"Capacidade informada: {capacidade_informada}"
        }

    @staticmethod
    def linha_invalida(linha_informada):
        """Resposta para linha/rota inválida."""
        return {
            'success': False,
            'status_code': 400,
            'message': "Linha/rota do transporte inválida.",
            'errors': {
                'linha': (
                    "A linha/rota não pode estar vazia e deve ter "
                    "no máximo 50 caracteres"
                )
            },
            'details': f"Linha informada: '{linha_informada}'"
        }


class VeiculoException(Exception):
    """
    Exceção base para erros relacionados a veículos.
    Permite criar exceções específicas do domínio de veículos.
    """

    def __init__(self, message, error_code=None, details=None):
        self.message = message
        self.error_code = error_code
        self.details = details
        super().__init__(self.message)


class VeiculoDuplicadoException(VeiculoException):
    """
    Exceção para tentativa de cadastro de veículo com dados duplicados.
    """

    def __init__(self, campo, valor):
        message = f"Já existe um veículo com este {campo}: {valor}"
        super().__init__(
            message=message,
            error_code="VEICULO_DUPLICADO",
            details={'campo': campo, 'valor': valor}
        )


class VeiculoNaoEncontradoException(VeiculoException):
    """
    Exceção para veículo não encontrado.
    """

    def __init__(self, identificador):
        message = f"Veículo não encontrado: {identificador}"
        super().__init__(
            message=message,
            error_code="VEICULO_NAO_ENCONTRADO",
            details={'identificador': identificador}
        )


class UsuarioVeiculoException(VeiculoException):
    """
    Exceção para problemas relacionados ao usuário proprietário do veículo.
    """

    def __init__(self, matricula, motivo="Usuário inválido"):
        message = f"Problema com usuário proprietário {matricula}: {motivo}"
        super().__init__(
            message=message,
            error_code="USUARIO_VEICULO_INVALIDO",
            details={'matricula': matricula, 'motivo': motivo}
        )


def handle_veiculo_validation_error(validation_error):
    """
    Manipula erros de validação específicos de veículos.

    Args:
        validation_error: Exceção de validação do Django/DRF

    Returns:
        dict: Resposta de erro formatada
    """
    if hasattr(validation_error, 'error_dict'):
        # Erro de validação do Django
        errors = validation_error.error_dict
    elif hasattr(validation_error, 'detail'):
        # Erro de validação do DRF
        errors = validation_error.detail
    else:
        # Erro genérico
        errors = {'non_field_errors': [str(validation_error)]}

    # Formata os erros específicos de veículos
    formatted_errors = {}
    for field, field_errors in errors.items():
        if isinstance(field_errors, list):
            formatted_errors[field] = field_errors[0]
        else:
            formatted_errors[field] = str(field_errors)

    return {
        'success': False,
        'status_code': 400,
        'message': "Erro de validação nos dados do veículo.",
        'errors': formatted_errors,
        'details': "Verifique os dados informados e tente novamente."
    }


def raise_veiculo_validation_error(field, message, code=None):
    """
    Levanta uma exceção de validação específica para veículos.

    Args:
        field: Campo que gerou o erro
        message: Mensagem de erro
        code: Código do erro (opcional)
    """
    raise DRFValidationError({field: message}, code=code)
