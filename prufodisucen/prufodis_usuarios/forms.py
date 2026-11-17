from django import forms
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .models import Usuario

UserModel = get_user_model()


class UsuarioInlineForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = "__all__"

    def clean(self):
        cleaned_data = super().clean()
        rol = cleaned_data.get("rol")
        asignaturas = cleaned_data.get("asignaturas")

        if rol == Usuario.Rol.PROFESOR and not asignaturas:
            self.add_error(
                "asignaturas",
                "Todo profesor debe tener al menos una asignatura asignada.",
            )
        elif rol != Usuario.Rol.PROFESOR and asignaturas:
            self.add_error(
                "asignaturas",
                "Solo los profesores pueden tener asignaturas.",
            )

        return cleaned_data


class EmailAuthenticationForm(AuthenticationForm):
    email = forms.EmailField(
        label=_("Email"),
        max_length=254,
        widget=forms.EmailInput(attrs={"autofocus": True, "autocomplete": "email"}),
    )

    def __init__(self, request=None, *args, **kwargs):
        super().__init__(request, *args, **kwargs)
        self.fields.pop("username")

    def clean(self):
        email = self.cleaned_data.get("email")
        password = self.cleaned_data.get("password")

        if email and password:
            users = list(
                UserModel._default_manager.filter(email__iexact=email)[:2]
            )
            if len(users) == 1:
                self.user_cache = authenticate(
                    self.request,
                    username=users[0].get_username(),
                    password=password,
                )

            if self.user_cache is None:
                raise self.get_invalid_login_error()

            self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data

    def get_invalid_login_error(self):
        return ValidationError(
            self.error_messages["invalid_login"],
            code="invalid_login",
            params={"username": _("email address")},
        )
