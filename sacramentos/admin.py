from django.contrib import admin
from .models import Inscripcion


@admin.register(Inscripcion)
class InscripcionAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre_completo', 'tipo', 'fecha', 'telefono')
    search_fields = ('nombre_completo', 'telefono')
    list_filter = ('tipo', 'fecha')
    

# Register your models here.
