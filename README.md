# SITA Backend - Sistema STRANS

<p align="center">
  <img src="https://img.shields.io/badge/Django-5.2.4-green?style=flat-square&logo=django" alt="Django 5.2.4">
  <img src="https://img.shields.io/badge/DRF-3.16.0-red?style=flat-square&logo=django" alt="Django REST Framework">
  <img src="https://img.shields.io/badge/Python-3.8+-blue?style=flat-square&logo=python" alt="Python 3.8+">
  <img src="https://img.shields.io/badge/License-GPL--2.0-yellow?style=flat-square" alt="License GPL-2.0">
  <img src="https://img.shields.io/badge/API-v1.0.0-purple?style=flat-square" alt="API Version">
</p>

Sistema backend completo para gerenciamento de usuários e condutores do **Sistema de Trânsito (SITA)** da STRANS, desenvolvido em Django REST Framework com autenticação JWT, validações brasileiras e documentação automática.

## 🚀 Funcionalidades Principais

### 🔐 Autenticação e Segurança
- **Autenticação JWT**: Login via matrícula com tokens access/refresh
- **Sistema de Senhas Automático**: Senha opcional no cadastro (usa matrícula como padrão)
- **Grupos de Permissões**: Sistema hierárquico com 4 níveis de acesso
- **Validações Brasileiras**: CPF, telefone e dados específicos do Brasil

### 👥 Gestão de Usuários
- **Cadastro Inteligente**: Geração automática de matrícula única
- **CRUD Completo**: Criar, listar, visualizar, editar e ativar/desativar usuários
- **Busca Avançada**: Busca multifield por matrícula, nome, email e CPF
- **Filtros Dinâmicos**: Por status, grupos e permissões
- **Paginação Automática**: Controle de grandes volumes de dados

### 🚗 Gestão de Condutores
- **Registro de CNH**: Categoria, validade e data de emissão
- **Vínculo com Usuários**: Relacionamento one-to-one com usuários
- **API RESTful**: CRUD completo via ViewSets

### 📚 Documentação e API
- **Swagger UI**: Documentação interativa em `/api/docs/`
- **OpenAPI 3.0**: Schema completo em `/api/schema/`
- **Postman Collection**: Collection pronta para testes
- **Respostas Padronizadas**: Formato JSON consistente em toda API

## 🏗️ Arquitetura

### Apps Principais
- **`app_usuarios`**: Gerenciamento de usuários customizados
- **`app_condutores`**: Gestão de condutores e CNH
- **`utils`**: Validadores, permissões e utilitários compartilhados

### Tecnologias Utilizadas
- **Backend**: Django 5.2.4 + Django REST Framework 3.16.0
- **Autenticação**: djangorestframework-simplejwt 5.5.1
- **Documentação**: drf-spectacular 0.28.0
- **Validações**: validator-collection 1.5.0
- **Filtros**: django-filter 25.1
- **CORS**: django-cors-headers 4.7.0

## 📋 Requisitos

- Python 3.8+
- Django 5.2.4
- SQLite (desenvolvimento) / PostgreSQL (produção recomendado)

## ⚡ Instalação Rápida

### 1. Clone e Configure o Ambiente

```bash
# Clone o repositório
git clone https://github.com/inovacorrente/sita-backend.git
cd sita-backend

# Crie e ative o ambiente virtual
python3 -m venv venv

# Linux/macOS
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 2. Instale as Dependências

```bash
pip install -r requirements.txt
```

### 3. Configure as Variáveis de Ambiente

Crie um arquivo `.env` baseado no exemplo:

```env
SECRET_KEY=sua-chave-secreta-muito-segura-aqui
DEBUG=1
ALLOWED_HOSTS=localhost,127.0.0.1
PAGE_SIZE=10
ACCESS_TOKEN_MINUTES=60
REFRESH_TOKEN_DAYS=7
```

### 4. Configure o Banco de Dados

```bash
# Execute as migrações
python manage.py migrate

# Crie os grupos padrão do sistema
python manage.py criar_grupos

# (Opcional) Crie usuários de exemplo para desenvolvimento
python manage.py criar_usuarios
```

### 5. Inicie o Servidor

```bash
python manage.py runserver
```

🎉 **Pronto!** A API estará rodando em `http://localhost:8000`

## 📖 Guia de Uso Rápido

### 🔑 Login e Autenticação

```bash
# Login com usuário de exemplo
curl -X POST http://localhost:8000/api/usuarios/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "matricula": "123456789012",
    "password": "admin123"
  }'
```

