from .models import *
from .serializers import *
from rest_framework import viewsets
from rest_framework.exceptions import ValidationError as APIValidationError
from rest_framework.parsers import FormParser, MultiPartParser

# Create your views here.
class EstudianteViewSet(viewsets.ModelViewSet):
    queryset = Estudiante.objects.all()
    serializer_class = EstudianteSerializer


class DocumentoEstudianteViewSet(viewsets.ModelViewSet):
    queryset = DocumentoEstudiante.objects.all()
    serializer_class = DocumentoEstudianteSerializer
    parser_classes = [MultiPartParser, FormParser]

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


class AsignaturaViewSet(viewsets.ModelViewSet):
    queryset = Asignatura.objects.all()
    serializer_class = AsignaturaSerializer

class DocumentoAsignaturaViewSet(viewsets.ModelViewSet):
    queryset = DocumentoAsignatura.objects.all()
    serializer_class = DocumentoAsignaturaSerializer
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        queryset = super().get_queryset()
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


class AsistenciaViewSet(viewsets.ModelViewSet):
    queryset = Asistencia.objects.all()
    serializer_class = AsistenciaSerializer

class AsistenciaEstudianteViewSet(viewsets.ModelViewSet):
    queryset = AsistenciaEstudiante.objects.all()
    serializer_class = AsistenciaEstudianteSerializer

class TipoCompetenciaViewSet(viewsets.ModelViewSet):
    queryset = TipoCompetencia.objects.all()
    serializer_class = TipoCompetenciaSerializer

class CompetenciaViewSet(viewsets.ModelViewSet):
    queryset = Competencia.objects.all()
    serializer_class = CompetenciaSerializer

class EvaluacionesViewSet(viewsets.ModelViewSet):
    queryset = Evaluaciones.objects.all()
    serializer_class = EvaluacionesSerializer