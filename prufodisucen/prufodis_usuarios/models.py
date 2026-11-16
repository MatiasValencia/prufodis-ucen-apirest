from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class Usuario(models.Model):
    class Rol(models.TextChoices):
        ADMINISTRADOR = "administrador", "Administrador"
        PROFESOR = "profesor", "Profesor"
        PSICOLOGO = "psicologo", "Psicólogo"

    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="perfil",
    )
    rol = models.CharField(max_length=20, choices=Rol.choices)
    asignatura = models.ForeignKey(
        "prufodis.Asignatura",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="profesores",
    )

    def clean(self):
        super().clean()

        if self.rol == self.Rol.PROFESOR and self.asignatura_id is None:
            raise ValidationError({
                "asignatura": "Todo profesor debe tener una asignatura asignada."
            })

        if self.rol != self.Rol.PROFESOR and self.asignatura_id is not None:
            raise ValidationError({
                "asignatura": "Solo los profesores pueden tener una asignatura."
            })

    def __str__(self):
        return f"{self.usuario.get_full_name() or self.usuario.username} ({self.get_rol_display()})"