**Resposta:**
```json
{
  "success": true,
  "status_code": 200,
  "message": "Login realizado com sucesso.",
  "data": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "token_type": "Bearer",
    "expires_in": 3600
  }
}
```

### 👤 Cadastro de Usuário (Senha Automática)

```bash
# Cadastro sem senha - sistema gerará automaticamente
curl -X POST http://localhost:8000/api/usuarios/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "nome_completo": "João Silva",
    "email": "joao@email.com",
    "cpf": "12345678901",
    "data_nascimento": "1990-01-01",
    "sexo": "M"
  }'
```

> 💡 **Dica**: Se não fornecer senha, o sistema usará a matrícula gerada como senha padrão!

### 🔍 Busca Avançada

```bash
# Buscar usuários por nome
curl -X GET "http://localhost:8000/api/usuarios/listar/?search=João" \
  -H "Authorization: Bearer <seu_token>"

# Filtrar usuários ativos que são administradores
curl -X GET "http://localhost:8000/api/usuarios/listar/?is_active=true&is_staff=true" \
  -H "Authorization: Bearer <seu_token>"
```

## 🎯 Endpoints Principais

| Método                | Endpoint                                      | Descrição                | Auth |
| --------------------- | --------------------------------------------- | ------------------------ | ---- |
| `POST`                | `/api/usuarios/login/`                        | Login com matrícula      | ❌    |
| `POST`                | `/api/usuarios/register/`                     | Cadastro de usuário      | ⚠️*   |
| `GET`                 | `/api/usuarios/listar/`                       | Listar com filtros       | ✅    |
| `GET`                 | `/api/usuarios/me/`                           | Próprios dados           | ✅    |
| `PATCH`               | `/api/usuarios/me/`                           | Atualizar próprios dados | ✅    |
| `GET`                 | `/api/usuarios/<matricula>/`                  | Ver usuário específico   | ✅    |
| `PATCH`               | `/api/usuarios/<matricula>/editar/`           | Editar usuário           | ✅    |
| `PATCH`               | `/api/usuarios/ativar-desativar/<matricula>/` | Toggle status            | ✅    |
| `GET/POST/PUT/DELETE` | `/api/condutores/condutores/`                 | CRUD de condutores       | ✅    |

*⚠️ Requer autenticação apenas para criar administradores*

## 📋 Exemplos Completos dos Endpoints

### 🔐 1. Autenticação - Login

**Endpoint:** `POST /api/usuarios/login/`

**Descrição:** Autentica usuário e retorna tokens JWT

**Corpo da Requisição:**
```json
{
  "matricula": "123456789012",
  "password": "admin123"
}
```

**Exemplo com cURL:**
```bash
curl -X POST http://localhost:8000/api/usuarios/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "matricula": "123456789012",
    "password": "admin123"
  }'
```

**Resposta de Sucesso (200):**
```json
{
  "success": true,
  "status_code": 200,
  "message": "Login realizado com sucesso.",
  "data": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzM5MzQ2MDAwfQ...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTczOTQzMjQwMH0...",
    "token_type": "Bearer",
    "expires_in": 3600
  }
}
```

**Resposta de Erro (401):**
```json
{
  "success": false,
  "status_code": 401,
  "message": "Credenciais inválidas.",
  "errors": {
    "non_field_errors": "Matrícula ou senha incorretos."
  },
  "details": "Verifique sua matrícula e senha e tente novamente."
}
```

---

### 👤 2. Usuários - Cadastro

**Endpoint:** `POST /api/usuarios/register/`

**Descrição:** Cria novo usuário (senha opcional - usa matrícula como padrão)

**Corpo da Requisição (Usuário Comum):**
```json
{
  "nome_completo": "João Silva Santos",
  "email": "joao.silva@email.com",
  "cpf": "12345678901",
  "data_nascimento": "1990-05-15",
  "sexo": "M",
  "telefone": "85987654321"
}
```

**Corpo da Requisição (Com Senha Personalizada):**
```json
{
  "nome_completo": "Maria Santos",
  "email": "maria.santos@email.com",
  "cpf": "98765432100",
  "password": "minhasenha123",
  "data_nascimento": "1985-06-15",
  "sexo": "F",
  "telefone": "85999887766",
  "groups": [1, 2]
}
```

**Corpo da Requisição (Administrador - requer auth):**
```json
{
  "nome_completo": "Admin Sistema",
  "email": "admin@sistema.com",
  "cpf": "11122233344",
  "password": "senhaadmin123",
  "data_nascimento": "1980-01-01",
  "sexo": "M",
  "is_staff": true,
  "is_superuser": true
}
```

