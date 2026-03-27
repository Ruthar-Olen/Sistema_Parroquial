from django.contrib import admin  # Admin de Django
from django.urls import path, include  # Rutas e includes
from django.conf import settings  # Acceso a la configuración del proyecto
from django.conf.urls.static import static  # Sirve archivos media en desarrollo


urlpatterns = [
    path('admin/', admin.site.urls),  # Ruta del admin
    path('', include('accounts.urls')),  # Rutas de cuentas y login
    path('dashboard/', include('dashboard.urls')),  # Rutas del dashboard
    path('administracion/', include('administracion.urls')),  # Rutas del módulo interno de administración
    path('sacramentos/', include('sacramentos.urls')),  # Rutas del módulo sacramentos
    path('catequesis/', include('catequesis.urls')),  # Rutas del módulo catequesis
    path('oficios/', include('oficios.urls')),  # Rutas del módulo de oficios
    path('inventario/', include('inventario.urls')),  # Rutas del módulo de inventario
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)  # Sirve archivos subidos en desarrollo