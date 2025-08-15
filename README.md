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

8. (Opcional) Crie veículos de exemplo:
   ```sh
   python manage.py criar_veiculos_fake --quantidade 10
   ```

9. Inicie o servidor:
   ```sh
   python manage.py runserver
   ```

## Comandos de Management

O sistema inclui comandos personalizados para facilitar o desenvolvimento e testes:

### Comandos de Usuários

#### `criar_grupos`
Cria os grupos padrão do sistema com suas permissões específicas.

```sh
python manage.py criar_grupos
```

**Grupos criados:**
- `ADMINISTRADOR` - Acesso total ao sistema
- `ATENDENTE ADMINISTRATIVO` - Acesso para atendimento
- `FISCAL` - Acesso para fiscalização
- `CONDUTOR` - Acesso básico para condutores

#### `criar_usuarios`
Cria usuários de exemplo para testes.

```sh
python manage.py criar_usuarios
```

**Usuários criados:**
- Admin: matrícula `400000000001`, senha `admin123`
- Atendente: matrícula `400000000002`, senha `atendente123`
- Fiscal: matrícula `400000000003`, senha `fiscal123`
- Condutor: matrícula `400000000004`, senha `condutor123`

### Comandos de Veículos

#### `criar_veiculos_fake`
Gera dados fake de veículos usando a biblioteca Faker.

**Uso básico:**
```sh
# Cria 10 veículos distribuídos igualmente entre os tipos
python manage.py criar_veiculos_fake --quantidade 10

# Cria quantidades específicas por tipo
python manage.py criar_veiculos_fake --taxis 5 --mototaxis 3 --transporte 2

# Remove todos os veículos existentes antes de criar novos
python manage.py criar_veiculos_fake --quantidade 15 --clear
```

**Parâmetros disponíveis:**
- `--quantidade`: Quantidade total a criar (distribuído igualmente)
- `--taxis`: Quantidade específica de táxis
- `--mototaxis`: Quantidade específica de mototáxis  
- `--transporte`: Quantidade específica de veículos de transporte municipal
- `--clear`: Remove todos os veículos existentes antes de criar

**Dados gerados automaticamente:**
- Placas brasileiras (padrão antigo e Mercosul)
- RENAVAM e chassi válidos
- Marcas e modelos realistas por tipo de veículo
- Cores variadas
- Anos de fabricação entre 2000 e atual
- Linhas e capacidades para transporte municipal
- Associação aleatória com usuários existentes

**Exemplos práticos:**
```sh
# Criar dados para desenvolvimento
python manage.py criar_veiculos_fake --quantidade 20

# Criar apenas táxis para testar funcionalidade específica
python manage.py criar_veiculos_fake --taxis 10

# Resetar dados e criar novo conjunto
python manage.py criar_veiculos_fake --clear --quantidade 30

# Criar distribuição personalizada
python manage.py criar_veiculos_fake --taxis 8 --mototaxis 12 --transporte 5
```

## Endpoints Principais

### Autenticação
- Login: `POST /api/usuarios/login/`
- Refresh Token: `POST /api/usuarios/token/refresh/`

### Usuários
- Listar usuários: `GET /api/usuarios/`
- Criar usuário: `POST /api/usuarios/`
- Detalhes do usuário: `GET /api/usuarios/{id}/`
- Atualizar usuário: `PUT/PATCH /api/usuarios/{id}/`

### Veículos

#### Táxis
- Listar táxis: `GET /api/veiculos/taxis/`
- Criar táxi: `POST /api/veiculos/taxis/`
- Detalhes do táxi: `GET /api/veiculos/taxis/{identificador}/`
- Atualizar táxi: `PUT/PATCH /api/veiculos/taxis/{identificador}/`
- Meus táxis: `GET /api/veiculos/taxis/meus_veiculos/`
- Resumo de táxis: `GET /api/veiculos/taxis/resumo/`

#### Mototáxis
- Listar mototáxis: `GET /api/veiculos/mototaxis/`
- Criar mototáxi: `POST /api/veiculos/mototaxis/`
- Detalhes do mototáxi: `GET /api/veiculos/mototaxis/{identificador}/`
- Atualizar mototáxi: `PUT/PATCH /api/veiculos/mototaxis/{identificador}/`
- Meus mototáxis: `GET /api/veiculos/mototaxis/meus_veiculos/`
- Resumo de mototáxis: `GET /api/veiculos/mototaxis/resumo/`

#### Transporte Municipal
- Listar transportes: `GET /api/veiculos/transporte-municipal/`
- Criar transporte: `POST /api/veiculos/transporte-municipal/`
- Detalhes do transporte: `GET /api/veiculos/transporte-municipal/{identificador}/`
- Atualizar transporte: `PUT/PATCH /api/veiculos/transporte-municipal/{identificador}/`
- Meus transportes: `GET /api/veiculos/transporte-municipal/meus_veiculos/`
- Resumo de transportes: `GET /api/veiculos/transporte-municipal/resumo/`
- Agrupar por linha: `GET /api/veiculos/transporte-municipal/por_linha/`

### Parâmetros de Filtro

