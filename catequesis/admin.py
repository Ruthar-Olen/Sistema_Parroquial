from django.contrib import admin
from .models import Catequista, GrupoCatequesis


@admin.register(Catequista)
class CatequistaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')
    search_fields = ('nombre',)


@admin.register(GrupoCatequesis)
class GrupoCatequesisAdmin(admin.ModelAdmin):
    list_display = ('id', 'numero_grupo', 'catequista', 'lugar', 'dia')
    search_fields = ('numero_grupo', 'catequista__nombre', 'lugar', 'dia')
    list_filter = ('dia',)