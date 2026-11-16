from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from .models import Usuario

class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = "__all__"

    def validate(self, attrs):
        perfil = self.instance or Usuario()
        for campo in ("rol", "asignatura"):
            if campo in attrs:
                setattr(perfil, campo, attrs[campo])

        try:
            perfil.clean()
        except DjangoValidationError as error:
            raise serializers.ValidationError(error.message_dict) from error

        return attrs