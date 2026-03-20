from django.urls import path
from .views import (
    crear_inscripcion,
    lista_inscripciones,
    editar_inscripcion,
    eliminar_inscripcion,
    detalle_inscripcion,
)

urlpatterns = [
    path('nueva/', crear_inscripcion, name='crear_inscripcion'),
    path('lista/', lista_inscripciones, name='lista_inscripciones'),
    path('detalle/<int:pk>/', detalle_inscripcion, name='detalle_inscripcion'),
    path('editar/<int:pk>/', editar_inscripcion, name='editar_inscripcion'),
    path('eliminar/<int:pk>/', eliminar_inscripcion, name='eliminar_inscripcion'),
]