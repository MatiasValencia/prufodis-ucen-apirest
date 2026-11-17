from django.conf import settings
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
    asignaturas = models.ManyToManyField(
        "prufodis.Asignatura",
        blank=True,
        related_name="profesores",
    )

    def __str__(self):
        return f"{self.usuario.get_full_name() or self.usuario.username} ({self.get_rol_display()})"
