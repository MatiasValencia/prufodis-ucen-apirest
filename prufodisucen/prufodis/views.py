from .models import Alumno, Asignatura
from .serializers import AlumnoSerializer, AsignaturaSerializer
from rest_framework import viewsets

# Create your views here.
class AlumnoViewSet(viewsets.ModelViewSet):
    queryset = Alumno.objects.all()
    serializer_class = AlumnoSerializer

class AsignaturaViewSet(viewsets.ModelViewSet):
    queryset = Asignatura.objects.all()
    serializer_class = AsignaturaSerializer