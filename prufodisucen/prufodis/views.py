from .models import *
from .serializers import *
from rest_framework import viewsets
from rest_framework.exceptions import (
    PermissionDenied,
    ValidationError as APIValidationError,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import FormParser, MultiPartParser
from prufodis_usuarios.models import Usuario
from prufodis_usuarios.permissions import (
    AsignaturaPermission,
    PERMISSION_DENIED_MESSAGE,
    RolRequiredPermission,
)


class RolViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, RolRequiredPermission]
    required_role = None


class ProfesorAsignaturaViewSet(RolViewSet):
    required_role = Usuario.Rol.PROFESOR

    def get_asignatura_id(self):
        return self.request.usuario_perfil.asignatura_id

    def ensure_assigned_subject(self, asignatura):
        if asignatura is None or asignatura.pk != self.get_asignatura_id():
            raise PermissionDenied(PERMISSION_DENIED_MESSAGE)

    def perform_create(self, serializer):
        self.validate_write_scope(serializer.validated_data)
        serializer.save()

    def perform_update(self, serializer):
        self.validate_write_scope(
            serializer.validated_data,
            instance=serializer.instance,
        )
        serializer.save()

    def belongs_to_assigned_subject(self, obj):
        raise NotImplementedError

    def validate_write_scope(self, data, instance=None):
        raise NotImplementedError


class EstudianteViewSet(RolViewSet):
    queryset = Estudiante.objects.all()
    serializer_class = EstudianteSerializer
    required_role = Usuario.Rol.ADMINISTRADOR
    filterset_fields = (
        "nombres",
        "primerApellido",
        "segundoApellido",
        "rut",
        "apoderado",
        "telefono",
    )
    search_fields = (
        "nombres",
        "primerApellido",
        "segundoApellido",
        "rut",
        "apoderado",
        "telefono",
    )


class DocumentoEstudianteViewSet(RolViewSet):
    queryset = DocumentoEstudiante.objects.all()
    serializer_class = DocumentoEstudianteSerializer
    parser_classes = [MultiPartParser, FormParser]
    required_role = Usuario.Rol.PSICOLOGO
    filterset_fields = ("estudiante", "fechaSubida")
    search_fields = (
        "archivo",
        "estudiante__nombres",
        "estudiante__primerApellido",
        "estudiante__segundoApellido",
    )

    def get_queryset(self):
        queryset = super().get_queryset()
        estudiante_id = self.request.query_params.get("estudiante")
        if estudiante_id is None:
            return queryset

        try:
            estudiante_id = int(estudiante_id)
        except ValueError as error:
            raise APIValidationError({
                "estudiante": "Debe ser un identificador válido."
            }) from error

        return queryset.filter(estudiante_id=estudiante_id)


class AsignaturaViewSet(RolViewSet):
    queryset = Asignatura.objects.all()
    serializer_class = AsignaturaSerializer
    permission_classes = [IsAuthenticated, AsignaturaPermission]
    filterset_fields = ("nombre", "cantidadNotas", "estudiantes")
    search_fields = ("nombre",)

    def get_queryset(self):
        queryset = super().get_queryset()
        if (
            self.action == "list"
            and self.request.usuario_perfil.rol == Usuario.Rol.PROFESOR
        ):
            return queryset.filter(pk=self.request.usuario_perfil.asignatura_id)
        return queryset

    def update(self, request, *args, **kwargs):
        if request.usuario_perfil.rol == Usuario.Rol.PROFESOR:
            if set(request.data) - {"estudiantes"}:
                raise PermissionDenied(PERMISSION_DENIED_MESSAGE)
            kwargs["partial"] = True
        return super().update(request, *args, **kwargs)


class DocumentoAsignaturaViewSet(ProfesorAsignaturaViewSet):
    queryset = DocumentoAsignatura.objects.all()
    serializer_class = DocumentoAsignaturaSerializer
    parser_classes = [MultiPartParser, FormParser]
    filterset_fields = ("asignatura", "fechaSubida")
    search_fields = ("archivo", "asignatura__nombre")

    def get_queryset(self):
        queryset = super().get_queryset().filter(
            asignatura_id=self.get_asignatura_id()
        )
        if self.action != "list":
            return super().get_queryset()

        asignatura_id = self.request.query_params.get("asignatura")
        if asignatura_id is None:
            return queryset

        try:
            asignatura_id = int(asignatura_id)
        except ValueError as error:
            raise APIValidationError({
                "asignatura": "Debe ser un identificador válido."
            }) from error

        return queryset.filter(asignatura_id=asignatura_id)

    def validate_write_scope(self, data, instance=None):
        asignatura = data.get(
            "asignatura",
            instance.asignatura if instance is not None else None,
        )
        self.ensure_assigned_subject(asignatura)

    def belongs_to_assigned_subject(self, obj):
        return obj.asignatura_id == self.get_asignatura_id()