**Filtros disponíveis para veículos:**
- `matricula`: Filtra por matrícula do usuário (apenas admins)
- `placa`: Filtra por placa do veículo
- `marca`: Filtra por marca do veículo
- `modelo`: Filtra por modelo do veículo
- `search`: Busca geral por placa, marca, modelo, cor, usuário ou identificador
- `page`: Número da página para paginação
- `page_size`: Itens por página

**Filtros específicos para transporte municipal:**
- `linha`: Filtra por linha de transporte
- `capacidade_min`: Capacidade mínima do veículo
- `capacidade_max`: Capacidade máxima do veículo

**Exemplos de uso:**
```sh
# Buscar todos os táxis de uma marca
GET /api/veiculos/taxis/?marca=Toyota

# Buscar veículos por placa
GET /api/veiculos/taxis/?placa=ABC1234

# Busca geral
GET /api/veiculos/taxis/?search=Honda

# Meus veículos com busca
GET /api/veiculos/taxis/meus_veiculos/?search=Civic

# Transporte municipal por linha
GET /api/veiculos/transporte-municipal/?linha=001

# Paginação
GET /api/veiculos/taxis/?page=2&page_size=10
```

### Documentação
- Documentação Swagger: `/api/docs/`
- Schema OpenAPI: `/api/schema/`

## Permissões e Segurança

### Controle de Acesso a Veículos

O sistema implementa controle de acesso baseado em permissões do Django:

**Usuários Administradores (`is_staff=True`):**
- Podem visualizar, criar, editar e deletar qualquer veículo
- Podem filtrar veículos por matrícula do usuário
- Têm acesso total a todas as funcionalidades

**Usuários Regulares:**
- Podem visualizar apenas seus próprios veículos
- Podem editar apenas seus próprios veículos
- Podem deletar apenas seus próprios veículos
- Não podem acessar veículos de outros usuários

**Endpoints de Segurança:**
- `/meus_veiculos/`: Retorna apenas veículos do usuário logado
- Verificação automática de propriedade em operações CRUD
- Respostas HTTP 403 (Forbidden) para tentativas de acesso não autorizado

### Autenticação JWT

O sistema utiliza JWT (JSON Web Tokens) para autenticação:

```sh
# Login
POST /api/usuarios/login/
{
    "matricula": "400000000001",
    "password": "admin123"
}

# Resposta
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}

# Uso do token
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

## Estrutura do Projeto

```
sita-backend/
├── app_usuarios/          # App de usuários customizados
│   ├── management/
│   │   └── commands/      # Comandos: criar_grupos, criar_usuarios
│   ├── models.py          # UsuarioCustom
│   ├── serializers.py     # Serializers de usuários
│   └── views.py           # ViewSets de usuários
├── app_condutores/        # App de condutores (CNH)
├── app_veiculos/          # App de veículos
│   ├── management/
│   │   └── commands/      # Comandos: criar_veiculos_fake
│   ├── models.py          # TaxiVeiculo, MotoTaxiVeiculo, TransporteMunicipalVeiculo
│   ├── serializers.py     # Serializers de veículos
│   ├── views.py           # ViewSets de veículos
│   └── admin.py           # Configuração do Django Admin
├── documentos/            # App para documentos de veículos
├── utils/                 # Utilitários compartilhados
│   ├── commons/           # Validadores e exceções comuns
│   ├── app_usuarios/      # Validadores específicos de usuários
│   ├── app_veiculos/      # Validadores específicos de veículos
│   └── permissions/       # Permissões customizadas
└── settings/              # Configurações do Django
```

## Recursos Implementados

### ✅ Autenticação e Usuários
- ✅ Login via matrícula e senha
- ✅ JWT tokens (access e refresh)
- ✅ Usuários customizados com CPF, telefone, grupos
- ✅ Geração automática de matrícula
- ✅ Sistema de grupos e permissões

### ✅ Veículos
- ✅ Três tipos: Táxi, Mototáxi, Transporte Municipal
- ✅ Validações brasileiras (placa, RENAVAM, chassi)
- ✅ Identificador único por veículo
- ✅ Relacionamento com usuários
- ✅ Filtros avançados e busca
- ✅ Controle de acesso por proprietário
- ✅ Endpoints `/meus_veiculos/` para usuários

### ✅ API REST
- ✅ Django REST Framework
- ✅ Serializers específicos (create/view/update)
- ✅ Paginação automática
- ✅ Documentação Swagger
- ✅ Validações customizadas
- ✅ Tratamento de erros padronizado

### ✅ Admin Django
- ✅ Interface administrativa completa
- ✅ Filtros e busca otimizados
- ✅ Autocomplete para relacionamentos
- ✅ Campos organizados em fieldsets
- ✅ Listagem otimizada com select_related

### ✅ Comandos de Management
- ✅ Criação de grupos padrão
- ✅ Criação de usuários de teste
- ✅ Geração de dados fake de veículos
- ✅ Suporte a argumentos personalizados

### ✅ Utilitários e Validações
- ✅ Validadores para CPF, placa, RENAVAM, chassi
- ✅ Exceções customizadas por app
- ✅ Respostas padronizadas de sucesso/erro
- ✅ Permissões baseadas no Django

## Variáveis de Ambiente

Veja o arquivo [.env-example](.env-example) para exemplos de configuração.

## Licença

Este projeto está licenciado sob a [GNU GPL v2](LICENSE).