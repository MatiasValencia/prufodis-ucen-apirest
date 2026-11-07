from .models import Alumno
from .serializers import AlumnoSerializer
from rest_framework import viewsets

# Create your views here.
class AlumnoViewSet(viewsets.ModelViewSet):
    queryset = Alumno.objects.all()
    serializer_class = AlumnoSerializer