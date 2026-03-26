from django.urls import path  # Importa path para definir rutas
from .views import (
    menu_catequesis,  # Vista principal del módulo

    lista_catequistas, crear_catequista, editar_catequista, eliminar_catequista,  # Vistas de catequistas
    lista_grupos, crear_grupo, editar_grupo, eliminar_grupo,  # Vistas de grupos
    lista_horarios, crear_horario, editar_horario, eliminar_horario,  # Vistas de horarios

    grupos_por_catequista, horarios_por_grupo,  # APIs internas para sacramentos

    lista_formatos,  # Vista de lista de formatos
    editar_formato,  # Vista para editar un formato
    preview_formato,  # Vista para mostrar la vista previa del formato
)

urlpatterns = [
    path('', menu_catequesis, name='menu_catequesis'),  # Menú principal de catequesis

    path('catequistas/', lista_catequistas, name='lista_catequistas'),  # Lista de catequistas
    path('catequistas/nuevo/', crear_catequista, name='crear_catequista'),  # Crear catequista
    path('catequistas/editar/<int:pk>/', editar_catequista, name='editar_catequista'),  # Editar catequista
    path('catequistas/eliminar/<int:pk>/', eliminar_catequista, name='eliminar_catequista'),  # Eliminar catequista

    path('grupos/', lista_grupos, name='lista_grupos'),  # Lista de grupos
    path('grupos/nuevo/', crear_grupo, name='crear_grupo'),  # Crear grupo
    path('grupos/editar/<int:pk>/', editar_grupo, name='editar_grupo'),  # Editar grupo
    path('grupos/eliminar/<int:pk>/', eliminar_grupo, name='eliminar_grupo'),  # Eliminar grupo

    path('horarios/', lista_horarios, name='lista_horarios'),  # Lista de horarios
    path('horarios/nuevo/', crear_horario, name='crear_horario'),  # Crear horario
    path('horarios/editar/<int:pk>/', editar_horario, name='editar_horario'),  # Editar horario
    path('horarios/eliminar/<int:pk>/', eliminar_horario, name='eliminar_horario'),  # Eliminar horario

    path('formatos/', lista_formatos, name='lista_formatos'),  # Lista de formatos
    path('formatos/editar/<int:pk>/', editar_formato, name='editar_formato'),  # Editar formato
    path('formatos/preview/<int:pk>/', preview_formato, name='preview_formato'),  # Vista previa del formato

    # API
    path('api/grupos-por-catequista/', grupos_por_catequista, name='grupos_por_catequista'),  # API de grupos por catequista
    path('api/horarios-por-grupo/', horarios_por_grupo, name='horarios_por_grupo'),  # API de horarios por grupo
]