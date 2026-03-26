from django.urls import path
from .views import (
    menu_catequesis,

    lista_catequistas, crear_catequista, editar_catequista, eliminar_catequista,
    lista_grupos, crear_grupo, editar_grupo, eliminar_grupo,
    lista_horarios, crear_horario, editar_horario, eliminar_horario,

    grupos_por_catequista, horarios_por_grupo,

    lista_formatos,  # Importa la vista de formatos
)

urlpatterns = [
    path('', menu_catequesis, name='menu_catequesis'),

    path('catequistas/', lista_catequistas, name='lista_catequistas'),
    path('catequistas/nuevo/', crear_catequista, name='crear_catequista'),
    path('catequistas/editar/<int:pk>/', editar_catequista, name='editar_catequista'),
    path('catequistas/eliminar/<int:pk>/', eliminar_catequista, name='eliminar_catequista'),

    path('grupos/', lista_grupos, name='lista_grupos'),
    path('grupos/nuevo/', crear_grupo, name='crear_grupo'),
    path('grupos/editar/<int:pk>/', editar_grupo, name='editar_grupo'),
    path('grupos/eliminar/<int:pk>/', eliminar_grupo, name='eliminar_grupo'),

    path('horarios/', lista_horarios, name='lista_horarios'),
    path('horarios/nuevo/', crear_horario, name='crear_horario'),
    path('horarios/editar/<int:pk>/', editar_horario, name='editar_horario'),
    path('horarios/eliminar/<int:pk>/', eliminar_horario, name='eliminar_horario'),

    path('formatos/', lista_formatos, name='lista_formatos'),  # Nueva ruta para formatos

    # API
    path('api/grupos-por-catequista/', grupos_por_catequista, name='grupos_por_catequista'),
    path('api/horarios-por-grupo/', horarios_por_grupo, name='horarios_por_grupo'),
]