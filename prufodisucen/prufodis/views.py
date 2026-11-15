from .models import *
from .serializers import *
from rest_framework import viewsets

# Create your views here.
class EstudianteViewSet(viewsets.ModelViewSet):
    queryset = Estudiante.objects.all()
    serializer_class = EstudianteSerializer

class AsignaturaViewSet(viewsets.ModelViewSet):
    queryset = Asignatura.objects.all()
    serializer_class = AsignaturaSerializer

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