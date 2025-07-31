"""
Tratamento customizado de exceções e formatação de respostas de erro da API.
Padroniza as mensagens de erro em formato JSON para melhor consumo.
"""

from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    """
    Manipulador customizado de exceções para padronizar respostas de erro.
    """
    # Chama o manipulador padrão do DRF primeiro
    response = exception_handler(exc, context)

    if response is not None:
        custom_response_data = format_error_response(
            response.data, response.status_code
        )
        response.data = custom_response_data

    return response


def format_error_response(errors, status_code):
    """
    Formata os erros em um padrão consistente para a API.

    Args:
        errors: Dados de erro do DRF
        status_code: Código de status HTTP

    Returns:
        dict: Resposta formatada padronizada
    """
    # Estrutura base da resposta de erro
    error_response = {
        'success': False,
        'status_code': status_code,
        'message': get_error_message(status_code),
        'errors': {},
        'details': None
    }

    # Processa diferentes tipos de erro
    if isinstance(errors, dict):
        # Erros de validação de campos
        for field, field_errors in errors.items():
            if field == 'non_field_errors':
                error_response['details'] = (
                    field_errors[0] if field_errors else None
                )
            else:
                # Converte lista de erros em string única
                if isinstance(field_errors, list):
                    error_response['errors'][field] = (
                        field_errors[0] if field_errors
                        else "Campo inválido."
                    )
                else:
                    error_response['errors'][field] = str(field_errors)
    elif isinstance(errors, list):
        # Erros gerais (lista)
        error_response['details'] = (
            errors[0] if errors else "Erro de validação."
        )
    else:
        # Erro como string
        error_response['details'] = str(errors)

    return error_response


def get_error_message(status_code):
    """
    Retorna mensagem de erro amigável baseada no código de status.

    Args:
        status_code: Código de status HTTP

    Returns:
        str: Mensagem de erro padronizada
    """
    error_messages = {
        400: "Dados inválidos fornecidos.",
        401: "Credenciais de autenticação não fornecidas ou inválidas.",
        403: "Você não tem permissão para executar esta ação.",
        404: "Recurso não encontrado.",
        405: "Método não permitido para este endpoint.",
        409: "Conflito: o recurso já existe ou não pode ser processado.",
        422: "Dados não processáveis.",
        429: "Muitas tentativas. Tente novamente mais tarde.",
        500: "Erro interno do servidor.",
    }

    return error_messages.get(status_code, "Erro não especificado.")


