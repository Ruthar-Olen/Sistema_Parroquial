from django.urls import path  # Importa path para definir rutas
from .views import editor_oficio  # Importa la vista principal del módulo

urlpatterns = [
    path('', editor_oficio, name='editor_oficio'),  # Ruta principal del editor de oficios
]