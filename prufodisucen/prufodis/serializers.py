from rest_framework import serializers
from .models import *

class EstudianteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Estudiante
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

class HabilidadesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Habilidades
        fields = '__all__'

class EvaluacionesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Evaluaciones
        fields = '__all__'