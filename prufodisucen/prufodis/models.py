from decimal import Decimal

from django.core.exceptions import ValidationError
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


class DocumentoEstudiante(models.Model):
    estudiante = models.ForeignKey(
        Estudiante,
        on_delete=models.CASCADE,
        related_name="documentos",
    )
    archivo = models.FileField(
        upload_to="antecedentes_estudiantes/",
        validators=[
            FileExtensionValidator(
                allowed_extensions=[
                    "pdf",
                    "doc",
                    "docx",
                    "xls",
                    "xlsx",
                    "ppt",
                    "pptx",
                    "odt",
                    "ods",
                    "odp",
                    "rtf",
                    "txt",
                    "csv",
                ]
            )
        ],
    )
    fechaSubida = models.DateTimeField(auto_now_add=True)


class Asignatura(models.Model):
    nombre = models.CharField(max_length=100)
    cantidadNotas = models.IntegerField()
    porcentajeNotas = models.JSONField(default=list)
    estudiantes = models.ManyToManyField(
        Estudiante
    )

    def clean(self):
        super().clean()

        if (
            not isinstance(self.cantidadNotas, int)
            or isinstance(self.cantidadNotas, bool)
            or self.cantidadNotas <= 0
        ):
            raise ValidationError({
                "cantidadNotas": "Ingrese una cantidad válida de notas, mayor a 0"
            })

        porcentajes = self.porcentajeNotas
        es_lista_numerica = isinstance(porcentajes, list) and all(
            isinstance(porcentaje, (int, float))
            and not isinstance(porcentaje, bool)
            for porcentaje in porcentajes
        )
        total_es_100 = es_lista_numerica and sum(
            (Decimal(str(porcentaje)) for porcentaje in porcentajes),
            Decimal("0"),
        ) == Decimal("100")
        cantidad_coincide = (
            isinstance(porcentajes, list)
            and len(porcentajes) == self.cantidadNotas
        )

        if not cantidad_coincide and not total_es_100:
            mensaje = (
                "La cantidad de porcentajes y cantidad de notas deben coincidir, "
                "y también deben sumar 100."
            )
        elif not cantidad_coincide:
            mensaje = (
                "La cantidad de porcentajes debe ser la misma cantidad de notas "
                "de la asignatura."
            )
        elif not total_es_100:
            mensaje = "El total de los porcentajes debe ser 100."
        else:
            return

        raise ValidationError({"porcentajeNotas": mensaje})

class DocumentoAsignatura(models.Model):
    asignatura = models.ForeignKey(
        Asignatura,
        on_delete=models.CASCADE,
        related_name="documentos",
    )
    archivo = models.FileField(
        upload_to="recursos_asignatura/",
        validators=[
            FileExtensionValidator(
                allowed_extensions=[
                    "pdf",
                    "doc",
                    "docx",
                    "xls",
                    "xlsx",
                    "ppt",
                    "pptx",
                    "odt",
                    "ods",
                    "odp",
                    "rtf",
                    "txt",
                    "csv",
                ]
            )
        ],
    )
    fechaSubida = models.DateTimeField(auto_now_add=True)

class Asistencia(models.Model):
    asignatura = models.ForeignKey(Asignatura, on_delete=models.CASCADE)
    fecha = models.DateField()
    horaInicio = models.TimeField()
    horaFin = models.TimeField()
    estudiantes = models.ManyToManyField(
        Estudiante,
        through="AsistenciaEstudiante",
    )

    def clean(self):
        super().clean()

        if (
            self.horaInicio is not None
            and self.horaFin is not None
            and self.horaFin <= self.horaInicio
        ):
            raise ValidationError({
                "horaFin": (
                    "La hora de fin de la clase debe ser mayor a la hora de inicio"
                )
            })

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

class TipoCompetencia(models.Model):
    nombreTipoCompetencia = models.CharField(max_length=100)

class Competencia(models.Model):
    nombreCompetencia = models.CharField(max_length=100)
    tipoCompetencia = models.ForeignKey(TipoCompetencia, on_delete=models.CASCADE)
    estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE)
    descripcion = models.TextField()

class Evaluaciones(models.Model):
    asignatura = models.ForeignKey(Asignatura, on_delete=models.CASCADE)
    estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE)
    nota = models.DecimalField(max_digits=10, decimal_places=1)

    def clean(self):
        super().clean()

        if (
            self.nota is not None
            and not Decimal("1.0") <= self.nota <= Decimal("7.0")
        ):
            raise ValidationError({
                "nota": "La nota debe ser entre un 1.0 y un 7.0"
            })

        if self.asignatura_id is None:
            return

        asignatura_anterior_id = None
        if not self._state.adding:
            asignatura_anterior_id = (
                type(self).objects.filter(pk=self.pk)
                .values_list("asignatura_id", flat=True)
                .first()
            )

        if asignatura_anterior_id == self.asignatura_id:
            return

        if (
            type(self).objects.filter(asignatura_id=self.asignatura_id).count()
            >= self.asignatura.cantidadNotas
        ):
            raise ValidationError({
                "asignatura": "No se pueden agregar más notas"
            })