class AsistenciaViewSet(ProfesorAsignaturaViewSet):
    queryset = Asistencia.objects.all()
    serializer_class = AsistenciaSerializer
    filterset_fields = ("asignatura", "fecha", "horaInicio", "horaFin")
    search_fields = ("asignatura__nombre", "estudiantes__nombres")

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.action == "list":
            return queryset.filter(asignatura_id=self.get_asignatura_id())
        return queryset

    def validate_write_scope(self, data, instance=None):
        asignatura = data.get(
            "asignatura",
            instance.asignatura if instance is not None else None,
        )
        self.ensure_assigned_subject(asignatura)

    def belongs_to_assigned_subject(self, obj):
        return obj.asignatura_id == self.get_asignatura_id()


class AsistenciaEstudianteViewSet(ProfesorAsignaturaViewSet):
    queryset = AsistenciaEstudiante.objects.all()
    serializer_class = AsistenciaEstudianteSerializer
    filterset_fields = ("asistencia", "estudiante", "presente")
    search_fields = (
        "asistencia__asignatura__nombre",
        "estudiante__nombres",
        "estudiante__primerApellido",
        "estudiante__segundoApellido",
    )

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.action == "list":
            return queryset.filter(
                asistencia__asignatura_id=self.get_asignatura_id()
            )
        return queryset

    def validate_write_scope(self, data, instance=None):
        asistencia = data.get(
            "asistencia",
            instance.asistencia if instance is not None else None,
        )
        estudiante = data.get(
            "estudiante",
            instance.estudiante if instance is not None else None,
        )
        asignatura = asistencia.asignatura if asistencia is not None else None
        self.ensure_assigned_subject(asignatura)
        if estudiante is None or not asignatura.estudiantes.filter(
            pk=estudiante.pk
        ).exists():
            raise PermissionDenied(PERMISSION_DENIED_MESSAGE)

    def belongs_to_assigned_subject(self, obj):
        return (
            obj.asistencia.asignatura_id == self.get_asignatura_id()
            and obj.asistencia.asignatura.estudiantes.filter(
                pk=obj.estudiante_id
            ).exists()
        )


class TipoCompetenciaViewSet(RolViewSet):
    queryset = TipoCompetencia.objects.all()
    serializer_class = TipoCompetenciaSerializer
    filterset_fields = ("nombreTipoCompetencia",)
    search_fields = ("nombreTipoCompetencia",)


class CompetenciaViewSet(RolViewSet):
    queryset = Competencia.objects.all()
    serializer_class = CompetenciaSerializer
    required_role = Usuario.Rol.PSICOLOGO
    filterset_fields = ("tipoCompetencia", "estudiante")
    search_fields = (
        "nombreCompetencia",
        "descripcion",
        "tipoCompetencia__nombreTipoCompetencia",
        "estudiante__nombres",
        "estudiante__primerApellido",
        "estudiante__segundoApellido",
    )


class EvaluacionesViewSet(ProfesorAsignaturaViewSet):
    queryset = Evaluaciones.objects.all()
    serializer_class = EvaluacionesSerializer
    filterset_fields = ("asignatura", "estudiante", "nota")
    search_fields = (
        "asignatura__nombre",
        "estudiante__nombres",
        "estudiante__primerApellido",
        "estudiante__segundoApellido",
    )

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.action == "list":
            return queryset.filter(asignatura_id=self.get_asignatura_id())
        return queryset

    def validate_write_scope(self, data, instance=None):
        asignatura = data.get(
            "asignatura",
            instance.asignatura if instance is not None else None,
        )
        estudiante = data.get(
            "estudiante",
            instance.estudiante if instance is not None else None,
        )
        self.ensure_assigned_subject(asignatura)
        if estudiante is None or not asignatura.estudiantes.filter(
            pk=estudiante.pk
        ).exists():
            raise PermissionDenied(PERMISSION_DENIED_MESSAGE)

    def belongs_to_assigned_subject(self, obj):
        return (
            obj.asignatura_id == self.get_asignatura_id()
            and obj.asignatura.estudiantes.filter(pk=obj.estudiante_id).exists()
        )
