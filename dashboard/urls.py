from django.urls import path
from .views import (
    admin_dashboard,
    user_dashboard,
    direccion_dashboard,
    secretaria_dashboard,
    catequesis_dashboard,
    consulta_dashboard,
)

urlpatterns = [
    path('admin/', admin_dashboard, name='admin_dashboard'),
    path('usuario/', user_dashboard, name='user_dashboard'),
    path('direccion/', direccion_dashboard, name='direccion_dashboard'),
    path('secretaria/', secretaria_dashboard, name='secretaria_dashboard'),
    path('catequesis/', catequesis_dashboard, name='catequesis_dashboard'),
    path('consulta/', consulta_dashboard, name='consulta_dashboard'),
]