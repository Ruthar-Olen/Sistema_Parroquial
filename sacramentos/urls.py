from django.urls import path  # Importa path para definir rutas
from .views import (  # Importa todas las vistas que usará este módulo
    crear_inscripcion,
    lista_inscripciones,
    editar_inscripcion,
    eliminar_inscripcion,
    detalle_inscripcion,
    reporte_inscripciones,
    exportar_inscripciones_csv,
    exportar_inscripciones_excel,
    exportar_expediente_pdf,
)

urlpatterns = [
    path('nueva/', crear_inscripcion, name='crear_inscripcion'),  # Ruta para crear inscripción
    path('lista/', lista_inscripciones, name='lista_inscripciones'),  # Ruta para lista resumida
    path('reporte/', reporte_inscripciones, name='reporte_inscripciones'),  # Ruta para reporte agrupado
    path('exportar/csv/', exportar_inscripciones_csv, name='exportar_inscripciones_csv'),  # Exportación CSV
    path('exportar/excel/', exportar_inscripciones_excel, name='exportar_inscripciones_excel'),  # Exportación Excel
    path('detalle/<int:pk>/', detalle_inscripcion, name='detalle_inscripcion'),  # Detalle individual
    path('detalle/<int:pk>/pdf/', exportar_expediente_pdf, name='exportar_expediente_pdf'),  # PDF bonito individual
    path('editar/<int:pk>/', editar_inscripcion, name='editar_inscripcion'),  # Editar inscripción
    path('eliminar/<int:pk>/', eliminar_inscripcion, name='eliminar_inscripcion'),  # Eliminar inscripción
]