from django.contrib import admin  # Importa el módulo de administración de Django
from .models import AreaInventario, EstadoInventario, BienInventario  # Importa los modelos del módulo inventario


@admin.register(AreaInventario)
class AreaInventarioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'prefijo', 'activa')  # Columnas visibles en la lista del admin
    search_fields = ('nombre', 'prefijo')  # Permite buscar por nombre o prefijo
    list_filter = ('activa',)  # Agrega filtro lateral por activa/inactiva
    ordering = ('nombre',)  # Ordena por nombre


@admin.register(EstadoInventario)
class EstadoInventarioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'activo')  # Columnas visibles en la lista del admin
    search_fields = ('nombre',)  # Permite buscar por nombre
    list_filter = ('activo',)  # Filtro lateral por activo/inactivo
    ordering = ('nombre',)  # Orden alfabético


@admin.register(BienInventario)
class BienInventarioAdmin(admin.ModelAdmin):
    list_display = (
        'codigo',
        'descripcion_corta',
        'area',
        'estado',
        'cantidad',
        'activo',
        'fecha_alta',
    )  # Columnas visibles en el admin

    search_fields = (
        'codigo',
        'descripcion',
        'observaciones',
        'area__nombre',
        'estado__nombre',
    )  # Campos donde se puede buscar

    list_filter = (
        'activo',
        'area',
        'estado',
        'fecha_alta',
    )  # Filtros laterales

    ordering = ('-fecha_alta', 'codigo')  # Ordena por fecha más reciente
    autocomplete_fields = ('area', 'estado')  # Hace más cómodo elegir relaciones si hay muchos registros

    def descripcion_corta(self, obj):
        return obj.descripcion[:60] + ('...' if len(obj.descripcion) > 60 else '')  # Recorta la descripción para que no se vea enorme

    descripcion_corta.short_description = 'Descripción'  # Nombre visible de la columna