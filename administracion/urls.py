from django.urls import path  # Permite definir rutas de la app
from .views import dashboard_administracion, detalle_modelo  # Vistas del panel interno


urlpatterns = [
    path('', dashboard_administracion, name='dashboard_administracion'),
    # Ruta principal del módulo de Administración

    path('modelo/<str:app_label>/<str:model_name>/', detalle_modelo, name='detalle_modelo_administracion'),
    # Ruta para explorar registros de un modelo específico
]