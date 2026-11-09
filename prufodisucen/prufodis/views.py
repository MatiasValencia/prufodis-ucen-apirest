from .models import *
from .serializers import *
from rest_framework import viewsets

# Create your views here.
class AlumnoViewSet(viewsets.ModelViewSet):
    queryset = Alumno.objects.all()
    serializer_class = AlumnoSerializer

class AsignaturaViewSet(viewsets.ModelViewSet):
    queryset = Asignatura.objects.all()
    serializer_class = AsignaturaSerializer

class AsistenciaViewSet(viewsets.ModelViewSet):
    queryset = Asistencia.objects.all()
    serializer_class = AsistenciaSerializer

class AsistenciaEstudianteViewSet(viewsets.ModelViewSet):
    queryset = AsistenciaEstudiante.objects.all()
    serializer_class = AsistenciaEstudianteSerializer

class HabilidadesViewSet(viewsets.ModelViewSet):
    queryset = Habilidades.objects.all()
    serializer_class = HabilidadesSerializer

class EvaluacionesViewSet(viewsets.ModelViewSet):
    queryset = Evaluaciones.objects.all()
    serializer_class = EvaluacionesSerializer