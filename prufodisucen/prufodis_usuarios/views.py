from rest_framework import viewsets

from .models import Usuario
from .permissions import RolRequiredPermission
from .serializers import UsuarioSerializer


class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.select_related("usuario").prefetch_related(
        "asignaturas"
    )
    serializer_class = UsuarioSerializer
    permission_classes = [RolRequiredPermission]
    required_role = None
    filterset_fields = ("rol", "asignaturas")
    search_fields = (
        "usuario__username",
        "usuario__first_name",
        "usuario__last_name",
        "rol",
    )
