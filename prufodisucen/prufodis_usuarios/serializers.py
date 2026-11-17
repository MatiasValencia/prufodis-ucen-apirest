from rest_framework import serializers

from .models import Usuario


class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = "__all__"

    def validate(self, attrs):
        perfil = self.instance or Usuario()
        rol = attrs.get("rol", perfil.rol)
        if "asignaturas" in attrs:
            asignaturas = attrs["asignaturas"]
        elif self.instance is not None and self.instance.pk:
            asignaturas = self.instance.asignaturas.all()
        else:
            asignaturas = ()

        tiene_asignaturas = bool(asignaturas)
        if rol == Usuario.Rol.PROFESOR and not tiene_asignaturas:
            raise serializers.ValidationError({
                "asignaturas": (
                    "Todo profesor debe tener al menos una asignatura asignada."
                )
            })
        if rol != Usuario.Rol.PROFESOR and tiene_asignaturas:
            raise serializers.ValidationError({
                "asignaturas": "Solo los profesores pueden tener asignaturas."
            })

        return attrs