**Resposta de Sucesso (201):**
```json
{
  "nome_completo": "João Silva Santos",
  "email": "joao.silva@email.com",
  "matricula": "202590125123",
  "cpf": "12345678901",
  "telefone": "85987654321",
  "data_nascimento": "1990-05-15",
  "sexo": "M",
  "is_active": true,
  "is_staff": false,
  "is_superuser": false,
  "groups": []
}
```

**Resposta de Erro - CPF Inválido (400):**
```json
{
  "success": false,
  "status_code": 400,
  "message": "CPF inválido.",
  "errors": {
    "cpf": "O CPF fornecido não é válido. Verifique os dígitos e tente novamente."
  },
  "details": "O CPF deve conter 11 dígitos numéricos válidos."
}
```

**Resposta de Erro - Email Já Existe (409):**
```json
{
  "success": false,
  "status_code": 409,
  "message": "E-mail já está em uso.",
  "errors": {
    "email": "Este e-mail já está cadastrado no sistema."
  },
  "details": "Cada e-mail pode ser usado apenas uma vez no sistema."
}
```

---

### 📋 3. Usuários - Listar com Filtros

**Endpoint:** `GET /api/usuarios/listar/`

**Descrição:** Lista usuários com busca e filtros avançados

**Parâmetros de Query:**
- `search`: Busca por matrícula, nome, email ou CPF
- `is_active`: Filtrar por status ativo/inativo
- `is_staff`: Filtrar por administradores
- `is_superuser`: Filtrar por superusuários
- `page`: Número da página
- `page_size`: Itens por página

**Exemplos de Requisições:**
```bash
# Busca simples
GET /api/usuarios/listar/?search=João

# Filtros combinados
GET /api/usuarios/listar/?is_active=true&is_staff=false&page=1

# Busca por CPF
GET /api/usuarios/listar/?search=12345678901

# Apenas administradores ativos
GET /api/usuarios/listar/?is_staff=true&is_active=true
```

**Resposta de Sucesso (200):**
```json
{
  "count": 25,
  "next": "http://localhost:8000/api/usuarios/listar/?page=2",
  "previous": null,
  "results": [
    {
      "nome_completo": "João Silva Santos",
      "email": "joao.silva@email.com",
      "matricula": "202590125123",
      "cpf": "12345678901",
      "telefone": "85987654321",
      "data_nascimento": "1990-05-15",
      "sexo": "M",
      "is_active": true,
      "is_staff": false,
      "is_superuser": false,
      "groups": []
    },
    {
      "nome_completo": "Maria Santos",
      "email": "maria.santos@email.com",
      "matricula": "202510025456",
      "cpf": "98765432100",
      "telefone": "85999887766",
      "data_nascimento": "1985-06-15",
      "sexo": "F",
      "is_active": true,
      "is_staff": false,
      "is_superuser": false,
      "groups": [1]
    }
  ]
}
```

---

### 👁️ 4. Usuários - Ver Próprios Dados

**Endpoint:** `GET /api/usuarios/me/`

**Descrição:** Retorna dados do usuário autenticado

**Headers Obrigatórios:**
```
Authorization: Bearer <access_token>
```

**Resposta de Sucesso (200):**
```json
{
  "success": true,
  "status_code": 200,
  "message": "Dados do usuário recuperados com sucesso.",
  "data": {
    "nome_completo": "João Silva Santos",
    "email": "joao.silva@email.com",
    "matricula": "202590125123",
    "cpf": "12345678901",
    "telefone": "85987654321",
    "data_nascimento": "1990-05-15",
    "sexo": "M"
  }
}
```

---

### ✏️ 5. Usuários - Atualizar Próprios Dados

**Endpoint:** `PATCH /api/usuarios/me/`

**Descrição:** Permite ao usuário atualizar seus próprios dados

**Corpo da Requisição:**
```json
{
  "telefone": "85999888777",
  "email": "novo.email@email.com"
}
```

**Resposta de Sucesso (200):**
```json
{
  "success": true,
  "status_code": 200,
  "message": "Dados atualizados com sucesso.",
  "data": {
    "nome_completo": "João Silva Santos",
    "email": "novo.email@email.com",
    "matricula": "202590125123",
    "cpf": "12345678901",
    "telefone": "85999888777",
    "data_nascimento": "1990-05-15",
    "sexo": "M"
  }
}
```

---

