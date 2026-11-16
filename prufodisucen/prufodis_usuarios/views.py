from rest_framework import viewsets

from .models import Usuario
from .permissions import RolRequiredPermission
from .serializers import UsuarioSerializer


class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.select_related("usuario", "asignatura").all()
    serializer_class = UsuarioSerializer
    permission_classes = [RolRequiredPermission]
    required_role = None
