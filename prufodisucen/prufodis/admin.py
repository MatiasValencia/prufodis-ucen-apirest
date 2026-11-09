from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Estudiante)
admin.site.register(Asignatura)
admin.site.register(Asistencia)
admin.site.register(AsistenciaEstudiante)
admin.site.register(Habilidades)
admin.site.register(Evaluaciones)