### 👥 6. Usuários - Ver Usuário Específico

**Endpoint:** `GET /api/usuarios/<matricula>/`

**Descrição:** Visualiza dados de usuário específico (próprios dados ou admin)

**Exemplo:** `GET /api/usuarios/202590125123/`

**Resposta de Sucesso (200):**
```json
{
  "nome_completo": "João Silva Santos",
  "email": "joao.silva@email.com",
  "matricula": "202590125123",
  "cpf": "12345678901",
  "telefone": "85987654321",
  "data_nascimento": "1990-05-15",
  "sexo": "M",
  "is_active": true,
  "is_staff": false,
  "is_superuser": false,
  "groups": []
}
```

**Resposta de Erro - Sem Permissão (403):**
```json
{
  "success": false,
  "status_code": 403,
  "message": "Acesso negado.",
  "errors": {
    "permission": "Você não tem permissão para executar esta ação."
  },
  "details": "Entre em contato com o administrador se precisar de mais permissões."
}
```

---

### 📝 7. Usuários - Editar Usuário (Admin)

**Endpoint:** `PATCH /api/usuarios/<matricula>/editar/`

**Descrição:** Atualiza dados de qualquer usuário (apenas admins)

**Exemplo:** `PATCH /api/usuarios/202590125123/editar/`

**Corpo da Requisição:**
```json
{
  "telefone": "85999888777",
  "is_active": false,
  "groups": [1, 2]
}
```

**Resposta de Sucesso (200):**
```json
{
  "nome_completo": "João Silva Santos",
  "email": "joao.silva@email.com",
  "cpf": "12345678901",
  "telefone": "85999888777",
  "data_nascimento": "1990-05-15",
  "sexo": "M",
  "is_active": false,
  "is_staff": false,
  "is_superuser": false,
  "groups": [1, 2]
}
```

---

### 🔄 8. Usuários - Ativar/Desativar (Toggle)

**Endpoint:** `PATCH /api/usuarios/ativar-desativar/<matricula>/`

**Descrição:** Alterna automaticamente o status is_active do usuário

**Exemplo:** `PATCH /api/usuarios/ativar-desativar/202590125123/`

**Corpo da Requisição:** Nenhum (vazio)

**Resposta de Sucesso - Usuário Ativado (200):**
```json
{
  "success": true,
  "status_code": 200,
  "message": "Usuário ativado com sucesso.",
  "data": {
    "matricula": "202590125123",
    "is_active": true
  }
}
```

**Resposta de Sucesso - Usuário Desativado (200):**
```json
{
  "success": true,
  "status_code": 200,
  "message": "Usuário desativado com sucesso.",
  "data": {
    "matricula": "202590125123",
    "is_active": false
  }
}
```

---

### 🚗 9. Condutores - Listar

**Endpoint:** `GET /api/condutores/condutores/`

**Descrição:** Lista condutores com filtros e busca

**Parâmetros de Query:**
- `search`: Busca por nome ou matrícula
- `categoria_cnh`: Filtrar por categoria (A, B, C, D, E, AD)
- `ordering`: Ordenação (-data_criacao, data_validade_cnh)

**Exemplo:** `GET /api/condutores/condutores/?categoria_cnh=B&search=João`

**Resposta de Sucesso (200):**
```json
{
  "count": 10,
  "next": null,
  "previous": null,
  "results": [
    {
      "usuario": {
        "nome_completo": "João Silva Santos",
        "email": "joao.silva@email.com",
        "matricula": "202590125123",
        "cpf": "12345678901",
        "telefone": "85987654321",
        "data_nascimento": "1990-05-15",
        "sexo": "M",
        "is_active": true,
        "is_staff": false,
        "is_superuser": false,
        "groups": [4]
      },
      "categoria_cnh": "B",
      "data_validade_cnh": "2026-05-01",
      "data_emissao_cnh": "2021-05-01",
      "data_criacao": "2025-01-15T10:30:00Z"
    }
  ]
}
```

---

### 🚗 10. Condutores - Criar

**Endpoint:** `POST /api/condutores/condutores/`

**Descrição:** Cria novo condutor vinculado a um usuário

**Corpo da Requisição:**
```json
{
  "matricula": "202590125123",
  "categoria_cnh": "B",
  "data_validade_cnh": "2026-05-01",
  "data_emissao_cnh": "2021-05-01"
}
```

