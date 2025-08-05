"""
Tratamento customizado de exceções específicas para condutores.
Padroniza as mensagens de erro relacionadas a CNH e condutores.
"""

from rest_framework import serializers


class CondutorErrorResponse:
    """
    Classe para gerar respostas de erro padronizadas específicas
    para condutores. Segue o padrão do projeto SITA Backend.
    """

    @staticmethod
    def usuario_nao_encontrado():
        """Resposta para usuário com matrícula não encontrado"""
        return {
            'success': False,
            'status_code': 404,
            'message': "Usuário não encontrado.",
            'errors': {
                'matricula': "Usuário com esta matrícula não foi encontrado."
            },
            'details': "Verifique se a matrícula foi digitada corretamente."
        }

    @staticmethod
    def usuario_ja_condutor():
        """Resposta para usuário que já é condutor"""
        return {
            'success': False,
            'status_code': 409,
            'message': "Usuário já é um condutor.",
            'errors': {
                'matricula': "Este usuário já está cadastrado como condutor."
            },
            'details': (
                "Cada usuário pode ser condutor apenas uma vez no sistema."
            )
        }

    @staticmethod
    def categoria_cnh_invalida():
        """Resposta para categoria de CNH inválida"""
        return {
            'success': False,
            'status_code': 400,
            'message': "Categoria de CNH inválida.",
            'errors': {
                'categoria_cnh': "A categoria informada não é válida."
            },
            'details': (
                "Categorias válidas: A, B, C, D, E, AD, AB, AC, AE. "
                "Verifique a categoria na sua CNH."
            )
        }

    @staticmethod
    def cnh_vencida():
        """Resposta para CNH vencida"""
        return {
            'success': False,
            'status_code': 400,
            'message': "CNH vencida.",
            'errors': {
                'data_validade_cnh': "A CNH está vencida."
            },
            'details': (
                "É necessário renovar a CNH antes de cadastrar "
                "como condutor no sistema."
            )
        }

    @staticmethod
    def data_emissao_futura():
        """Resposta para data de emissão futura"""
        return {
            'success': False,
            'status_code': 400,
            'message': "Data de emissão inválida.",
            'errors': {
                'data_emissao_cnh': "A data de emissão não pode ser futura."
            },
            'details': "Verifique a data de emissão informada na CNH."
        }

    @staticmethod
    def data_validade_invalida():
        """Resposta para data de validade anterior à emissão"""
        return {
            'success': False,
            'status_code': 400,
            'message': "Datas da CNH inconsistentes.",
            'errors': {
                'data_validade_cnh': (
                    "Data de validade deve ser posterior à data de emissão."
                )
            },
            'details': (
                "Verifique as datas informadas. A data de validade "
                "deve ser sempre posterior à data de emissão."
            )
        }

    @staticmethod
    def condutor_nao_encontrado():
        """Resposta para condutor não encontrado"""
        return {
            'success': False,
            'status_code': 404,
            'message': "Condutor não encontrado.",
            'errors': {
                'matricula': "Condutor com esta matricula não foi encontrado."
            },
            'details': "Verifique se a matrícula do condutor está correta."
        }


class CondutorValidationError(serializers.ValidationError):
    """
    Exceção customizada para erros de validação de condutores.
    Permite usar respostas padronizadas do CondutorErrorResponse.
    """

    def __init__(self, error_response_method, *args, **kwargs):
        """
        Inicializa a exceção com resposta padronizada.

        Args:
            error_response_method: Método da classe CondutorErrorResponse
        """
        if callable(error_response_method):
            error_data = error_response_method()
            detail = error_data.get('errors', {})
        else:
            detail = error_response_method

        super().__init__(detail=detail, *args, **kwargs)
