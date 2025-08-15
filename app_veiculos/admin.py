"""
Configuração do Django Admin para o app de veículos do sistema SITA.
Inclui ModelAdmin para todos os tipos de veículos com campos personalizados.
"""
from django.contrib import admin

from .models import MotoTaxiVeiculo, TaxiVeiculo, TransporteMunicipalVeiculo

# ============================================================================
# BASE ADMIN CLASS
# ============================================================================


class BaseVeiculoAdmin(admin.ModelAdmin):
    """
    Classe base para administração de veículos.
    Contém configurações comuns para todos os tipos de veículos.
    """
    # Campos exibidos na lista
    list_display = [
        'identificador_unico_veiculo',
        'placa',
        'marca',
        'modelo',
        'cor',
        'get_usuario_nome',
        'get_usuario_matricula',
        'anoFabricacao'
    ]

    # Campos para busca
    search_fields = [
        'identificador_unico_veiculo',
        'placa',
        'marca',
        'modelo',
        'cor',
        'renavam',
        'chassi',
        'usuario__nome_completo',
        'usuario__matricula'
    ]

    # Filtros laterais
    list_filter = [
        'marca',
        'cor',
        'anoFabricacao',
        'anoLimiteFabricacao',
        'usuario__groups'
    ]

    # Campos somente leitura
    readonly_fields = ['identificador_unico_veiculo']

    # Organização dos campos no formulário
    fieldsets = (
        ('Informações do Usuário', {
            'fields': ('usuario',)
        }),
        ('Identificação do Veículo', {
            'fields': (
                'identificador_unico_veiculo',
                'placa',
                'renavam',
                'chassi'
            )
        }),
        ('Características do Veículo', {
            'fields': (
                'marca',
                'modelo',
                'cor',
                'anoFabricacao',
                'anoLimiteFabricacao'
            )
        }),
    )

    # Autocomplete para usuário
    autocomplete_fields = ['usuario']

    # Ordenação padrão
    ordering = ['-id']

    # Número de itens por página
    list_per_page = 25

    # Exibir total de registros
    list_max_show_all = 200

    def get_usuario_nome(self, obj):
        """Retorna o nome completo do usuário proprietário."""
        return obj.usuario.nome_completo if obj.usuario else '-'
    get_usuario_nome.short_description = 'Nome do Usuário'
    get_usuario_nome.admin_order_field = 'usuario__nome_completo'

    def get_usuario_matricula(self, obj):
        """Retorna a matrícula do usuário proprietário."""
        return obj.usuario.matricula if obj.usuario else '-'
    get_usuario_matricula.short_description = 'Matrícula'
    get_usuario_matricula.admin_order_field = 'usuario__matricula'

    def get_queryset(self, request):
        """Otimiza consultas com select_related."""
        return super().get_queryset(request).select_related('usuario')


# ============================================================================
# ADMIN CLASSES ESPECÍFICAS
# ============================================================================

@admin.register(TaxiVeiculo)
class TaxiVeiculoAdmin(BaseVeiculoAdmin):
    """
    Administração para veículos de táxi.
    Herda configurações base e adiciona customizações específicas.
    """
    pass


@admin.register(MotoTaxiVeiculo)
class MotoTaxiVeiculoAdmin(BaseVeiculoAdmin):
    """
    Administração para veículos de mototáxi.
    Herda configurações base e adiciona customizações específicas.
    """
    pass


@admin.register(TransporteMunicipalVeiculo)
class TransporteMunicipalVeiculoAdmin(BaseVeiculoAdmin):
    """
    Administração para veículos de transporte municipal.
    Herda configurações base e adiciona campos específicos.
    """
    # Adiciona campos específicos do transporte municipal
    list_display = BaseVeiculoAdmin.list_display + ['linha', 'capacidade']

    # Adiciona filtros específicos
    list_filter = BaseVeiculoAdmin.list_filter + ['linha', 'capacidade']

    # Adiciona busca por linha
    search_fields = BaseVeiculoAdmin.search_fields + ['linha']

    # Reorganiza fieldsets para incluir campos específicos
    fieldsets = BaseVeiculoAdmin.fieldsets + (
        ('Informações do Transporte', {
            'fields': ('linha', 'capacidade'),
            'description': 'Informações específicas do transporte municipal'
        }),
    )

    def get_queryset(self, request):
        """Otimiza consultas específicas para transporte municipal."""
        return super().get_queryset(request)


# ============================================================================
# CUSTOMIZAÇÕES GERAIS DO ADMIN
# ============================================================================

# Configurações do título do admin
admin.site.site_header = "SITA - Sistema de Trânsito"
admin.site.site_title = "SITA Admin"
admin.site.index_title = "Administração do Sistema SITA"
