"""
Configurações de administração para o modelo de usuário customizado.
Define como o modelo UsuarioCustom será exibido e gerenciado no site de
administração do Django.
"""

from django.contrib import admin

from app_condutores.models import Condutor

from .models import UsuarioCustom  # Importe seus modelos


# 1. Crie uma classe Inline para o modelo Condutor
# Use TabularInline para uma visualização mais compacta (tabela)
# Use StackedInline para uma visualização padrão (campos empilhados)
class CondutorInline(admin.StackedInline):  # ou admin.TabularInline
    model = Condutor
    can_delete = False  # Impede exclusão pelo usuário
    verbose_name_plural = 'Informações do Condutor'
    # Campos exibidos no inline
    fields = (
        'categoria_cnh',
        'data_emissao_cnh',
        'data_validade_cnh',
    )
    extra = 0


class UsuarioCustomAdmin(admin.ModelAdmin):
    """
    Configurações de exibição do modelo UsuarioCustom no admin.
    Define os campos a serem exibidos na lista e no formulário de edição.
    """
    list_display = (
        'matricula', 'nome_completo', 'email', 'is_active', 'is_staff'
    )
    search_fields = (
        'matricula', 'nome_completo', 'email', 'cpf'
    )
    list_filter = ('is_active', 'is_staff', 'sexo', 'groups')
    ordering = ('-id',)

    # 3. Adicione o inline à classe de admin principal
    inlines = (CondutorInline,)

    # Garantir que o usuário seja salvo antes do inline
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if hasattr(obj, 'condutor'):
            obj.condutor.save()


# Registre sua classe de admin personalizada
admin.site.register(UsuarioCustom, UsuarioCustomAdmin)
