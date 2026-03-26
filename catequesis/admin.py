from django.contrib import admin  # Importa herramientas de administración de Django
from .models import (
    Catequista,
    GrupoCatequesis,
    HorarioCatequesis,
    FormatoTipo,
    FormatoCatequesis,
    FormatoCelda
)  # Importa todos los modelos del módulo


@admin.register(Catequista)
class CatequistaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')  # Campos visibles en listado
    search_fields = ('nombre',)  # Permite búsqueda por nombre


@admin.register(GrupoCatequesis)
class GrupoCatequesisAdmin(admin.ModelAdmin):
    list_display = ('id', 'numero_grupo', 'catequista', 'lugar', 'dia')  # Campos visibles
    search_fields = ('numero_grupo', 'catequista__nombre', 'lugar', 'dia')  # Búsqueda
    list_filter = ('dia',)  # Filtro lateral por día


@admin.register(HorarioCatequesis)
class HorarioCatequesisAdmin(admin.ModelAdmin):
    list_display = ('id', 'grupo', 'hora_inicio', 'hora_fin')  # Campos visibles
    search_fields = ('grupo__numero_grupo',)  # Búsqueda por grupo


@admin.register(FormatoTipo)
class FormatoTipoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'clave', 'activo')  # Campos visibles
    search_fields = ('nombre', 'clave')  # Búsqueda por nombre o clave
    list_filter = ('activo',)  # Filtro por estado activo


class FormatoCeldaInline(admin.TabularInline):
    model = FormatoCelda  # Modelo que se mostrará en línea
    extra = 5  # Número de filas vacías para agregar rápidamente
    fields = ('fila', 'columna', 'contenido', 'destacado', 'orden')  # Campos visibles en línea
    ordering = ('fila', 'columna')  # Orden natural de la cuadrícula


@admin.register(FormatoCatequesis)
class FormatoCatequesisAdmin(admin.ModelAdmin):
    list_display = ('id', 'tipo', 'ciclo', 'titulo', 'orientacion', 'activo')  # Campos visibles
    search_fields = ('titulo', 'ciclo', 'tipo__nombre')  # Búsqueda
    list_filter = ('tipo', 'orientacion', 'activo')  # Filtros laterales

    inlines = [FormatoCeldaInline]  # Permite editar celdas directamente dentro del formato

    fieldsets = (
        ('Información general', {
            'fields': ('tipo', 'ciclo', 'titulo', 'subtitulo')
        }),  # Datos básicos del formato

        ('Configuración del documento', {
            'fields': ('orientacion', 'activo', 'usa_celdas')
        }),  # Configuración general

        ('Contenido', {
            'fields': ('texto_pie',)
        }),  # Texto inferior del formato
    )