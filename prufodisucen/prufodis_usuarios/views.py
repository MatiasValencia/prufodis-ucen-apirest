from rest_framework import viewsets

from .models import Usuario
from .serializers import UsuarioSerializer


class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.select_related("usuario", "asignatura").all()
    serializer_class = UsuarioSerializer