**Resposta de Sucesso (201):**
```json
{
  "success": true,
  "status_code": 201,
  "message": "Condutor criado com sucesso.",
  "data": {
    "usuario": {
      "nome_completo": "João Silva Santos",
      "email": "joao.silva@email.com",
      "matricula": "202590125123",
      "cpf": "12345678901",
      "telefone": "85987654321",
      "data_nascimento": "1990-05-15",
      "sexo": "M",
      "is_active": true,
      "is_staff": false,
      "is_superuser": false,
      "groups": [4]
    },
    "categoria_cnh": "B",
    "data_validade_cnh": "2026-05-01",
    "data_emissao_cnh": "2021-05-01",
    "cnh_vencida": false,
    "dias_para_vencimento": 365,
    "data_criacao": "2025-01-15T10:30:00Z",
    "data_atualizacao": "2025-01-15T10:30:00Z"
  }
}
```

**Resposta de Erro - Usuário Não é Condutor (400):**
```json
{
  "success": false,
  "status_code": 400,
  "message": "Dados inválidos fornecidos.",
  "errors": {
    "matricula": "Usuário não pertence ao grupo CONDUTOR."
  },
  "details": null
}
```

---

### 🚗 11. Condutores - Ver Detalhes

**Endpoint:** `GET /api/condutores/condutores/<matricula>/`

**Descrição:** Visualiza detalhes completos do condutor

**Exemplo:** `GET /api/condutores/condutores/202590125123/`

**Resposta de Sucesso (200):**
```json
{
  "success": true,
  "status_code": 200,
  "message": "Dados do condutor recuperados com sucesso.",
  "data": {
    "usuario": {
      "nome_completo": "João Silva Santos",
      "email": "joao.silva@email.com",
      "matricula": "202590125123",
      "cpf": "12345678901",
      "telefone": "85987654321",
      "data_nascimento": "1990-05-15",
      "sexo": "M",
      "is_active": true,
      "is_staff": false,
      "is_superuser": false,
      "groups": [4]
    },
    "categoria_cnh": "B",
    "data_validade_cnh": "2026-05-01",
    "data_emissao_cnh": "2021-05-01",
    "cnh_vencida": false,
    "dias_para_vencimento": 365,
    "data_criacao": "2025-01-15T10:30:00Z",
    "data_atualizacao": "2025-01-15T10:30:00Z"
  }
}
```

---

### 🚗 12. Condutores - Atualizar

**Endpoint:** `PATCH /api/condutores/condutores/<matricula>/`

**Descrição:** Atualiza dados do condutor

**Exemplo:** `PATCH /api/condutores/condutores/202590125123/`

**Corpo da Requisição:**
```json
{
  "categoria_cnh": "AB",
  "data_validade_cnh": "2027-01-01"
}
```

**Resposta de Sucesso (200):**
```json
{
  "success": true,
  "status_code": 200,
  "message": "Dados do condutor atualizados com sucesso.",
  "data": {
    "usuario": {
      "nome_completo": "João Silva Santos",
      "email": "joao.silva@email.com",
      "matricula": "202590125123",
      "cpf": "12345678901",
      "telefone": "85987654321",
      "data_nascimento": "1990-05-15",
      "sexo": "M",
      "is_active": true,
      "is_staff": false,
      "is_superuser": false,
      "groups": [4]
    },
    "categoria_cnh": "AB",
    "data_validade_cnh": "2027-01-01",
    "data_emissao_cnh": "2021-05-01",
    "cnh_vencida": false,
    "dias_para_vencimento": 730,
    "data_criacao": "2025-01-15T10:30:00Z",
    "data_atualizacao": "2025-01-15T15:45:00Z"
  }
}
```

---

### ❌ Respostas de Erro Comuns

**Token Inválido ou Ausente (401):**
```json
{
  "detail": "Given token not valid for any token type",
  "code": "token_not_valid",
  "messages": [
    {
      "token_class": "AccessToken",
      "token_type": "access",
      "message": "Token is invalid or expired"
    }
  ]
}
```

**Usuário Não Encontrado (404):**
```json
{
  "success": false,
  "status_code": 404,
  "message": "Usuário não encontrado.",
  "errors": {
    "matricula": "Nenhum usuário encontrado com esta matrícula."
  },
  "details": "Verifique se a matrícula está correta."
}
```

**Erro Interno do Servidor (500):**
```json
{
  "success": false,
  "status_code": 500,
  "message": "Erro interno do servidor.",
  "errors": {
    "server": "Ocorreu um erro inesperado. Tente novamente."
  },
  "details": "Se o problema persistir, entre em contato com o suporte."
}
```

