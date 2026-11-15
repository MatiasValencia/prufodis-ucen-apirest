from django.db import models
from django.core.validators import FileExtensionValidator, RegexValidator

# Create your models here.
REQUIRED_FIELD_ERROR = "Favor de rellenar todos los campos del formulario."


class Estudiante(models.Model):
    nombres = models.CharField(
        max_length=100,
        error_messages={
            "blank": REQUIRED_FIELD_ERROR,
            "null": REQUIRED_FIELD_ERROR,
        },
    )
    primerApellido = models.CharField(
        max_length=100,
        error_messages={
            "blank": REQUIRED_FIELD_ERROR,
            "null": REQUIRED_FIELD_ERROR,
        },
    )
    segundoApellido = models.CharField(
        max_length=100,
        error_messages={
            "blank": REQUIRED_FIELD_ERROR,
            "null": REQUIRED_FIELD_ERROR,
        },
    )
    rut = models.CharField(
        max_length=10,
        unique=True,
        validators=[
            RegexValidator(
                regex=r"^[0-9]{7,8}-[0-9K]\Z",
                message="Ingrese un RUT válido.",
            )
        ],
        error_messages={
            "blank": REQUIRED_FIELD_ERROR,
            "null": REQUIRED_FIELD_ERROR,
            "unique": "Este RUT ya está registrado.",
        },
    )
    apoderado = models.CharField(
        max_length=100,
        error_messages={
            "blank": REQUIRED_FIELD_ERROR,
            "null": REQUIRED_FIELD_ERROR,
        },
    )
    telefono = models.CharField(
        max_length=9,
        unique=True,
        validators=[
            RegexValidator(
                regex=r"^[0-9]{9}\Z",
                message="Inserte un número de teléfono de 9 dígitos.",
            )
        ],
        error_messages={
            "blank": REQUIRED_FIELD_ERROR,
            "null": REQUIRED_FIELD_ERROR,
            "unique": "Este teléfono ya está registrado.",
        },
    )
    fotografia = models.ImageField(
        upload_to="estudiantes/",
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=["jpg", "png"])],
    )

class Asignatura(models.Model):
    nombre = models.CharField(max_length=100)
    cantidadNotas = models.IntegerField()
    porcentajeNotas = models.JSONField(default=list)
    estudiantes = models.ManyToManyField(
        Estudiante
    )

class Asistencia(models.Model):
    asignatura = models.ForeignKey(Asignatura, on_delete=models.CASCADE)
    fecha = models.DateField()
    horaInicio = models.TimeField()
    horaFin = models.TimeField()
    estudiantes = models.ManyToManyField(
        Estudiante,
        through="AsistenciaEstudiante",
    )

class AsistenciaEstudiante(models.Model):
    asistencia = models.ForeignKey(Asistencia, on_delete=models.CASCADE)
    estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE)
    presente = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["asistencia", "estudiante"],
                name="unique_asistencia_estudiante",
            )
        ]

class Habilidades(models.Model):
    nombreHabilidad = models.CharField(max_length=100)
    descripcion = models.TextField()
    estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE)

class Evaluaciones(models.Model):
    asignatura = models.ForeignKey(Asignatura, on_delete=models.CASCADE)
    estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE)
    nota = models.DecimalField(max_digits=2, decimal_places=1)