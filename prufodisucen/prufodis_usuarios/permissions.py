from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import SAFE_METHODS, BasePermission

from .models import Usuario


PERMISSION_DENIED_MESSAGE = (
    "Usted no tiene los permisos para realizar esta tarea"
)


class RolRequiredPermission(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        rol_requerido = getattr(view, "required_role", None)
        perfil = Usuario.objects.filter(
            usuario_id=request.user.pk
        ).first()

        if perfil is None:
            raise PermissionDenied(PERMISSION_DENIED_MESSAGE)

        request.usuario_perfil = perfil
        if rol_requerido is None or perfil.rol != rol_requerido:
            if request.method in SAFE_METHODS:
                return True
            raise PermissionDenied(PERMISSION_DENIED_MESSAGE)

        return True

    def has_object_permission(self, request, view, obj):
        if (
            getattr(view, "required_role", None) == Usuario.Rol.PROFESOR
            and not view.belongs_to_assigned_subject(obj)
        ):
            raise PermissionDenied(PERMISSION_DENIED_MESSAGE)

        return True


class AsignaturaPermission(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        perfil = Usuario.objects.filter(
            usuario_id=request.user.pk
        ).first()
        if perfil is None or perfil.rol not in (
            Usuario.Rol.ADMINISTRADOR,
            Usuario.Rol.PROFESOR,
        ):
            if perfil is None:
                raise PermissionDenied(PERMISSION_DENIED_MESSAGE)
            if request.method not in SAFE_METHODS:
                raise PermissionDenied(PERMISSION_DENIED_MESSAGE)

        request.usuario_perfil = perfil
        if (
            perfil.rol == Usuario.Rol.PROFESOR
            and view.action not in ("list", "retrieve", "update", "partial_update")
            and request.method not in SAFE_METHODS
        ):
            raise PermissionDenied(PERMISSION_DENIED_MESSAGE)

        return True

    def has_object_permission(self, request, view, obj):
        perfil = request.usuario_perfil
        if (
            perfil.rol == Usuario.Rol.PROFESOR
            and obj.pk != perfil.asignatura_id
        ):
            raise PermissionDenied(PERMISSION_DENIED_MESSAGE)

        return True
