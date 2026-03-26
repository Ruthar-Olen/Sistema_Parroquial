from django.urls import path  # Importa path para definir rutas
from .views import (  # Importa las vistas del módulo
    crear_inscripcion,
    lista_inscripciones,
    editar_inscripcion,
    eliminar_inscripcion,
    detalle_inscripcion,
    reporte_inscripciones,
    exportar_inscripciones_csv,
    exportar_inscripciones_excel,
    exportar_expediente_pdf,
    exportar_reporte_grupos_pdf,
    seleccionar_formato_inscripcion,
    generar_formato_pdf,
)

urlpatterns = [
    path('nueva/', crear_inscripcion, name='crear_inscripcion'),  # Crear inscripción
    path('lista/', lista_inscripciones, name='lista_inscripciones'),  # Lista operativa
    path('reporte/', reporte_inscripciones, name='reporte_inscripciones'),  # Reporte agrupado en pantalla
    path('exportar/csv/', exportar_inscripciones_csv, name='exportar_inscripciones_csv'),  # Exportar CSV
    path('exportar/excel/', exportar_inscripciones_excel, name='exportar_inscripciones_excel'),  # Exportar Excel
    path('exportar/reporte-grupos-pdf/', exportar_reporte_grupos_pdf, name='exportar_reporte_grupos_pdf'),  # PDF formal por grupos
    path('detalle/<int:pk>/', detalle_inscripcion, name='detalle_inscripcion'),  # Detalle individual
    path('detalle/<int:pk>/pdf/', exportar_expediente_pdf, name='exportar_expediente_pdf'),  # PDF individual bonito
    path('editar/<int:pk>/', editar_inscripcion, name='editar_inscripcion'),  # Editar inscripción
    path('eliminar/<int:pk>/', eliminar_inscripcion, name='eliminar_inscripcion'),  # Eliminar inscripción
    path('formatos/<int:pk>/', seleccionar_formato_inscripcion, name='seleccionar_formato_inscripcion'),  # Pantalla para elegir formato
    path('formatos/<int:pk>/<str:clave_tipo>/pdf/', generar_formato_pdf, name='generar_formato_pdf'),  # Genera el PDF del formato elegido
]