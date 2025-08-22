import os


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
                'expires_in': int(os.environ.get(
                    'ACCESS_TOKEN_EXPIRES_IN', 3600
                ))
            }
        }


class ValidationErrorResponse:
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

    @staticmethod
    def erro_interno(mensagem_ou_dict=None):
        """Resposta para erro interno do servidor."""
        if mensagem_ou_dict is None:
            mensagem = "Erro interno do servidor"
        elif isinstance(mensagem_ou_dict, dict):
            mensagem = mensagem_ou_dict.get(
                'detail', 'Erro interno do servidor'
            )
        else:
            mensagem = str(mensagem_ou_dict)

        return {
            'success': False,
            'status_code': 500,
            'message': "Erro interno do servidor.",
            'errors': {
                'servidor': (
                    "Ocorreu um erro interno. Tente novamente mais tarde."
                )
            },
            'details': mensagem
        }
