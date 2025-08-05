"""
Tratamento customizado de exceções e formatação de respostas de erro da API.
Padroniza as mensagens de erro em formato JSON para melhor consumo.
"""


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
