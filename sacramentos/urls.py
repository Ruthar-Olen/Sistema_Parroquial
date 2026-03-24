from django.urls import path
from .views import (
    crear_inscripcion,
    lista_inscripciones,
    editar_inscripcion,
    eliminar_inscripcion,
    detalle_inscripcion,
    reporte_inscripciones,
    exportar_inscripciones_csv,
    exportar_inscripciones_excel,
)

urlpatterns = [
    path('nueva/', crear_inscripcion, name='crear_inscripcion'),
    path('lista/', lista_inscripciones, name='lista_inscripciones'),
    path('reporte/', reporte_inscripciones, name='reporte_inscripciones'),
    path('exportar/csv/', exportar_inscripciones_csv, name='exportar_inscripciones_csv'),
    path('exportar/excel/', exportar_inscripciones_excel, name='exportar_inscripciones_excel'),
    path('detalle/<int:pk>/', detalle_inscripcion, name='detalle_inscripcion'),
    path('editar/<int:pk>/', editar_inscripcion, name='editar_inscripcion'),
    path('eliminar/<int:pk>/', eliminar_inscripcion, name='eliminar_inscripcion'),
]