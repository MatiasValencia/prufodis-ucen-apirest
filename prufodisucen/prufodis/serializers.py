from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers
from .models import *

class EstudianteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Estudiante
        fields = '__all__'
        extra_kwargs = {
            field: {
                "error_messages": {
                    "blank": REQUIRED_FIELD_ERROR,
                    "null": REQUIRED_FIELD_ERROR,
                    "required": REQUIRED_FIELD_ERROR,
                }
            }
            for field in (
                "nombres",
                "primerApellido",
                "segundoApellido",
                "rut",
                "apoderado",
                "telefono",
            )
        }

class AsignaturaSerializer(serializers.ModelSerializer):
    estudiantes = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Estudiante.objects.all(),
        allow_empty=False,
        error_messages={
            "empty": "La asignatura debe tener al menos un estudiante."
        },
    )

    class Meta:
        model = Asignatura
        fields = '__all__'

    def validate(self, attrs):
        asignatura = self.instance or Asignatura()
        for campo in ("cantidadNotas", "porcentajeNotas"):
            if campo in attrs:
                setattr(asignatura, campo, attrs[campo])

        try:
            asignatura.clean()
        except DjangoValidationError as error:
            raise serializers.ValidationError(error.message_dict) from error

        if (
            self.instance is not None
            and "estudiantes" not in attrs
            and not self.instance.estudiantes.exists()
        ):
            raise serializers.ValidationError({
                "estudiantes": "La asignatura debe tener al menos un estudiante."
            })

        return attrs

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
