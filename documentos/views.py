from rest_framework import mixins, viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated

from .models import Documento
from .serializers import DocumentoSerializer


class DocumentoViewSet(
        mixins.CreateModelMixin,
        mixins.RetrieveModelMixin,
        mixins.ListModelMixin,
        mixins.DestroyModelMixin,
        viewsets.GenericViewSet,
):  # noqa: D101
    queryset = Documento.objects.select_related(
        'veiculo', 'veiculo__usuario'
    ).all()
    serializer_class = DocumentoSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    parser_classes = [MultiPartParser, FormParser]
    lookup_field = 'id'
