"""
Configuração do Django Admin para o app de documentos do sistema SITA.
Inclui ModelAdmin para documentos de veículos com GenericForeignKey.
"""
from django.contrib import admin

from .models import Documento


@admin.register(Documento)
class DocumentoAdmin(admin.ModelAdmin):
    """
    Administração para documentos de veículos.
    Trabalha com GenericForeignKey para qualquer tipo de veículo.
    """
    # Campos exibidos na lista
    list_display = [
        'id',
        'get_veiculo_info',
        'get_usuario_info',
        'documento',
        'data_criacao',
        'data_alteracao'
    ]

    # Filtros laterais
    list_filter = [
        'content_type',
        'data_criacao',
        'data_alteracao'
    ]

    # Campos para busca
    search_fields = [
        'object_id',
        # Não podemos buscar diretamente nos campos do GenericForeignKey
        # mas podemos buscar pelo ID do objeto
    ]

    # Campos somente leitura
    readonly_fields = ['data_criacao', 'data_alteracao']

    # Organização dos campos no formulário
    fieldsets = (
        ('Veículo Associado', {
            'fields': ('content_type', 'object_id'),
            'description': 'Selecione o tipo e ID do veículo'
        }),
        ('Documento', {
            'fields': ('documento',)
        }),
        ('Timestamps', {
            'fields': ('data_criacao', 'data_alteracao'),
            'classes': ('collapse',)
        }),
    )

    # Ordenação padrão
    ordering = ['-data_criacao']

    # Número de itens por página
    list_per_page = 25

    def get_veiculo_info(self, obj):
        """Retorna informações do veículo associado."""
        veiculo = obj.get_veiculo()
        if veiculo:
            return f"{veiculo.identificador_unico_veiculo} - {veiculo.placa}"
        return "Veículo não encontrado"
    get_veiculo_info.short_description = 'Veículo'

    def get_usuario_info(self, obj):
        """Retorna informações do usuário proprietário do veículo."""
        veiculo = obj.get_veiculo()
        if veiculo and veiculo.usuario:
            nome = veiculo.usuario.nome_completo
            matricula = veiculo.usuario.matricula
            return f"{nome} ({matricula})"
        return "Usuário não encontrado"
    get_usuario_info.short_description = 'Proprietário'

    def has_change_permission(self, request, obj=None):
        """Permite edição apenas se o usuário for staff."""
        return request.user.is_staff

    def has_delete_permission(self, request, obj=None):
        """Permite exclusão apenas se o usuário for staff."""
        return request.user.is_staff
