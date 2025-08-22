"""
Configuração do Django Admin para o app de veículos do sistema SITA.
Inclui ModelAdmin para todos os tipos de veículos com campos personalizados.
"""
from django.contrib import admin

from .models import (BannerIdentificacao, MotoTaxiVeiculo, TaxiVeiculo,
                     TransporteMunicipalVeiculo)

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

@admin.register(BannerIdentificacao)
class BannerIdentificacaoAdmin(admin.ModelAdmin):
    """
    Administração para banners de identificação de veículos.
    """
    list_display = [
        'id',
        'get_veiculo_info',
        'get_proprietario_nome',
        'ativo',
        'data_criacao',
        'data_atualizacao'
    ]

    list_filter = [
        'ativo',
        'data_criacao',
        'content_type'
    ]

    search_fields = [
        'veiculo__placa',
        'veiculo__identificador_unico_veiculo'
    ]

    readonly_fields = [
        'data_criacao',
        'data_atualizacao',
        'qr_url'
    ]

    actions = ['regenerar_banners']

    def get_veiculo_info(self, obj):
        """Retorna informações do veículo."""
        if obj.veiculo:
            placa = obj.veiculo.placa
            identificador = obj.veiculo.identificador_unico_veiculo
            return f"{placa} ({identificador})"
        return "N/A"
    get_veiculo_info.short_description = "Veículo"

    def get_proprietario_nome(self, obj):
        """Retorna nome do proprietário."""
        if obj.veiculo and obj.veiculo.usuario:
            return obj.veiculo.usuario.nome_completo
        return "N/A"
    get_proprietario_nome.short_description = "Proprietário"

    def regenerar_banners(self, request, queryset):
        """Action para regenerar banners selecionados."""
        count = 0
        for banner in queryset:
            try:
                banner.gerar_banner()
                count += 1
            except Exception as e:
                self.message_user(
                    request,
                    f"Erro ao regenerar banner {banner.id}: {str(e)}",
                    level='ERROR'
                )

        if count > 0:
            self.message_user(
                request,
                f"{count} banner(s) regenerado(s) com sucesso."
            )
    regenerar_banners.short_description = "Regenerar banners selecionados"


# Configurações do título do admin
admin.site.site_header = "SITA - Sistema de Trânsito"
admin.site.site_title = "SITA Admin"
admin.site.index_title = "Administração do Sistema SITA"
