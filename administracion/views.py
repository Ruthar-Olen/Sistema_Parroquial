from django.contrib.auth.decorators import login_required, user_passes_test  # Seguridad de acceso
from django.shortcuts import render
from django.http import Http404
from django.contrib import admin  # Permite leer el registro de modelos del admin original


def es_superusuario(user):
    return user.is_superuser
    # Restringe acceso únicamente a superusuarios


@login_required
@user_passes_test(es_superusuario, raise_exception=True)
def dashboard_administracion(request):
    # Construye el inventario de modelos usando exactamente los modelos registrados en /admin
    modelos_admin = []

    for modelo in admin.site._registry.keys():
        total = 0
        # Intenta contar registros; si la tabla no existe en este entorno, deja 0 sin romper la vista
        try:
            total = modelo.objects.count()
        except Exception:
            total = 0

        modelos_admin.append({
            'app_label': modelo._meta.app_label,
            'model_name': modelo._meta.model_name,
            'nombre_modelo': modelo._meta.verbose_name_plural.title(),
            'total': total,
        })

    modelos_admin.sort(key=lambda x: (x['app_label'], x['nombre_modelo']))
    # Ordena por app y nombre para mostrar una navegación clara y consistente

    return render(request, 'administracion/dashboard.html', {
        'modelos_admin': modelos_admin,
    })


@login_required
@user_passes_test(es_superusuario, raise_exception=True)
def detalle_modelo(request, app_label, model_name):
    modelo_objetivo = None

    # Busca el modelo solicitado dentro del mismo registro del admin original
    for modelo in admin.site._registry.keys():
        if modelo._meta.app_label == app_label and modelo._meta.model_name == model_name:
            modelo_objetivo = modelo
            break

    if not modelo_objetivo:
        raise Http404('Modelo no encontrado en la configuración de administración.')
        # Protege el endpoint contra rutas inválidas o modelos no registrados en admin

    queryset = modelo_objetivo.objects.all()
    # Obtiene todos los registros del modelo seleccionado

    if hasattr(modelo_objetivo, 'pk'):
        queryset = queryset.order_by('-pk')
        # Orden descendente por ID para mostrar primero lo más reciente

    registros = queryset[:80]
    # Limita a 80 filas para mantener la pantalla ágil

    return render(request, 'administracion/detalle_modelo.html', {
        'app_label': app_label,
        'model_name': model_name,
        'nombre_modelo': modelo_objetivo._meta.verbose_name_plural.title(),
        'total': queryset.count(),
        'registros': registros,
    })