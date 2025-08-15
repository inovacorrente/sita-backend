from django.contrib import admin

from .models import Documento


@admin.register(Documento)
class DocumentoAdmin(admin.ModelAdmin):  # noqa: D101
    list_display = (
        'id', 'veiculo', 'documento', 'data_criacao', 'data_alteracao'
    )
    list_filter = ('data_criacao', 'data_alteracao')
    search_fields = (
        'veiculo__identificador_unico_veiculo',
        'veiculo__usuario__matricula'
    )
