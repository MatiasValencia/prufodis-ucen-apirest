from django.db import models
from django.core.validators import FileExtensionValidator

# Create your models here.
class Alumno(models.Model):
    nombres = models.CharField(max_length=100)
    primerApellido = models.CharField(max_length=100)
    segundoApellido = models.CharField(max_length=100)
    rut = models.CharField(max_length=10)
    apoderado = models.CharField(max_length=100)
    telefono = models.IntegerField()
    fotografia = models.ImageField(
        upload_to="alumnos/",
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=["jpg", "png"])],
    )

class Asignatura(models.Model):
    nombre = models.CharField(max_length=100)
    cantidadNotas = models.IntegerField()
    porcentajeNotas = models.JSONField(default=list)
    estudiantes = models.ManyToManyField(
        Alumno
    )

class Asistencia(models.Model):
    asignatura = models.ForeignKey(Asignatura, on_delete=models.CASCADE)
    fecha = models.DateField()
    horaInicio = models.TimeField()
    horaFin = models.TimeField()
    estudiantes = models.ManyToManyField(
        Alumno,
        through="AsistenciaEstudiante",
    )

class AsistenciaEstudiante(models.Model):
    asistencia = models.ForeignKey(Asistencia, on_delete=models.CASCADE)
    estudiante = models.ForeignKey(Alumno, on_delete=models.CASCADE)
    presente = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["asistencia", "estudiante"],
                name="unique_asistencia_estudiante",
            )
        ]