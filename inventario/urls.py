from django.urls import path  # Importa path para definir rutas
from .views import lista_bienes, crear_bien  # Importa vistas del módulo inventario


urlpatterns = [
    path('', lista_bienes, name='lista_bienes'),  # Ruta principal del inventario
    path('nuevo/', crear_bien, name='crear_bien'),  # Ruta para dar de alta un bien nuevo
]