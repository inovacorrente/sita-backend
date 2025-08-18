from rest_framework import serializers

from .models import Documento


class DocumentoSerializer(serializers.ModelSerializer):  # noqa: D101
    class Meta:
        model = Documento
        fields = [
            'id', 'veiculo', 'documento', 'data_criacao', 'data_alteracao'
        ]
        read_only_fields = ['id', 'data_criacao', 'data_alteracao']
        read_only_fields = ['id', 'data_criacao', 'data_alteracao']
