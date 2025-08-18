# Instruções Personalizadas - GitHub Copilot
# Projeto SITA Backend - Sistema STRANS

## Contexto do Projeto

Este é o backend do Sistema SITA (Sistema de Trânsito) da STRANS, desenvolvido em Django REST Framework.

O sistema gerencia usuários, autenticação JWT, e operações relacionadas ao trânsito municipal.

## Criação de aquivos que não pode ser criado
A cada função que o copilot sugerir, verificar se já existe um arquivo com o mesmo nome. Se existir, não criar outro arquivo.

O copilot não precisa criar .md de instruções do que ele implementa ou de como ele funciona, pois sera documentada no README.md do projeto, faça modificações no README.md para documentar o que foi implementado, só quando for pedido.

## Padrões de Código Python/Django

Sempre seguir PEP 8 com linha máxima de 120 caracteres.

Usar nomes descritivos em snake_case para variáveis e funções, PascalCase para classes e models.

Documentar funções complexas com docstrings no formato Google Style.

Para models Django, sempre incluir docstring na classe e help_text nos campos importantes.

```python
class UsuarioCustom(AbstractUser):
    """
    Modelo customizado de usuário para o sistema SITA.
    Inclui campos adicionais específicos do domínio municipal.
    """
    cpf = models.CharField(
        max_length=11, 
        unique=True,
        help_text="CPF sem pontuação"
    )
```

## Ambiente de Desenvolvimento
Sempre que for utlilizar o terminal, usar o ambiente virtual do projeto:

```bash
# Ativar ambiente virtual 

### Linux/Mac
source venv/bin/activate

### Windows
venv\Scripts\activate
```


## Estrutura de API REST

Sempre retornar respostas no formato padrão do projeto:

Sucesso (2xx):
```json
{
    "success": true,
    "data": {...},
    "message": "Operação realizada com sucesso"
}
```

Erro (4xx/5xx):
```json
{
    "success": false,
    "error": {
        "code": "ERROR_CODE",
        "message": "Mensagem descritiva",
        "details": {...}
    }
}
```

Para ViewSets DRF, usar sempre ModelViewSet como base e incluir permission_classes apropriadas.

Serializers devem ter docstring explicando seu propósito e extra_kwargs para campos sensíveis como password.

## Validações e Segurança

Sempre implementar validadores customizados para CPF, telefone e outros dados brasileiros.

```python
def validate_cpf(value):
    """Valida formato e dígitos verificadores do CPF."""
    if len(value) != 11 or not value.isdigit():
        raise ValidationError("CPF deve conter 11 dígitos numéricos")
```

Para autenticação, usar sempre JWT tokens com refresh token.

Headers obrigatórios: Authorization: Bearer <token> e Content-Type: application/json.

## Validators e Exceptions em `utils/`

Para evitar duplicidade e facilitar reuso, centralize validadores e exceções no diretório `utils/` do projeto.

Estrutura recomendada:

```
utils/
  commons/
    exceptions.py    # Classes/utilitários de respostas e exceções comuns
  app_usuarios/
    validators.py    # Validadores específicos do app (se necessário)
    exceptions.py    # Exceções/respostas específicas do app (se necessário)
  app_condutores/
    validators.py
    exceptions.py
  # ... outros apps, se houver validações específicas
```

Diretrizes para validadores (em `utils/app_{nome do app}/validators.py`):
- Use funções puras com type hints e docstrings (Google Style) e mensagens claras.
- Para models, levante `django.core.exceptions.ValidationError`.
- Para serializers, pode-se usar `rest_framework.serializers.ValidationError`.
- Mantenha nomes descritivos: `validate_cpf`, `validate_renavam`, `validate_vin`, `validate_placa_br`, etc.

Exemplo (esqueleto) de validador compartilhado:

```python
from django.core.exceptions import ValidationError

def normalize_alphanumeric_upper(value: str) -> str:
    """Remove espaços nas extremidades e aplica uppercase."""
    return value.strip().upper() if value is not None else value

def validate_placa_br(value: str):
    """Valida placa brasileira (padrão antigo e Mercosul)."""
    if not value:
        raise ValidationError("Placa não pode ser vazia")
    v = normalize_alphanumeric_upper(value)
    # aplique regex antigo/mercosul aqui; lance ValidationError em caso inválido
```

Diretrizes para exceções e respostas (em `utils/commons/exceptions.py`):
- Concentre helpers de resposta de sucesso/erro padronizada (ex.: `SuccessResponse`, `ValidationErrorResponse`).
- Para erros, prefira levantar exceções do Django/DRF; o handler customizado formatará a resposta.
- Evite construir dicionários de erro manualmente nas views; use o handler e utilitários.

Custom Exception Handler (já configurado):
- O projeto usa `REST_FRAMEWORK['EXCEPTION_HANDLER'] = 'utils.commons.validators.custom_exception_handler'`.
- Portanto, ao levantar `ValidationError`, `PermissionDenied`, `NotFound`, etc., as respostas serão padronizadas automaticamente.

Padrões de importação (exemplos):

```python
# Em models
from utils.app_veiculos.validators import validate_placa_br, validate_renavam, validate_vin

# Em serializers
from utils.app_veiculos.validators import normalize_alphanumeric_upper
from rest_framework import serializers

# Em views
from utils.commons.exceptions import SuccessResponse, ValidationErrorResponse
from rest_framework.exceptions import ValidationError
```

Uso em Model (campo com validator):

```python
class Veiculo(models.Model):
    placa = models.CharField(
        max_length=10,
        unique=True,
        validators=[validate_placa_br],
        help_text="Placa brasileira (padrão antigo ou Mercosul)",
    )
    # ...
    def clean(self):
        super().clean()
        self.placa = normalize_alphanumeric_upper(self.placa)
```