class ValidationErrorResponse:
    """
    Classe utilitária para gerar respostas de erro padronizadas.
    """

    @staticmethod
    def cpf_invalid():
        """Resposta para CPF inválido"""
        return {
            'success': False,
            'status_code': 400,
            'message': "CPF inválido.",
            'errors': {
                'cpf': (
                    "O CPF fornecido não é válido. "
                    "Verifique os dígitos e tente novamente."
                )
            },
            'details': "O CPF deve conter 11 dígitos numéricos válidos."
        }

    @staticmethod
    def cpf_already_exists():
        """Resposta para CPF já cadastrado"""
        return {
            'success': False,
            'status_code': 409,
            'message': "CPF já está em uso.",
            'errors': {
                'cpf': "Este CPF já está cadastrado no sistema."
            },
            'details': "Cada CPF pode ser usado apenas uma vez no sistema."
        }

    @staticmethod
    def email_invalid():
        """Resposta para e-mail inválido"""
        return {
            'success': False,
            'status_code': 400,
            'message': "E-mail inválido.",
            'errors': {
                'email': "O formato do e-mail não é válido."
            },
            'details': "Forneça um e-mail no formato: exemplo@dominio.com"
        }

    @staticmethod
    def email_already_exists():
        """Resposta para e-mail já cadastrado"""
        return {
            'success': False,
            'status_code': 409,
            'message': "E-mail já está em uso.",
            'errors': {
                'email': "Este e-mail já está cadastrado no sistema."
            },
            'details': "Cada e-mail pode ser usado apenas uma vez no sistema."
        }

    @staticmethod
    def telefone_invalid():
        """Resposta para telefone inválido"""
        return {
            'success': False,
            'status_code': 400,
            'message': "Telefone inválido.",
            'errors': {
                'telefone': "O formato do telefone não é válido."
            },
            'details': (
                "O telefone deve ter 10-11 dígitos com DDD. "
                "Ex: (11) 99999-9999"
            )
        }

    @staticmethod
    def password_mismatch():
        """Resposta para senhas não coincidentes"""
        return {
            'success': False,
            'status_code': 400,
            'message': "Senhas não coincidem.",
            'errors': {
                'password_confirm': (
                    "A confirmação da senha não confere "
                    "com a senha informada."
                )
            },
            'details': "Verifique se as senhas foram digitadas corretamente."
        }

    @staticmethod
    def password_too_weak():
        """Resposta para senha muito fraca"""
        return {
            'success': False,
            'status_code': 400,
            'message': "Senha muito fraca.",
            'errors': {
                'password': "A senha deve ter pelo menos 8 caracteres."
            },
            'details': (
                "Use uma combinação de letras, números e símbolos "
                "para maior segurança."
            )
        }

    @staticmethod
    def age_invalid():
        """Resposta para idade inválida"""
        return {
            'success': False,
            'status_code': 400,
            'message': "Data de nascimento inválida.",
            'errors': {
                'data_nascimento': "A idade deve estar entre 16 e 120 anos."
            },
            'details': "Verifique se a data de nascimento está correta."
        }

    @staticmethod
    def future_date():
        """Resposta para data no futuro"""
        return {
            'success': False,
            'status_code': 400,
            'message': "Data inválida.",
            'errors': {
                'data_nascimento': (
                    "A data de nascimento não pode ser no futuro."
                )
            },
            'details': "Forneça uma data de nascimento válida."
        }

    @staticmethod
    def login_invalid():
        """Resposta para credenciais inválidas"""
        return {
            'success': False,
            'status_code': 401,
            'message': "Credenciais inválidas.",
            'errors': {
                'non_field_errors': "Matrícula ou senha incorretos."
            },
            'details': "Verifique sua matrícula e senha e tente novamente."
        }

    @staticmethod
    def permission_denied():
        """Resposta para acesso negado"""
        return {
            'success': False,
            'status_code': 403,
            'message': "Acesso negado.",
            'errors': {
                'permission': "Você não tem permissão para executar esta ação."
            },
            'details': (
                "Entre em contato com o administrador se precisar "
                "de mais permissões."
            )
        }

    @staticmethod
    def user_not_found():
        """Resposta para usuário não encontrado"""
        return {
            'success': False,
            'status_code': 404,
            'message': "Usuário não encontrado.",
            'errors': {
                'matricula': "Nenhum usuário encontrado com esta matrícula."
            },
            'details': "Verifique se a matrícula está correta."
        }

    @staticmethod
    def required_field(field_name):
        """Resposta para campo obrigatório não preenchido"""
        return {
            'success': False,
            'status_code': 400,
            'message': f"Campo {field_name} é obrigatório.",
            'errors': {
                field_name: "Este campo é obrigatório e não pode estar vazio."
            },
            'details': f"Forneça um valor válido para o campo {field_name}."
        }


class SuccessResponse:
    """
    Classe utilitária para gerar respostas de sucesso padronizadas.
    """

    @staticmethod
    def created(data, message="Recurso criado com sucesso."):
        """Resposta para criação bem-sucedida"""
        return {
            'success': True,
            'status_code': 201,
            'message': message,
            'data': data
        }

    @staticmethod
    def updated(data, message="Recurso atualizado com sucesso."):
        """Resposta para atualização bem-sucedida"""
        return {
            'success': True,
            'status_code': 200,
            'message': message,
            'data': data
        }

    @staticmethod
    def retrieved(data, message="Dados recuperados com sucesso."):
        """Resposta para recuperação bem-sucedida"""
        return {
            'success': True,
            'status_code': 200,
            'message': message,
            'data': data
        }

    @staticmethod
    def deleted(message="Recurso removido com sucesso."):
        """Resposta para remoção bem-sucedida"""
        return {
            'success': True,
            'status_code': 204,
            'message': message,
            'data': None
        }

    @staticmethod
    def login_success(data):
        """Resposta para login bem-sucedido"""
        return {
            'success': True,
            'status_code': 200,
            'message': "Login realizado com sucesso.",
            'data': {
                'access_token': data.get('access'),
                'refresh_token': data.get('refresh'),
                'token_type': 'Bearer',
                'expires_in': 3600  # 1 hora em segundos
            }
        }
