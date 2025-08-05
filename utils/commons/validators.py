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