Uso em Serializer (validação de campo):

```python
class VeiculoSerializer(serializers.ModelSerializer):
    def validate_placa(self, value: str) -> str:
        value = normalize_alphanumeric_upper(value)
        validate_placa_br(value)
        return value
```

Uso em View (resposta padrão + exceção):

```python
class VeiculoViewSet(ModelViewSet):
    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return Response(SuccessResponse.created(response.data), status=201)

    def perform_create(self, serializer):
        if some_invalid_condition:
            # Será formatado pelo custom_exception_handler
            raise ValidationError({"placa": "Placa inválida."})
        serializer.save()
```

Boas práticas adicionais:
- Evite importações cíclicas: mantenha validadores/exceções genéricos em `utils/commons`.
- Validadores específicos de domínio de um app devem residir em uma pasta
    dedicada no `utils/` do projeto, por exemplo:
    - `utils/app_veiculos/validators.py` e `utils/app_veiculos/exceptions.py`
    - `utils/app_usuarios/validators.py` e `utils/app_usuarios/exceptions.py`
    - `utils/app_condutores/validators.py` e `utils/app_condutores/exceptions.py`
    Use `utils/commons` para tudo que for compartilhado entre apps e `utils/app_<app>`
    apenas para regras estritamente específicas daquele domínio.
- Exemplo de estrutura para o app de veículos:

```
utils/
    commons/
        validators.py
        exceptions.py
    app_veiculos/
        validators.py    # regras específicas (ex.: validações de categoria, regras municipais do app)
        exceptions.py    # exceções/respostas específicas do domínio de veículos
```

- Exemplo de importação quando houver regra específica de app:

```python
# Compartilhados
from utils.app_veiculos.validators import validate_vin

# Específicos de veículos
from utils.app_veiculos.validators import validate_restricao_categoria
```

- Sempre documente regras de negócio nas docstrings e use mensagens de validação em português, claras e objetivas.

## Testes

Não precisa criar Testes para cada função, mas sempre incluir testes para modelos, serializers e views principais.

## Performance e Cache

Para queries otimizadas, usar select_related() para ForeignKey e prefetch_related() para ManyToMany.

Implementar cache manual para dados que não mudam frequentemente usando django.core.cache.

```python
from django.core.cache import cache

def get_usuario_stats():
    cache_key = 'usuario_stats'
    stats = cache.get(cache_key)
    if stats is None:
        stats = {'total': UsuarioCustom.objects.count()}
        cache.set(cache_key, stats, 300)  # 5 minutos
    return stats
```

## Logging

Sempre usar logging para operações importantes e erros.

```python
import logging
logger = logging.getLogger(__name__)

def create(self, request, *args, **kwargs):
    logger.info(f"Criando usuário: {request.data.get('username')}")
```

## Migrations e Banco de Dados

Para migrations de dados, sempre incluir operação reversa.

Usar RunPython para migrations customizadas com função de rollback.

Para campos com índices, usar db_index=True ou indexes na Meta class.

## Comandos de Gerenciamento

Criar comandos customizados em app/management/commands/ para tarefas administrativas.

Sempre incluir help text e argumentos opcionais quando aplicável.

```python
class Command(BaseCommand):
    help = 'Descrição clara do comando'
    
    def add_arguments(self, parser):
        parser.add_argument('--quantidade', type=int, default=10)
```

## Convenções de Nomenclatura

URLs usar snake_case: usuarios/, usuarios/<int:matricula>/, login/

Views e funções em snake_case: criar_usuario, validar_dados

Arquivos e diretórios em snake_case: app_usuarios/, management/

Variáveis de ambiente em UPPER_CASE: DEBUG, SECRET_KEY

## Estrutura de Arquivos

Apps Django seguir estrutura padrão: models.py, views.py, serializers.py, urls.py, tests.py

Para validadores customizados, criar validators.py no app

Para utilitários, criar utils.py no app

Management commands em app/management/commands/

## Git e Commits

Usar conventional commits: feat:, fix:, docs:, test:, refactor:, chore:

Formato: tipo(escopo): descrição breve

Exemplo: feat(usuarios): adicionar validação de CPF

Branches seguir padrão: feature/nome-feature, bugfix/nome-bug, hotfix/nome-hotfix

## Variáveis de Ambiente

Sempre usar variáveis de ambiente para configurações sensíveis.

Obrigatórias: DEBUG, SECRET_KEY, ALLOWED_HOSTS, DATABASE_URL

Verificar configurações críticas no startup da aplicação.

## Tratamento de Erros

Sempre capturar e logar exceções específicas do Django (ValidationError, ObjectDoesNotExist).

Para APIs, retornar códigos HTTP apropriados: 400 (Bad Request), 401 (Unauthorized), 403 (Forbidden), 404 (Not Found).

Usar try/except com logging para operações que podem falhar.

## Contexto Municipal

Este é um sistema para prefeitura, então considerar:

Validações específicas do Brasil (CPF, telefone)

Campos como matrícula dos usuarios

Grupos de usuários: ADMINISTRADOR, ATENDENTE ADMINISTRATIVO, FISCAL, CONDUTOR

Foco em funcionalidades de trânsito e transporte público, taxista e mototaxista.

## Boas Práticas Gerais

Sempre pensar em segurança: validar dados de entrada, sanitizar outputs

Otimizar queries do banco de dados antes de implementar cache

Documentar APIs complexas com exemplos de uso

Manter código DRY (Don't Repeat Yourself) criando funções reutilizáveis

Usar type hints quando possível para melhor IntelliSense

Implementar paginação para listagens que podem ter muitos registros
