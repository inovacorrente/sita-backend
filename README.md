# SITA - Sistema STRANS

Sistema de gerenciamento de usuários para STRANS, desenvolvido em Django e Django REST Framework.

## Funcionalidades

- Autenticação JWT personalizada (login via matrícula)
- Cadastro de usuários customizados com campos adicionais (CPF, telefone, grupos)
- Geração automática de matrícula para usuários
- Gerenciamento de grupos e permissões
- Documentação automática da API com Swagger (drf-spectacular)

## Instalação

1. Clone o repositório:
   ```sh
   git clone https://github.com/inovacorrente/sita-backend
   cd sita-backend
   ```

2. Crie e ative um ambiente virtual:
   * Linux/MacOS
   ```sh
   python3 -m venv venv
   source venv/bin/activate
   ```
   * Windows
   ```sh
   venv\Scripts\activate
   ```

3. Instale as dependências:
   ```sh
   pip install -r requirements.txt
   ```

4. Configure as variáveis de ambiente:
   - Copie o arquivo `.env-example` para `.env` e ajuste conforme necessário.

5. Execute as migrações:
   ```sh
   python manage.py migrate
   ```

6. Crie os grupos padrão:
   ```sh
   python manage.py criar_grupos
   ```

7. (Opcional) Crie usuários de exemplo:
   ```sh
   python manage.py criar_usuarios
   ```

8. Inicie o servidor:
   ```sh
   python manage.py runserver
   ```

## Endpoints Principais

- Autenticação: `/api/usuarios/login/`
- Documentação Swagger: `/api/docs/`
- Schema OpenAPI: `/api/schema/`

## Variáveis de Ambiente

Veja o arquivo [.env-example](.env-example) para exemplos de configuração.

## Licença

Este projeto está licenciado sob a [GNU GPL v2](LICENSE).