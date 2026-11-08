from rest_framework import serializers
from .models import *

class AlumnoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alumno
        fields = '__all__'

class AsignaturaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Asignatura
        fields = '__all__'

class AsistenciaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Asistencia
        fields = '__all__'

class AsistenciaEstudianteSerializer(serializers.ModelSerializer):
    class Meta:
        model = AsistenciaEstudiante
        fields = '__all__'