from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Estudiante)
admin.site.register(DocumentoEstudiante)
admin.site.register(Asignatura)
admin.site.register(DocumentoAsignatura)
admin.site.register(Asistencia)
admin.site.register(AsistenciaEstudiante)
admin.site.register(TipoCompetencia)
admin.site.register(Competencia)
admin.site.register(Evaluaciones)