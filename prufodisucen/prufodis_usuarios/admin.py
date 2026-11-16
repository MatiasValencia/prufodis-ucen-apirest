from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .models import Usuario


class UsuarioInline(admin.StackedInline):
    model = Usuario
    can_delete = False
    extra = 1


class UsuarioAdmin(UserAdmin):
    inlines = (*UserAdmin.inlines, UsuarioInline)

admin.site.unregister(get_user_model())
admin.site.register(get_user_model(), UsuarioAdmin)