## 👥 Sistema de Grupos

| Grupo                        | Descrição                           | Permissões                        |
| ---------------------------- | ----------------------------------- | --------------------------------- |
| **ADMINISTRADOR**            | Acesso total ao sistema             | Todas as operações                |
| **ATENDENTE ADMINISTRATIVO** | Operações administrativas limitadas | Gestão de usuários com restrições |
| **FISCAL**                   | Atividades de fiscalização          | Consultas e relatórios            |
| **CONDUTOR**                 | Usuário básico do sistema           | Operações pessoais                |

## 🔧 Configuração Avançada

### Variáveis de Ambiente

```env
# Segurança
SECRET_KEY=sua-chave-super-secreta-de-50-caracteres-aqui
DEBUG=0  # 1 para desenvolvimento, 0 para produção
ALLOWED_HOSTS=seudominio.com,www.seudominio.com

# Paginação e Tokens
PAGE_SIZE=20  # Itens por página (padrão: 10)
ACCESS_TOKEN_MINUTES=60  # Duração do access token (padrão: 60)
REFRESH_TOKEN_DAYS=7  # Duração do refresh token (padrão: 7)
```

### Banco de Dados para Produção

```python
# settings/settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}
```

## 📚 Documentação Completa

### Acesse a Documentação Interativa

- **Swagger UI**: `http://localhost:8000/api/docs/`
- **OpenAPI Schema**: `http://localhost:8000/api/schema/`
- **Django Admin**: `http://localhost:8000/admin/`

### Recursos de Documentação

- **Documentação Completa**: [API_DOCUMENTATION.md](other/API_DOCUMENTATION.md)
- **Postman Collection**: [postman_collection.json](postman_collection.json)
- **Environment Postman**: [postman_environment.json](postman_environment.json)

## 🧪 Testes

```bash
# Executar todos os testes
python manage.py test

# Testes específicos de usuários
python manage.py test app_usuarios

# Testes específicos de condutores
python manage.py test app_condutores

# Testes com verbosidade
python manage.py test --verbosity=2
```

### Cobertura de Testes
- ✅ Autenticação JWT com matrícula
- ✅ Validações brasileiras (CPF, telefone)
- ✅ Sistema de permissões e grupos
- ✅ CRUD completo de usuários e condutores
- ✅ Geração automática de matrícula
- ✅ Respostas padronizadas da API

## 🚦 Sistema de Matrícula

O sistema gera automaticamente uma matrícula única para cada usuário:

**Formato**: `<ano><3_últimos_dígitos_CPF><2_últimos_dígitos_ano><3_dígitos_aleatórios>`

**Exemplo**: Para CPF `12345678901` em 2025 → `202590125123`

## 🛡️ Segurança

### Validações Implementadas
- **CPF**: Algoritmo oficial brasileiro + verificação de unicidade
- **Email**: Validação de formato + unicidade
- **Telefone**: Formato brasileiro (celular/fixo)
- **Senhas**: Hash seguro + validação de complexidade

### Autenticação e Autorização
- **JWT Tokens**: Access/refresh com rotação automática
- **Permissões Granulares**: Controle baseado em grupos Django
- **CORS**: Configurado para ambientes específicos
- **Rate Limiting**: Configurável via middleware

## 🚀 Deploy em Produção

### 1. Configurações de Produção

```env
DEBUG=0
SECRET_KEY=sua-chave-super-secreta-de-produção
ALLOWED_HOSTS=seudominio.com,www.seudominio.com
```

### 2. Colete Arquivos Estáticos

```bash
python manage.py collectstatic --noinput
```

### 3. Configurações de Segurança

```python
# settings/settings.py para produção
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
```

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'feat: Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

### Padrões de Commit
- `feat:` Nova funcionalidade
- `fix:` Correção de bug
- `docs:` Documentação
- `test:` Testes
- `refactor:` Refatoração
- `chore:` Tarefas de build/configuração

## 📜 Licença

Este projeto está licenciado sob a [GNU General Public License v2.0](LICENSE).

## 📞 Suporte

- **Documentação**: [other/API_DOCUMENTATION.md](other/API_DOCUMENTATION.md)
- **Issues**: [GitHub Issues](https://github.com/inovacorrente/sita-backend/issues)
- **Wiki**: [GitHub Wiki](https://github.com/inovacorrente/sita-backend/wiki)

---

<p align="center">
  Desenvolvido com ❤️ para STRANS<br>
  <strong>Sistema de Trânsito - SITA Backend v1.0.0</strong>
</p>