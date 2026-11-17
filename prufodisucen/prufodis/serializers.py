from collections.abc import Mapping

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


class DocumentoEstudianteSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentoEstudiante
        fields = "__all__"


class AsignaturaSerializer(serializers.ModelSerializer):
    estudiantes = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Estudiante.objects.all(),
        required=False,
    )

    class Meta:
        model = Asignatura
        fields = '__all__'

    def to_internal_value(self, data):
        if (
            isinstance(data, Mapping)
            and data.get("estudiantes", serializers.empty) is None
        ):
            data = data.copy()
            data["estudiantes"] = []

        return super().to_internal_value(data)

    def validate(self, attrs):
        asignatura = self.instance or Asignatura()
        for campo in ("cantidadNotas", "porcentajeNotas"):
            if campo in attrs:
                setattr(asignatura, campo, attrs[campo])

        try:
            asignatura.clean()
        except DjangoValidationError as error:
            raise serializers.ValidationError(error.message_dict) from error

        return attrs

class DocumentoAsignaturaSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentoAsignatura
        fields = "__all__"

class AsistenciaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Asistencia
        fields = '__all__'

    def validate(self, attrs):
        asistencia = self.instance or Asistencia()
        for campo in ("horaInicio", "horaFin"):
            if campo in attrs:
                setattr(asistencia, campo, attrs[campo])

        try:
            asistencia.clean()
        except DjangoValidationError as error:
            raise serializers.ValidationError(error.message_dict) from error

        return attrs

class AsistenciaEstudianteSerializer(serializers.ModelSerializer):
    class Meta:
        model = AsistenciaEstudiante
        fields = '__all__'

class TipoCompetenciaSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoCompetencia
        fields = '__all__'

class CompetenciaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Competencia
        fields = '__all__'

class EvaluacionesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Evaluaciones
        fields = '__all__'

    def validate(self, attrs):
        evaluacion = self.instance or Evaluaciones()
        for campo in ("nota", "asignatura"):
            if campo in attrs:
                setattr(evaluacion, campo, attrs[campo])

        try:
            evaluacion.clean()
        except DjangoValidationError as error:
            raise serializers.ValidationError(error.message_dict) from error

        return attrs
